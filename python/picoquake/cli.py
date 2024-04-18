from typing import List, cast
import csv
import logging
from serial.tools.list_ports import comports

from interface import *

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def measure(port, seconds: float,
            data_rate: float, filter: float,
            acc_range: float, gyro_range: float) -> List[IMUData]:
    device = PicoQuake(port)
    device.configure_approx(data_rate, filter, acc_range, gyro_range)
    out = device.measure(seconds=seconds)
    return cast(List[IMUData], out)

def measure_to_csv(port, seconds: float,
                   data_rate: float, filter: float,
                   acc_range: float, gyro_range: float,
                   csv_file: str):
    samples = measure(port, seconds, data_rate, filter, acc_range, gyro_range)
    # TODO: write samples to csv file
    
if __name__ == '__main__':
    # ports = comports()
    # for p in ports:
    #     print(f"device: {p.device}\n"
    #           f"name: {p.name}\n"
    #           f"description: {p.description}\n"
    #           f"hwid: {p.hwid}\n"
    #           f"vid: {p.vid}, pid: {p.pid}\n"
    #           f"serial_number: {p.serial_number}\n"
    #           f"location: {p.location}\n"
    #           f"manufacturer: {p.manufacturer}\n"
    #           f"product: {p.product}\n" 
    #           f"interface: {p.interface}\n\n")


    device = PicoQuake()
    device.configure(DataRate.hz_2000, Filter.hz_536, AccRange.g_2, GyroRange.dps_250)

    # device.start_continuos()
    # try:
    #     while True:
    #         sleep(2)
    #         print(device.measure())
    # finally:
    #     device.stop()

    sleep(2)
    try:
        samples = device.measure(seconds=5)
        print(f"Num Samples: {len(samples)}")
    finally:
        sleep(2)
        device.stop()

    # sleep(10)
    # device.stop()
