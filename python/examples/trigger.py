from time import sleep

import picoquake

if __name__ == "__main__":
    # Create a PicoQuake device
    device = picoquake.PicoQuake("c6e3")

    # Configure acquisition
    device.configure(
        sample_rate=picoquake.SampleRate.hz_100,
        filter_hz=picoquake.Filter.hz_42,
        acc_range=picoquake.AccRange.g_16,
        gyro_range=picoquake.GyroRange.dps_2000,
    )

    # Acquire data from the device
    data, exception = device.trigger(rms_threshold=2,
                                     pre_seconds=2,
                                     post_seconds=5,
                                     source="accel",
                                     axis="xyz",)

    # Stop the device
    device.stop()

    # Check if an exception occurred
    if exception is not None:
        raise exception

    # Print the acquired data
    print(f"Data: {data}")

    # Save to a CSV file
    data.to_csv("acquisition_triggered.csv")