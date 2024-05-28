"""
This module implements the main interface class for PicoQuake device.
"""

import time
from serial import Serial, SerialException
from serial.tools.list_ports import comports
from queue import Empty, Queue
from time import sleep, time
from threading import Thread, Event
from typing import List, Optional, cast, Tuple
import logging
import struct
from datetime import datetime

from cobs import cobs

from .msg import messages_pb2
from .configuration import *
from .data import *
from .exceptions import *

VID = 0x2E8A
PID = 0xA

_HANDSHAKE_TIMEOUT = 5.0
_STATUS_TIMEOUT = 2.0
_SAMPLE_START_TIMEOUT = 1.0
_READ_LAST_TIMEOUT = 1.0


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
        start_continuos: Starts the device in continuos mode.
        stop_continuos: Stops the device in continuos mode.
        read_last: Reads the last sample received in continuos mode.
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

        self.config: Config = Config(SampleRate.hz_100, Filter.hz_42, AccRange.g_2, GyroRange.dps_250)
        """The current configuration of the device."""

        self._continuos_mode = False
        self._acquire_n_samples = 0
        self._is_sampling = False
        self._sample_list: List[IMUSample] = []
        self._last_sample: Optional[IMUSample] = None

        self._out_packet_queue = Queue()
        self._in_message_queue = Queue()
        self._stop_event = Event()
        
        self._serial_thread = Thread(target=self._serial_worker, daemon=True)
        self._handler_thread = Thread(target=self._handler, daemon=True)

        self._device_status = Status(State.IDLE, 0, 0, 0)
        self._last_status_time = time()

        self._exception: Optional[Exception] = None

        self._started = False
        self._serial_thread.start()
        self._handler_thread.start()
        self._started = True

        self._handshake()
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
        if self._continuos_mode:
            raise RuntimeError("Continuos mode is active, stop it before acquiring")
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
        self._logger.info(f"Acquisition stopped. Took: {stop_t - start_t:.1f}s.")
        self._logger.info(f"Received {len(self._sample_list)} samples")

        data = AcquisitionData(samples=self._sample_list[0:n_samples],
                               device=cast(DeviceInfo, self.device_info),
                               config=self.config,
                               start_time=datetime.fromtimestamp(start_t))

        if exception is None:
            if len(self._sample_list) < n_samples:
                self._logger.warning(f"Expected {n_samples} samples, received {len(self._sample_list)}")
                exception = ConnectionError("Not all samples received")
            elif not data._check_integrity:
                self._logger.warning(f"Data integrity compromised, {data.skipped_samples} samples skipped")
                exception = ConnectionError("Data integrity compromised")
        return data, exception

    def start_continuos(self):
        """
        Starts the device in continuos mode. Samples can be read using `read_last()`.
        """
        self._continuos_mode = True
        self._start_sampling()
        self._logger.info("Continuos mode started")

    def stop_continuos(self):
        """
        Stops the device in continuos mode.
        """
        self._continuos_mode = False
        self._stop_sampling()
        self._last_sample = None
        self._logger.info("Continuos mode stopped")

    def read_last(self) -> IMUSample:
        """
        Reads the last sample received in continuos mode.

        Returns:
            The latest sample performed on device.

        Raises:
            RuntimeError: If continuos mode is not started.
            ConnectionError: If no samples are received.
        """       
        if not self._continuos_mode:
            raise RuntimeError("Continuos mode not started")

        start_time = time()
        while self._last_sample is None:
            if time() - start_time > _READ_LAST_TIMEOUT:
                if self._exception is not None:
                    raise self._exception
                else:
                    raise ConnectionError("No samples received")
            sleep(0.001)
        if self._exception is not None:
            raise self._exception
        return self._last_sample

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

    @_handle_exceptions
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
        self._sample_list = []
        self._last_sample = None
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
        self._continuos_mode = False
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
                    imu_data = msg
                    if self._continuos_mode:
                        self._last_sample = imu_data
                    else:
                        self._sample_list.append(imu_data)
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
                                                  msg.firmware.decode("utf-8"))

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
