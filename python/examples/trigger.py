"""
This example demonstrates how to trigger an acquisition based on a root mean square (RMS) threshold.
Sample rate is handled by the device and is very accurate.
"""

import logging

import picoquake

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create a PicoQuake device
    device = picoquake.PicoQuake("c6e3")

    # Configure acquisition
    device.configure(
        sample_rate=picoquake.SampleRate.hz_1000,
        filter_hz=picoquake.Filter.hz_213,
        acc_range=picoquake.AccRange.g_16,
        gyro_range=picoquake.GyroRange.dps_2000,
    )

    # Acquire data from the device
    data, exception = device.trigger(rms_threshold=0.5,
                                     pre_seconds=1,
                                     post_seconds=3,
                                     source="accel",
                                     axis="xyz",
                                     rms_window=0.1)

    # Stop the device
    device.stop()

    # Check if an exception occurred
    if exception is not None:
        print(f"Exception: {exception}")

    # Print the acquired data
    print(f"Data: {data}")

    # Save to a CSV file
    data.to_csv("acquisition_triggered.csv")
