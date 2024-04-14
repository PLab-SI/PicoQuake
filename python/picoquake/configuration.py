from enum import Enum
from dataclasses import dataclass

class DataRate(Enum):
    hz_12_5 = 0
    hz_25 = 1
    hz_50 = 2
    hz_100 = 3
    hz_200 = 4
    hz_500 = 5
    hz_1000 = 6
    hz_2000 = 7
    hz_4000 = 8
    # hz_8000 = 9
    # hz_16000 = 10
    # hz_32000 = 11

class Filter(Enum):
    hz_42 = 0
    hz_84 = 1
    hz_126 = 2
    hz_170 = 3
    hz_213 = 4
    hz_258 = 5
    hz_303 = 6
    hz_348 = 7
    hz_394 = 8
    hz_441 = 9
    hz_488 = 10
    hz_536 = 11
    hz_585 = 12
    hz_634 = 13
    hz_684 = 14
    hz_734 = 15
    hz_785 = 16
    hz_837 = 17
    hz_890 = 18
    hz_943 = 19
    hz_997 = 20
    hz_1051 = 21
    hz_1107 = 22
    hz_1163 = 23
    hz_1220 = 24
    hz_1277 = 25
    hz_1336 = 26
    hz_1395 = 27
    hz_1454 = 28
    hz_1515 = 29
    hz_1577 = 30
    hz_1639 = 31
    hz_1702 = 32
    hz_1766 = 33
    hz_1830 = 34
    hz_1896 = 35
    hz_1962 = 36
    hz_2029 = 37
    hz_2097 = 38
    hz_2166 = 39
    hz_2235 = 40
    hz_2306 = 41
    hz_2377 = 42
    hz_2449 = 43
    hz_2522 = 44
    hz_2596 = 45
    hz_2671 = 46
    hz_2746 = 47
    hz_2823 = 48
    hz_2900 = 49
    hz_2978 = 50
    hz_3057 = 51
    hz_3137 = 52
    hz_3217 = 53
    hz_3299 = 54
    hz_3381 = 55
    hz_3464 = 56
    hz_3548 = 57
    hz_3633 = 58
    hz_3718 = 59
    hz_3805 = 60
    hz_3892 = 61
    hz_3979 = 62

class AccRange(Enum):
    g_2 = 0
    g_4 = 1
    g_8 = 2
    g_16 = 3

class GyroRange(Enum):
    dps_15_625 = 0
    dps_31_25 = 1
    dps_62_5 = 2
    dps_125 = 3
    dps_250 = 4
    dps_500 = 5
    dps_1000 = 6
    dps_2000 = 7

@dataclass
class Config:
    data_rate: DataRate
    filter: Filter
    acc_range: AccRange
    gyro_range: GyroRange
