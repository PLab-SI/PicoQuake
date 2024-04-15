from interface import *

if __name__ == '__main__':
    device = PicoQuake("/dev/cu.usbmodem1101")
    device.configure(DataRate.hz_1000, Filter.hz_42, AccRange.g_2, GyroRange.dps_250)

    # device.start_continuos()
    # try:
    #     while True:
    #         sleep(0.1)
    #         print(device.measure())
    # finally:
    #     device.stop()


    try:
        samples = device.measure(n_samples=2000)
        print(len(samples))
    finally:
        device.stop()
