"""
This example demonstrates how to continuously read data from device.
Sample rate is handled by this script and may not be accurate due to system load.
Use this method to acquire data in real-time.
"""

from time import sleep
import logging

import picoquake

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create a PicoQuake device
    device = picoquake.PicoQuake("d4e9")

    # Configure acquisition
    device.configure(
        sample_rate=picoquake.SampleRate.hz_100,
        filter_hz=picoquake.Filter.hz_42,
        acc_range=picoquake.AccRange.g_16,
        gyro_range=picoquake.GyroRange.dps_2000,
    )

    # Alternatively, configure from float values.
    # The closest available values will be used.
    device.configure_approx(
        sample_rate=1000,
        filter_hz=200,
        acc_range=16,
        gyro_range=2000,
    )

    # Start continuous acquisition
    device.start_continuous()

    # Read from device
    try:
        while True:
            sample = device.read_last()
            print(f"Sample: {sample}")
            sleep(1)
    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        device.stop()
    
