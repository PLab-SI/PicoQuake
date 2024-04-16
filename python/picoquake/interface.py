from random import sample
import time
from serial import Serial
from enum import Enum
# from multiprocessing import Process, Queue, Event
from queue import Empty, Full, Queue
from time import sleep, time
from threading import Thread, Event
from typing import List
from google.protobuf.json_format import MessageToDict


from cobs import cobs

import msg.messages_pb2 as messages_pb2
from configuration import *
from data import *

STATUS_TIMEOUT = 2.0

class State(Enum):
    IDLE = 0
    SAMPLING = 1
    ERROR = 2

class CommandID(Enum):
    HANDSHAKE = 0
    START_SAMPLING = 1
    STOP_SAMPLING = 2

class PacketID(Enum):
    IMU_DATA = 1
    STATUS = 2
    DEVICE_INFO = 3
    COMMAND = 4

class PicoQuake:
    def __init__(self, port: str):
        self._port = port

        self.device_info: DeviceInfo | None = None

        self._config = Config(DataRate.hz_100, Filter.hz_42, AccRange.g_2, GyroRange.dps_250)
        self._continuos_mode = False
        self._measure_n_samples = 0
        self._is_sampling = False
        self._sample_list: List[IMUData] = []
        self._last_sample: IMUData | None = None

        self._out_packet_queue = Queue()
        self._in_message_queue = Queue()
        self._stop_event = Event()
        
        self._serial_thread = Thread(target=self._serial_worker)
        self._handler_thread = Thread(target=self._handler)

        self._last_status_time = 0

        self._serial_thread.start()
        self._handler_thread.start()

        self._handshake()
        print(f"Handshake: {self.device_info}")

    def __del__(self):
        self._stop()

    def configure(self, data_rate: DataRate, filter_hz: Filter,
                  acc_range: AccRange, gyro_range: GyroRange):
        self._config = Config(data_rate, filter_hz, acc_range, gyro_range)

    def stop(self):
        self._stop()

    def measure(self, seconds: float = 0, n_samples: int = 0,
                block: bool = True, timeout: float = 0) -> List[IMUData] | IMUData | None:
        if not self._continuos_mode:
            if seconds == 0 and n_samples == 0:
                raise ValueError("Either seconds or n_samples must be specified,"
                                 "or use start_continuos() before measure()")
            if seconds > 0:
                n_samples = int(seconds * self._config.data_rate.param_value)

            self._measure_n_samples = n_samples
            self._start_sampling()
            while self._is_sampling:
                sleep(0.001)
            return self._sample_list[0:n_samples]
        else:
            if block:
                start_time = time()
                while self._last_sample is None:
                    if timeout > 0 and time() - start_time > timeout:
                        break
                    sleep(0.001)
            return self._last_sample

    def start_continuos(self):
        self._continuos_mode = True
        self._start_sampling()
        pass

    def stop_continuos(self):
        self._continuos_mode = False
        self._stop_sampling()
        pass

    def _handshake(self, timeout: float = 1.0):
        self._send_command(CommandID.HANDSHAKE)
        start_time = time()
        while self.device_info is None:
            sleep(0.001)
            if time() - start_time > timeout:
                self._stop()
                raise Exception("Handshake timeout")

    def _start_sampling(self):
        self._sample_list = []
        self._last_sample = None
        self._send_command(CommandID.START_SAMPLING, self._config)
        self._is_sampling = True

    def _stop_sampling(self):
        self._send_command(CommandID.STOP_SAMPLING, self._config) 
        self._is_sampling = False

    def _send_command(self, cmd_id: CommandID, config: Config | None = None):
        msg = messages_pb2.Command()
        msg.id = cmd_id.value
        if config is not None:
            msg.filter_config = config.filter.index
            msg.data_rate = config.data_rate.index
            msg.acc_range = config.acc_range.index
            msg.gyro_range = config.gyro_range.index
        packet = cobs.encode(msg.SerializeToString())
        packet = bytes([0x00]) +  bytes([PacketID.COMMAND.value]) + packet + bytes([0x00])
        self._out_packet_queue.put_nowait(packet)
        print(f"Command sent: {cmd_id}")

    def _stop(self):
        self._stop_sampling()
        self._continuos_mode = False
        self._stop_event.set()
        self._serial_thread.join(timeout=1)
        self._handler_thread.join(timeout=1)

    def _handler(self):
        while not self._stop_event.is_set():
            # process messages
            try:
                msg = self._in_message_queue.get(timeout=0.01)
            except Empty:
                pass
            else:
                if isinstance(msg, messages_pb2.IMUData):
                    imu_data = IMUData(msg.count, msg.acc_x, msg.acc_y, msg.acc_z,
                                       msg.gyro_x, msg.gyro_y, msg.gyro_z)
                    if self._continuos_mode:
                        self._last_sample = imu_data
                    else:
                        self._sample_list.append(imu_data)
                        if len(self._sample_list) >= self._measure_n_samples:
                            self._stop_sampling()
                            # TODO: if sampling doesn't stop it sends command every time
                elif isinstance(msg, messages_pb2.Status):
                    status = Status(msg.state, msg.temperature, msg.missed_samples, msg.error_code)
                    print(status)
                    self._last_status_time = time()
                    if status.error_code == State.ERROR.value:
                        self._stop()
                        raise Exception("Device in error state")
                elif isinstance(msg, messages_pb2.DeviceInfo):
                    self.device_info = DeviceInfo(msg.unique_id, msg.firmware)
                    print("dev info rec")

            # # check device status
            # if time() - self._last_status_time > STATUS_TIMEOUT:
            #     self._stop()
            #     raise Exception("Device not responding")

    def _serial_worker(self):
        ser = Serial(self._port, timeout=0.001)
        data = b''
        in_buffer = b''
        receiving_packet = False
        while not self._stop_event.is_set():
            # receive
            data = ser.read(1)
            if len(data) > 0:
                if data == bytes([0x00]):
                    if receiving_packet:
                        if len(in_buffer) > 0:
                            # stop flag, end of packet
                            self._in_message_queue.put_nowait(self._decode_packet(in_buffer))
                            in_buffer = b''
                            receiving_packet = False
                        else:
                            # empty packet, treat as new start flag
                            pass
                    else:
                        # start flag
                        receiving_packet = True
                elif receiving_packet:
                    in_buffer += data
            
            # send
            try:
                packet = self._out_packet_queue.get_nowait()
                ser.write(packet)
            except Empty:
                pass
        ser.flush()
        ser.close()

    def _decode_packet(self, packet: bytes):
        packet_id = PacketID(packet[0])
        decoded = cobs.decode(packet[1:])
        if packet_id == PacketID.IMU_DATA:
            msg = messages_pb2.IMUData.FromString(decoded)
        elif packet_id == PacketID.STATUS:
            msg = messages_pb2.Status.FromString(decoded)
        elif packet_id == PacketID.DEVICE_INFO:
            msg = messages_pb2.DeviceInfo.FromString(decoded)
        return msg