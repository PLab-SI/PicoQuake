from enum import Enum
from dataclasses import dataclass

class DataRate(Enum):
    hz_12_5 = 12.5
    hz_25 = 25
    hz_50 = 50
    hz_100 = 100
    hz_200 = 200
    hz_500 = 500
    hz_1000 = 1000
    hz_2000 = 2000
    hz_4000 = 4000
    # hz_8000 = 8000
    # hz_16000 = 16000
    # hz_32000 = 32000

class Filter(Enum):
    hz_42 = 42
    hz_84 = 84
    hz_126 = 126
    hz_170 = 170
    hz_213 = 213
    hz_258 = 258
    hz_303 = 303
    hz_348 = 348
    hz_394 = 394
    hz_441 = 441
    hz_488 = 488
    hz_536 = 536
    hz_585 = 585
    hz_634 = 634
    hz_684 = 684
    hz_734 = 734
    hz_785 = 785
    hz_837 = 837
    hz_890 = 890
    hz_943 = 943
    hz_997 = 997
    hz_1051 = 1051
    hz_1107 = 1107
    hz_1163 = 1163
    hz_1220 = 1220
    hz_1277 = 1277
    hz_1336 = 1336
    hz_1395 = 1395
    hz_1454 = 1454
    hz_1515 = 1515
    hz_1577 = 1577
    hz_1639 = 1639
    hz_1702 = 1702
    hz_1766 = 1766
    hz_1830 = 1830
    hz_1896 = 1896
    hz_1962 = 1962
    hz_2029 = 2029
    hz_2097 = 2097
    hz_2166 = 2166
    hz_2235 = 2235
    hz_2306 = 2306
    hz_2377 = 2377
    hz_2449 = 2449
    hz_2522 = 2522
    hz_2596 = 2596
    hz_2671 = 2671
    hz_2746 = 2746
    hz_2823 = 2823
    hz_2900 = 2900
    hz_2978 = 2978
    hz_3057 = 3057
    hz_3137 = 3137
    hz_3217 = 3217
    hz_3299 = 3299
    hz_3381 = 3381
    hz_3464 = 3464
    hz_3548 = 3548
    hz_3633 = 3633
    hz_3718 = 3718
    hz_3805 = 3805
    hz_3892 = 3892
    hz_3979 = 3979

class AccRange(Enum):
    g_2 = 2
    g_4 = 4
    g_8 = 8
    g_16 = 16

class GyroRange(Enum):
    dps_15_625 = 15.625
    dps_31_25 = 31.25
    dps_62_5 = 62.5
    dps_125 = 125
    dps_250 = 250
    dps_500 = 500
    dps_1000 = 1000
    dps_2000 = 2000

@dataclass
class Config:
    data_rate: DataRate
    filter: Filter
    acc_range: AccRange
    gyro_range: GyroRange
