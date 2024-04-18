from dataclasses import dataclass, field
from enum import unique, Enum
from hashlib import blake2b


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


@dataclass
class IMUData:
    count: int
    acc_x: float
    acc_y: float
    acc_z: float
    gyro_x: float
    gyro_y: float
    gyro_z: float

    def __str__(self) -> str:
        return (f"cnt = {self.count}, "
                f"a_x = {self.acc_x:+.2f}, "
                f"a_y = {self.acc_y:+.2f}, "
                f"a_z = {self.acc_z:+.2f}, "
                f"g_x = {self.gyro_x:+.2f}, "
                f"g_y = {self.gyro_y:+.2f}, "
                f"g_z = {self.gyro_z:+.2f}")


@dataclass
class Status:
    state: State
    temperature: float
    missed_samples: int
    error_code: int

    def __str__(self) -> str:
        return (f"state = {self.state.name}, "
                f"temp = {self.temperature:+.2f}, "
                f"missed = {self.missed_samples}, "
                f"error = {self.error_code}")
    

@dataclass
class DeviceInfo:
    unique_id: str
    firmware: str
    short_id: str = field(init=False)

    @staticmethod
    def unique_id_to_short_id(unique_id: str) -> str:
        short = blake2b(unique_id.encode(), digest_size=2).hexdigest().upper()
        assert len(short) == 4
        return short

    def __post_init__(self):
        self.short_id = self.unique_id_to_short_id(self.unique_id)

    def __str__(self) -> str:
        return (f"device_id = {self.unique_id.upper()}, "
                f"short_id = {self.short_id}, "
                f"firmware = {self.firmware}")
