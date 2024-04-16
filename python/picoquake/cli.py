from typing import List, cast
import csv

from interface import *


def measure(port, seconds: float,
            data_rate: float, filter: float,
            acc_range: float, gyro_range: float) -> List[IMUData]:
    device = PicoQuake(port)
    device.configure(DataRate.find_closest(data_rate),
                     Filter.find_closest(filter),
                     AccRange.find_closest(acc_range),
                     GyroRange.find_closest(gyro_range))
    out = device.measure(seconds=seconds)
    return cast(List[IMUData], out)

def measure_to_csv(port, seconds: float,
                   data_rate: float, filter: float,
                   acc_range: float, gyro_range: float,
                   csv_file: str):
    samples = measure(port, seconds, data_rate, filter, acc_range, gyro_range)
    # TODO: write samples to csv file
    
if __name__ == '__main__':
    device = PicoQuake("/dev/cu.usbmodem212101")
    device.configure(DataRate.hz_2000, Filter.hz_536, AccRange.g_2, GyroRange.dps_250)

    # device.start_continuos()
    # try:
    #     while True:
    #         sleep(1)
    #         print(device.measure())
    # finally:
    #     device.stop()

    sleep(5)
    try:
        samples = device.measure(seconds=1)
        print(len(samples))
    finally:
        sleep(5)
        device.stop()

    # sleep(10)
    # device.stop()
