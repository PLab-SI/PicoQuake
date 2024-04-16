from dataclasses import dataclass

@dataclass
class IMUData:
    count: int
    acc_x: float
    acc_y: float
    acc_z: float
    gyro_x: float
    gyro_y: float
    gyro_z: float

    def __repr__(self) -> str:
        return (f"IMUData(cnt = {self.count}, "
                f"a_x = {self.acc_x:+.2f}, "
                f"a_y = {self.acc_y:+.2f}, "
                f"a_z = {self.acc_z:+.2f}, "
                f"g_x = {self.gyro_x:+.2f}, "
                f"g_y = {self.gyro_y:+.2f}, "
                f"g_z = {self.gyro_z:+.2f})")

@dataclass
class Status:
    state: int
    temperature: float
    missed_samples: int
    error_code: int

    def __repr__(self) -> str:
        return (f"Status(state = {self.state}, "
                f"temp = {self.temperature:+.2f}, "
                f"missed = {self.missed_samples}, "
                f"error = {self.error_code})")
    
@dataclass
class DeviceInfo:
    unique_id: bytes
    firmware: bytes

    def __repr__(self) -> str:
        return (f"DeviceInfo(device_id = {self.unique_id.hex(sep=':').upper()}, "
                f"firmware = {self.firmware.decode('utf-8')})")
