from interface import *

if __name__ == '__main__':
    device = PicoQuake("/dev/cu.usbmodem212101")
    device.configure(DataRate.hz_100, Filter.hz_42, AccRange.g_2, GyroRange.dps_250)

    # device.start_continuos()
    # try:
    #     while True:
    #         sleep(0.1)
    #         print(device.measure())
    # finally:
    #     device.stop()


    try:
        samples = device.measure(seconds=1)
        print(len(samples))
    finally:
        device.stop()
