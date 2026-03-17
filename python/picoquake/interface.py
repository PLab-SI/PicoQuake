"""
This module implements the main interface class for PicoQuake device.
"""

import time
from serial import Serial, SerialException
from serial.tools.list_ports import comports
from queue import Empty, Queue
from time import sleep, time
from threading import Thread, Event, Lock
from typing import List, Optional, cast, Tuple, Callable
import logging
import struct
from datetime import datetime
from collections import deque

from cobs import cobs

from .msg import messages_pb2
from .configuration import *
from .data import *
from .exceptions import *
from .analysis import *
from .utils import *

VID = 0x2E8A
PID = 0xA

_HANDSHAKE_TIMEOUT = 5.0
_STATUS_TIMEOUT = 2.0
_SAMPLE_START_TIMEOUT = 1.0

_LEN_DEQUE = 1_000_000


def _handle_exceptions(func):
    """
    Decorator for handling exceptions in class methods.
    Calls `_handle_exceptions` method of the class.
    """
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            self._handle_exceptions(e)
    return wrapper


class PicoQuake:
    """
    PicoQuake interface class
    
    Attributes:
        device_info: The device information.
        config: The current configuration of the device.

    Methods:
        configure: Configures the device with specified parameters.
        configure_approx: Configures the device with approximated parameters.
        stop: Stops the device.
        acquire: Acquires data for a specified duration.
        start_continuous: Starts the device in continuous mode.
        stop_continuous: Stops the device in continuous mode.
        read: Reads the specified number of samples received in continuous mode.
        read_last: Reads the last sample received in continuous mode.
        trigger: Triggers the device to start sampling when the RMS value exceeds the threshold.
        reboot_to_bootsel: Reboots the device to BOOTSEL mode.
    """

    def __init__(self, short_id: Optional[str] = None, port: Optional[str] = None):
        """
        Initializes the device.

        Specify `short_id` written on the device label to find the device automatically.
        Alternatively, specify the `port` to which the device is connected.

        Args:
            short_id: A 4-character string used to identify the device. Written on the device label.
            port: The port to which the device is connected.
        
        Raises:
            ValueError: If neither `short_id` nor `port` are provided, or if `short_id` is not a 4-character string.
            DeviceNotFound: If device with `short_id` is not found.
        """
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.NOTSET)

        if port is not None:
            self._port = port
        elif short_id is not None:
            if not (isinstance(short_id, str) and len(short_id) == 4):
                raise ValueError("Short ID must be a 4-character string")
            self._port = self._find_port(short_id)
            if self._port is None:
                raise DeviceNotFound(f"Device with short ID {short_id} not found")
        else:
            raise ValueError("Either short_id or port must be specified")

        self.device_info: Optional[DeviceInfo] = None
        """The device information."""

        self.config: Config = Config(SampleRate.hz_100, Filter.hz_42, AccRange.g_4, GyroRange.dps_1000)
        """The current configuration of the device."""

        self._continuous_mode = False
        self._acquire_n_samples = 0
        self._is_sampling = False
        self._sample_deque: deque = deque()

        self._out_packet_queue = Queue()
        self._in_message_queue = Queue()
        self._stop_event = Event()
        
        self._serial_thread = Thread(target=self._serial_worker, daemon=True)
        self._handler_thread = Thread(target=self._handler, daemon=True)
        self._lock = Lock()

        self._device_status = Status(State.IDLE, 0, 0, 0)
        self._last_status_time = time()

        self._exception: Optional[Exception] = None

        self._started = False
        self._serial_thread.start()
        self._handler_thread.start()
        self._started = True

        try:
            self._handshake()
        except HandshakeError:
            raise ConnectionError("Could not connect to the device, handshake failed")
        self._logger.info(f"Connected to: {self.device_info}")
        self._last_status_time = time()

    def configure(self, sample_rate: SampleRate, filter_hz: Filter,
                  acc_range: AccRange, gyro_range: GyroRange):
        """
        Configures PicoQuake with acquisition parameters.
        Parameters are selected from enums with available values.
        
        Args:
            sample_rate: The sample rate in Hz.
            filter_hz: The filter frequency in Hz.
            acc_range: The accelerometer range in g.
            gyro_range: The gyroscope range in dps.
        """
        self.config = Config(sample_rate, filter_hz, acc_range, gyro_range)
        self._logger.info(f"Configuration set: {self.config}")

    def configure_approx(self, sample_rate: float, filter_hz: float,
                         acc_range: float, gyro_range: float):
        """
        Configures PicoQuake with acquisition parameters.
        Parameters are approximated to the closest available values.

        Args:
            sample_rate: The sample rate in Hz.
            filter_hz: The filter frequency in Hz.
            acc_range: The accelerometer range in g.
            gyro_range: The gyroscope range in dps.
        """
        self.configure(SampleRate.find_closest(sample_rate),
                       Filter.find_closest(filter_hz),
                       AccRange.find_closest(acc_range),
                       GyroRange.find_closest(gyro_range))
        
    def stop(self):
        """
        Stops the device. Disconnects from the device and stops the acquisition.
        """
        self._stop()
        self._serial_thread.join()
        self._handler_thread.join()

    def acquire(self, seconds: float = 0, n_samples: int = 0) -> Tuple[AcquisitionData, Optional[Exception]]:
        """
        Starts data acquisition of a specified duration.
        Duration can be specified in seconds or number of samples.

        Args:
            seconds: The duration of the acquisition in seconds.
            n_samples: The number of samples to acquire.

        Returns:
            A tuple containing the acquisition data and an exception if any occurred.
        
        Raises:
            ValueError: If both `seconds` and `n_samples` are specified, if neither `seconds` nor `n_samples` are specified,
                        or if `seconds` or `n_samples` are negative.
            ConnectionError: If the acquisition times out or if not all samples are received. Incomplete data is still saved.
        """
        if self._continuous_mode:
            raise RuntimeError("Continuous mode is active, stop it before acquiring")
        if seconds != 0 and n_samples != 0:
            raise ValueError("Either seconds or n_samples must be specified, not both")
        if seconds == 0 and n_samples == 0:
            raise ValueError("Either seconds or n_samples must be specified")
        if seconds < 0 or n_samples < 0:
            raise ValueError("Seconds and n_samples must be positive")
        if seconds > 0:
            n_samples = int(seconds * self.config.sample_rate.param_value)

        max_duration = n_samples / self.config.sample_rate.param_value * 1.2 + 1.0
        exception: Optional[Exception] = None

        self._logger.info(f"Acquiring {n_samples} samples, max expected duration: {max_duration:.1f}s")
        self._sample_deque = deque(maxlen=n_samples * 2)
        self._acquire_n_samples = n_samples
        self._start_sampling(n_samples)
        # wait for sampling to start
        cmd_start_t = time()
        while True:
            if self._device_status.state == State.SAMPLING:
                break
            if time() - cmd_start_t > _SAMPLE_START_TIMEOUT:
                raise ConnectionError("Sampling not started in time")
            sleep(0.001)
        start_t = time()
        # wait for sampling to finish
        while True:
            if self._exception is not None:
                exception = self._exception
                break
            if self._device_status.state == State.IDLE:
                break
            if time() - start_t > max_duration:
                exception = ConnectionError("Sampling timeout")
                break
            sleep(0.001)
        stop_t = time()
        samples = list(self._sample_deque)
        self._logger.info(f"Acquisition stopped. Took: {stop_t - start_t:.1f}s.")
        self._logger.info(f"Received {len(samples)} samples")

        data = AcquisitionData(samples=samples[0:n_samples],
                               device=cast(DeviceInfo, self.device_info),
                               config=self.config,
                               start_time=datetime.fromtimestamp(start_t))
        data.re_centre(0)

        if exception is None:
            if len(samples) < n_samples:
                self._logger.warning(f"Expected {n_samples} samples, received {len(samples)}")
                exception = AcquisitionIncomplete("Not all samples received")
            elif not data._check_integrity:
                self._logger.warning(f"Data corrupted, {data.skipped_samples} samples skipped")
                exception = AcquisitionDataCorrupted("Data corrupted")
        return data, exception

    def start_continuous(self):
        """
        Starts the device in continuous mode. Samples can be read using `read_last()`.
        """
        self._continuous_mode = True
        self._sample_deque = deque(maxlen=_LEN_DEQUE)
        self._start_sampling()
        self._logger.info("Continuous mode started")

    def stop_continuous(self):
        """
        Stops the device in continuous mode.
        """
        self._continuous_mode = False
        self._stop_sampling()
        self._logger.info("Continuous mode stopped")

    def read(self, num: int=1, timeout: Optional[float]=None) -> List[IMUSample]:
        """
        Reads the specified number of samples received in continuous mode.
        Samples are returned in the same order as they were received.
        If timeout is None, blocks until the specified number of samples are received.

        Args:
            num: The number of samples to read.
            timeout: The maximum time to wait for the samples.
        
        Returns:
            List of samples. Might be less than `num` if timeout is set.

        Raises:
            RuntimeError: If continuous mode is not started.
        """
        if not self._continuous_mode:
            raise RuntimeError("Continuous mode not started")
        start_time = time()
        while len(self._sample_deque) < num:
            if timeout is not None:
                if time() - start_time > timeout:
                    break
            if self._exception is not None:
                raise self._exception
            sleep(0.001)
        samples = []
        with self._lock:
            num_ret = min(num, len(self._sample_deque))
            for _ in range(num_ret):
                samples.append(self._sample_deque.popleft())
        return samples
    
    def trigger(self, rms_threshold: float, pre_seconds: float, post_seconds:
                float, source: str="accel", axis: str="xyz",
                rms_window: float=1.0,
                on_trigger: Optional[Callable[[float], None]]=None) -> Tuple[AcquisitionData, Optional[Exception]]:
        """
        Triggers the device to start sampling when the RMS value exceeds the threshold.

        Args:
            rms_threshold: The RMS threshold in g.
            pre_seconds: The duration before the trigger in seconds.
            post_seconds: The duration after the trigger in seconds.
            source: The source of the RMS value, either "accel" or "gyro".
            axis: The axis or combination of axes to calculate the RMS value.
            rms_window: The window length in seconds to calculate the RMS value.
            on_trigger: A callback function to call when the trigger is activated.
                The RMS value is passed as an argument.

        Returns:
            A tuple containing the acquisition data and an exception if any occurred.
        """
        if rms_threshold <= 0:
            raise ValueError("RMS threshold must be greater than 0")
        if source not in ["accel", "gyro"]:
            raise ValueError("Source must be 'accel' or 'gyro'")
        combinations = get_axis_combinations("xyz")
        if axis not in combinations:
            raise ValueError("Invalid axis, must be 'x', 'y', 'z', or a combination.")

        window_len = int(rms_window * self.config.sample_rate.param_value)
        n_pre_samples = int(pre_seconds * self.config.sample_rate.param_value)
        n_post_samples = int(post_seconds * self.config.sample_rate.param_value)
        n_samples = n_pre_samples + n_post_samples
        last_sample_count = 0
        sample_count_at_trigger = 0
        trigger_time = 0
        exception: Optional[Exception] = None

        self.start_continuous()
        self._logger.info(f"Triggering on RMS value {rms_threshold} g")
        self._logger.info(f"deque maxlen: {_LEN_DEQUE}")

        # wait for sampling to start
        start_time = time()
        while True:
            if len(self._sample_deque) > 0:
                break
            if time() - start_time > _SAMPLE_START_TIMEOUT:
                self._logger.error("Sampling not started in time")
                self.stop_continuous()
                raise ConnectionError("Sampling not started in time")
        # wait for trigger
        while True:
            sample_count = self._sample_deque[-1].count
            if sample_count - last_sample_count < window_len:
                if self._exception is not None:
                    raise self._exception
                sleep(0.001)
                continue
            samples = deque_get_last_n(self._sample_deque, window_len)
            rms_acc, rms_gyro = imu_rms(samples, axis, de_trend=True)
            if source == "accel":
                rms_val = rms_acc
            else:
                rms_val = rms_gyro
            if rms_val > rms_threshold:
                sample_count_at_trigger = self._sample_deque[-1].count
                trigger_time = time()
                break
            last_sample_count = sample_count
        # trigger activated, acquire data
        self._logger.info(f"Triggered on RMS value {rms_val:.3f} g")
        if on_trigger is not None:
            on_trigger(rms_val)
        while True:
            sample_count = self._sample_deque[-1].count
            if sample_count - sample_count_at_trigger > n_post_samples:
                break
            if self._exception is not None:
                exception = self._exception
                break
            sleep(0.001)
        stop_t = time()
        self.stop_continuous()
        # find idx by comparing count
        for i in range(len(self._sample_deque)):
            if self._sample_deque[i].count == sample_count_at_trigger - n_pre_samples:
                start_idx = i
                break
        else:
            start_idx = 0
        for i in range(len(self._sample_deque)):
            if self._sample_deque[i].count == sample_count_at_trigger + n_post_samples:
                stop_idx = i
                break
        else:
            stop_idx = len(self._sample_deque)
        samples = deque_slice(self._sample_deque,
                              start_idx,
                              stop_idx)
        data = AcquisitionData(samples=samples,
                               device=cast(DeviceInfo, self.device_info),
                               config=self.config,
                               start_time=datetime.fromtimestamp(trigger_time))
        self._logger.info(f"Acquisition stopped. Took: {stop_t - trigger_time:.1f}s.")
        self._logger.info(f"Received {len(samples)} samples")
        data.re_centre(data.num_samples - n_post_samples)
        if exception is None:
            if sample_count_at_trigger < n_pre_samples:
                self._logger.warning(f"Triggered too early, {n_pre_samples - sample_count_at_trigger} samples skipped")
                exception = AcquisitionIncomplete("Triggered too early")
            elif len(samples) < n_samples:
                self._logger.warning(f"Expected {n_samples} samples, received {len(samples)}")
                exception = AcquisitionIncomplete("Not all samples received")
            elif not data._check_integrity:
                self._logger.warning(f"Data corrupted, {data.skipped_samples} samples skipped")
                exception = AcquisitionDataCorrupted("Data corrupted")
        return data, exception
        

    def read_last(self, timeout: Optional[float]=None) -> Optional[IMUSample]:
        """
        Reads the last sample received in continuous mode.
        If timeout is None, blocks until a sample is received.

        Args:
            timeout: The maximum time to wait for the sample.

        Returns:
            The latest sample received.

        Raises:
            RuntimeError: If continuous mode is not started.
        """       
        if not self._continuous_mode:
            raise RuntimeError("Continuous mode not started")

        start_time = time()
        while len(self._sample_deque) < 1:
            if timeout is not None:
                if time() - start_time > timeout:
                    break
            if self._exception is not None:
                raise self._exception
            sleep(0.001)
        with self._lock:
            if len(self._sample_deque) > 0:
                return self._sample_deque.pop()
            else:
                return None
    
    def reboot_to_bootsel(self):
        """
        Reboots the device to BOOTSEL mode.
        """
        if self._started:
            self.stop()
        self._logger.info("Rebooting to BOOTSEL...")
        ser = Serial(self._port, 1200, timeout=0.1)
        sleep(0.1)
        ser.close()

    def _find_port(self, short_id: str) -> Optional[str]:
        """
        Finds the port to which the device is connected.
        """
        ports = comports()
        for p in ports:
            self._logger.debug(f"Found port: {p.device}, pid: {p.pid}, vid: {p.vid}, sn: {p.serial_number}")
            if p.vid == VID and p.pid == PID and p.serial_number:
                if DeviceInfo.unique_id_to_short_id(p.serial_number) == short_id.upper():
                    return p.device
        return None

    def _handshake(self, timeout: float = _HANDSHAKE_TIMEOUT):
        """
        Performs the handshake with the device.
        """
        self._send_command(CommandID.HANDSHAKE)
        start_time = time()
        while self.device_info is None:
            sleep(0.001)
            if time() - start_time > timeout:
                self._stop()
                raise HandshakeError("Handshake timeout")

    def _start_sampling(self, num_samples: int = 0):
        """
        Sends start sampling command.

        Args:
            num_samples: The number of samples to acquire.
                If 0, the device will sample continuously.
        """
        self._logger.debug("Starting sampling...")
        self._send_command(CommandID.START_SAMPLING, self.config, num_samples)
        self._is_sampling = True

    def _stop_sampling(self):
        """
        Sends stop sampling command.
        """
        self._logger.debug("Stopping sampling...")
        self._send_command(CommandID.STOP_SAMPLING) 
        self._is_sampling = False

    def _send_command(self, cmd_id: CommandID, config: Optional[Config] = None,
                      num_samples: int = 0):
        """
        Sends a command to the device.

        Args:
            cmd_id: The command ID.
            config: The configuration to send with the command.
            num_samples: The number of samples to acquire.
        """
        msg = messages_pb2.Command()
        msg.id = cmd_id.value
        if config is not None:
            msg.filter_config = config.filter.index
            msg.data_rate = config.sample_rate.index
            msg.acc_range = config.acc_range.index
            msg.gyro_range = config.gyro_range.index
            msg.num_to_sample = num_samples
        packet = cobs.encode(msg.SerializeToString())
        packet = bytes([0x00]) + bytes([PacketID.COMMAND.value]) + packet + bytes([0x00])
        self._out_packet_queue.put_nowait(packet)
        self._logger.debug(f"Command sent: {cmd_id.name}")

    def _stop(self):
        """
        Sends stop command to the device.
        Sends stop event to handler threads.
        """
        if not self._started:
            return
        if self._is_sampling:
            self._stop_sampling()
        self._continuous_mode = False
        self._stop_event.set()
        self._logger.info("Device stopped")

    @_handle_exceptions
    def _handler(self):
        """
        Main handler thread for processing messages.
        """
        while not self._stop_event.is_set():
            # process messages
            try:
                msg = self._in_message_queue.get(timeout=0.1)
            except Empty:
                pass
            else:
                if isinstance(msg, IMUSample):
                    self._sample_deque.append(msg)
                elif isinstance(msg, messages_pb2.Status):
                    status = Status(State(msg.state), msg.temperature,
                                    msg.missed_samples, msg.error_code)
                    if status.state != self._device_status.state:
                        self._logger.debug(f"Device state changed from {self._device_status.state.name} to {status.state.name}")
                    self._device_status = status
                    self._last_status_time = time()
                    if status.state == State.ERROR.value:
                        raise DeviceError(status.error_code)
                elif isinstance(msg, messages_pb2.DeviceInfo):
                    self.device_info = DeviceInfo(msg.unique_id.hex().upper(),
                                                  msg.firmware.replace(b'\x00', b'').decode("utf-8"))

            # check device status
            if self.device_info is not None:
                if time() - self._last_status_time > _STATUS_TIMEOUT:
                    self._serial_thread.join(timeout=1.0)
                    self._logger.debug("Handler stopped")
                    raise ConnectionError("Connection lost, device not responding")
        self._serial_thread.join(timeout=1.0)
        self._logger.debug("Handler stopped")

    @_handle_exceptions
    def _serial_worker(self):
        """
        Main serial worker thread receiving and sending serial data.
        Packet decode errors are logged and ignored.

        Raises:
            ConnectionError: If cannot connect to the device or if the connection is lost.
        """
        self._logger.debug(f"Connecting on port {self._port} ...")
        try:
            ser = Serial(self._port, timeout=0.1)
            ser.reset_input_buffer()
            ser.reset_output_buffer()
        except SerialException:
            raise ConnectionError(f"Could not connect to port {self._port}")
        except PermissionError:
            raise ConnectionError(f"Permission denied on port {self._port}. Check user permissions.")
        in_buffer = bytearray()
        receiving_packet = False
        try:
            while not self._stop_event.is_set():
                # receive
                try:
                    data = ser.read(1000)
                except SerialException as e:
                    raise ConnectionError("Connection lost, port closed")
                if len(data) > 0:
                    for b in data:
                        if b == 0x00:
                            if receiving_packet:
                                if len(in_buffer) > 0:
                                    # stop flag, end of packet
                                    try:
                                        self._in_message_queue.put_nowait(self._decode_packet(in_buffer))
                                    except Exception as e:
                                        self._logger.error(f"Decode error: {e}")
                                    in_buffer.clear()
                                    receiving_packet = False
                                else:
                                    # empty packet, treat as new start flag
                                    pass
                            else:
                                # start flag
                                receiving_packet = True
                        elif receiving_packet:
                            in_buffer.append(b)
                
                # send
                try:
                    packet = self._out_packet_queue.get_nowait()
                    ser.write(packet)
                except Empty:
                    pass

        except:
            ser.close()
            self._logger.debug("Serial worker stopped")
            raise
        ser.close()
        self._logger.debug("Serial worker stopped")

    def _decode_packet(self, packet: bytes):
        """
        Decodes the packet received from the device.
        """
        packet_id = PacketID(packet[0])
        decoded = cobs.decode(packet[1:])
        if packet_id == PacketID.IMU_DATA:
            unpacked_data = struct.unpack('<Qffffff', decoded)
            msg = IMUSample(unpacked_data[0],
                            unpacked_data[1],
                            unpacked_data[2],
                            unpacked_data[3],
                            unpacked_data[4],
                            unpacked_data[5],
                            unpacked_data[6])
        elif packet_id == PacketID.STATUS:
            msg = messages_pb2.Status.FromString(decoded)
        elif packet_id == PacketID.DEVICE_INFO:
            msg = messages_pb2.DeviceInfo.FromString(decoded)
        return msg

    def _handle_exceptions(self, e: Exception):
        """
        Handles exceptions raised in class methods.
        """
        if self._exception is not None:
            return
        self._exception = e
        self._logger.exception(f"Exception: {e}")
