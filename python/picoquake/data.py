from dataclasses import dataclass, field
from enum import Enum
from hashlib import blake2b
from datetime import datetime

from .configuration import Config


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
class IMUSample:
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


@dataclass
class AcquisitionResult:
    samples: list[IMUSample]
    device: DeviceInfo
    config: Config
    start_time: datetime
    end_time: datetime
    integrity: bool = field(init=False)
    skipped_samples: int = field(init=False)

    @property
    def duration(self) -> float:
        return self.num_samples / self.config.data_rate.param_value
    
    @property
    def num_samples(self) -> int:
        return len(self.samples)
    
    def check_integrity(self) -> int:
        last_count = self.samples[0].count
        skipped = 0
        for s in self.samples:
            diff = s.count - last_count
            if diff > 1:
                skipped += diff - 1
            last_count = s.count
        return skipped
    
    def normalize_count(self):
        first = self.samples[0].count
        for s in self.samples:
            s.count -= first
    
    def __post_init__(self):
        self.skipped_samples = self.check_integrity()
        self.integrity = self.skipped_samples == 0
        self.normalize_count()

    def __str__(self) -> str:
        return (f"num_samples = {self.num_samples}, " 
                f"duration = {self.duration:.2f}s, "
                f"integrity = {self.integrity}, "
                f"skipped = {self.skipped_samples}")
