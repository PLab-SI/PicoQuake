"""
This example demonstrates how to acquire a sample of a specified duration.
Sample rate is handled by the device and is very accurate.
Use this method to acquire high quality data for further analysis.
"""

import logging

import picoquake

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create a PicoQuake device
    device = picoquake.PicoQuake("d4e9")

    # Configure acquisition
    device.configure(
        sample_rate=picoquake.SampleRate.hz_1000,
        filter_hz=picoquake.Filter.hz_213,
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

    # Acquire data from the device
    data, exception = device.acquire(seconds=1)

    # Stop the device
    device.stop()

    # Check if an exception occurred
    if exception is not None:
        raise exception

    # Print the acquired data
    print(f"Data: {data}")

    # Save to a CSV file
    data.to_csv("acquisition.csv")
