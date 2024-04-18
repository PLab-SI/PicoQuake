from calendar import c
from enum import Enum
from dataclasses import dataclass
from typing import TypeVar, Type

T = TypeVar('T', bound='ConfigEnum')

class ConfigEnum(Enum):

    def __new__(cls, *args):
        if not len(args) == 2:
            raise ValueError(f"Member must have 2 elements: {args}")
        if not isinstance(args[0], int):
            raise ValueError(f"First element must be an integer: {args}")
        if not isinstance(args[1], (int, float)):
            raise ValueError(f"Second element must be an integer or float {args}")
        obj = object.__new__(cls)
        obj._value_ = args
        return obj

    @classmethod
    def from_index(cls: Type[T], index: int) -> T:
        for member in cls:
            if member.value[0] == index:
                return member
        raise ValueError(f"Invalid index: {index}")

    @classmethod
    def from_param_value(cls: Type[T], value: float | int, tolerance: float = 1e-5) -> T:
        for member in cls:
            if isinstance(value, float):
                if abs(member.value[1] - value) < tolerance:
                    return member
            elif isinstance(value, int):
                if member.value[1] == value:
                    return member
        raise ValueError(f"Invalid value: {value}")
    
    @classmethod
    def find_closest(cls: Type[T], value: float | int) -> T:
        if not list(cls):
                raise ValueError("No members in the enum")
        closest = next(iter(cls))
        closest_diff = float('inf')
        for member in cls:
            diff = abs(member.value[1] - value)
            if diff < closest_diff:
                closest = member
                closest_diff = diff
        return closest
    
    @property
    def index(self) -> int:
        return self.value[0]
    
    @property
    def param_value(self) ->  float | int:
        return self.value[1]


class DataRate(ConfigEnum):
    hz_12_5 = 1, 2
    hz_25 = 1, 25.0
    hz_50 = 2, 50.0
    hz_100 = 3, 100.0
    hz_200 = 4, 200.0
    hz_500 = 5, 500.0
    hz_1000 = 6, 1000.0
    hz_2000 = 7, 2000.0
    hz_4000 = 8, 4000.0
    # hz_8000 = (9, 8000.0)
    # hz_16000 = (10, 16000.0)
    # hz_32000 = (11, 32000.0)


class Filter(ConfigEnum):
    hz_42 = 0, 42
    hz_84 = 1, 84
    hz_126 = 2, 126
    hz_170 = 3, 170
    hz_213 = 4, 213
    hz_258 = 5, 258
    hz_303 = 6, 303
    hz_348 = 7, 348
    hz_394 = 8, 394
    hz_441 = 9, 441
    hz_488 = 10, 488
    hz_536 = 11, 536
    hz_585 = 12, 585
    hz_634 = 13, 634
    hz_684 = 14, 684
    hz_734 = 15, 734
    hz_785 = 16, 785
    hz_837 = 17, 837
    hz_890 = 18, 890
    hz_943 = 19, 943
    hz_997 = 20, 997
    hz_1051 = 21, 1051
    hz_1107 = 22, 1107
    hz_1163 = 23, 1163
    hz_1220 = 24, 1220
    hz_1277 = 25, 1277
    hz_1336 = 26, 1336
    hz_1395 = 27, 1395
    hz_1454 = 28, 1454
    hz_1515 = 29, 1515
    hz_1577 = 30, 1577
    hz_1639 = 31, 1639
    hz_1702 = 32, 1702
    hz_1766 = 33, 1766
    hz_1830 = 34, 1830
    hz_1896 = 35, 1896
    hz_1962 = 36, 1962
    hz_2029 = 37, 2029
    hz_2097 = 38, 2097
    hz_2166 = 39, 2166
    hz_2235 = 40, 2235
    hz_2306 = 41, 2306
    hz_2377 = 42, 2377
    hz_2449 = 43, 2449
    hz_2522 = 44, 2522
    hz_2596 = 45, 2596
    hz_2671 = 46, 2671
    hz_2746 = 47, 2746
    hz_2823 = 48, 2823
    hz_2900 = 49, 2900
    hz_2978 = 50, 2978
    hz_3057 = 51, 3057
    hz_3137 = 52, 3137
    hz_3217 = 53, 3217
    hz_3299 = 54, 3299
    hz_3381 = 55, 3381
    hz_3464 = 56, 3464
    hz_3548 = 57, 3548
    hz_3633 = 58, 3633
    hz_3718 = 59, 3718
    hz_3805 = 60, 3805
    hz_3892 = 61, 3892
    hz_3979 = 62, 3979


class AccRange(ConfigEnum):
    g_2 = 0, 2
    g_4 = 1, 4
    g_8 = 2, 8
    g_16 = 3, 16


class GyroRange(ConfigEnum):
    dps_15_625 = 0, 15.625
    dps_31_25 = 1, 31.25
    dps_62_5 = 2, 62.5
    dps_125 = 3, 125.0
    dps_250 = 4, 250.0
    dps_500 = 5, 500.0
    dps_1000 = 6, 1000.0
    dps_2000 = 7, 2000.0


@dataclass
class Config:
    data_rate: DataRate
    filter: Filter
    acc_range: AccRange
    gyro_range: GyroRange

    def __str__(self):
        return f"data_rate = {self.data_rate.param_value}, filter = {self.filter.param_value}, " \
               f"acc_range = {self.acc_range.param_value}, gyro_range = {self.gyro_range.param_value}"
