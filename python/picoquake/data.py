from dataclasses import dataclass, field
from enum import Enum
from hashlib import blake2b
from datetime import datetime
import csv
from typing import Optional
import os

from .configuration import *


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

    @staticmethod
    def unique_id_to_short_id(unique_id: str) -> str:
        short = blake2b(unique_id.encode(), digest_size=2).hexdigest().upper()
        assert len(short) == 4
        return short
    
    @property
    def short_id(self) -> str:
        return self.unique_id_to_short_id(self.unique_id)

    def __str__(self) -> str:
        return (f"device_id = {self.unique_id.upper()}, "
                f"short_id = {self.short_id}, "
                f"firmware = {self.firmware}")


@dataclass
class AcquisitionData:
    samples: list[IMUSample]
    device: DeviceInfo
    config: Config
    start_time: datetime
    skipped_samples: int = field(init=False)
    csv_path: Optional[str] = None

    @property
    def duration(self) -> float:
        return self.num_samples / self.config.sample_rate.param_value
    
    @property
    def num_samples(self) -> int:
        return len(self.samples)
    
    @property
    def integrity(self) -> bool:
        return self.skipped_samples == 0
    
    @property
    def filename(self) -> Optional[str]:
        if self.csv_path is None:
            return None
        else:
            return os.path.basename(self.csv_path)
    
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
        self.normalize_count()

    def __str__(self) -> str:
        return (f"device = {self.device.short_id}, "
                f"start_time = {self.start_time.isoformat(sep=' ')}, "
                f"num_samples = {self.num_samples}, " 
                f"duration = {self.duration:.2f}s, "
                f"skipped = {self.skipped_samples}")
    
    def to_csv(self, filename: str):
        metadata = f"# PLab PicoQuake Data\n" \
               f"# Time: {self.start_time.isoformat(sep=' ')}, Device: {self.device.short_id.upper()} ({self.device.unique_id})\n" \
               f"# Num. samples: {self.num_samples}, Duration: {self.duration} s\n" \
               f"# Config: {self.config}\n" \
               f"# Integrity: {self.integrity}, Skipped samples: {self.skipped_samples}\n"
        with open(filename, "w") as f:
            f.write(metadata)
            writer = csv.writer(f)
            writer.writerow(["count", "a_x", "a_y", "a_z", "g_x", "g_y", "g_z"])
            for sample in self.samples:
                writer.writerow([sample.count, sample.acc_x, sample.acc_y, sample.acc_z,
                                sample.gyro_x, sample.gyro_y, sample.gyro_z])

    @classmethod
    def from_csv(cls, path: str) -> 'AcquisitionData':
        with open(path, "r") as f:
            reader = csv.reader(f)
            metadata = []
            try:
                for _ in range(5):
                    metadata.append(next(reader))
                start_time = datetime.fromisoformat(metadata[1][0].split(": ")[1])

                unique_id = metadata[1][1].split(": ")[1].split(" ")[1][1:-1]
                try:
                    firmware = metadata[1][2].split(": ")[1]
                except IndexError:
                    firmware = "unknown"
                device = DeviceInfo(unique_id, firmware)

                sample_rate = float(metadata[3][0].split(" = ")[1].split(" ")[0])
                filter = float(metadata[3][1].split(" = ")[1].split(" ")[0])
                acc_range = float(metadata[3][2].split(" = ")[1].split(" ")[0])
                gyro_range = float(metadata[3][3].split(" = ")[1].split(" ")[0])
                config = Config(SampleRate.from_param_value(sample_rate),
                                Filter.from_param_value(filter),
                                AccRange.from_param_value(acc_range),
                                GyroRange.from_param_value(gyro_range))
            except Exception as e:
                raise ValueError(f"Error parsing metadata: {e}")
            next(reader)

            samples = []
            try:
                for row in reader:
                    count, a_x, a_y, a_z, g_x, g_y, g_z = map(float, row)
                    samples.append(IMUSample(int(count), a_x, a_y, a_z, g_x, g_y, g_z))
            except Exception as e:
                raise ValueError(f"Error parsing samples: {e}")
            
            return cls(samples=samples,
                       device=device,
                       config=config,
                       start_time=start_time,
                       csv_path=path)
