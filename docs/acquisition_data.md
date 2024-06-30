# Acquisition CSV File

The CSV file contains IMU sample data from an acquisition session, along with relevant metadata about the *PicoQuake* device, acquisition configuration, and session details.

## Metadata

The first few lines of the CSV file contain metadata about the acquisition session:

``` plaintext
# PLab PicoQuake Data
# Time: 2024-04-21 15:54:46.333682, Device: D4E9 (E6632891E36F2029)
# Num. samples: 10000, Duration: 5.0 s
# Config: data_rate = 2000.0 Hz, filter = 488 Hz, acc_range = 4 g, gyro_range = 250.0 dps
# Integrity: True, Skipped samples: 0
```

- `Time`: Acquisition start time (local timezone in ISO 8601 format).
- `Device`: Device information, including the device short ID and unique ID.
- `Num. samples`: Number of samples collected during the acquisition session.
- `Duration`: Duration of the acquisition session (in seconds).
- `Config`: Acquisition configuration details, including data rate, filter frequency, accelerometer range, and gyroscope range.
- `Integrity`: Integrity status of the acquisition (whether there are skipped samples).
- `Skipped samples`: Number of skipped samples (if any) during the acquisition session.

## Data Columns

After the metadata, the CSV file contains the actual IMU sample data organized into columns. The columns are:

1. `count`: Sample count, representing the sequential number of each sample.
2. `a_x`: Acceleration in the X-axis (in g).
3. `a_y`: Acceleration in the Y-axis (in g).
4. `a_z`: Acceleration in the Z-axis (in g).
5. `g_x`: Gyro data in the X-axis (in degrees per second).
6. `g_y`: Gyro data in the Y-axis (in degrees per second).
7. `g_z`: Gyro data in the Z-axis (in degrees per second).

!!! note ""
    1 g = 9.81 m/s²

## Example Data

| count | a_x    | a_y   | a_z   | g_x    | g_y    | g_z   |
|-------|--------|-------|-------|--------|--------|-------|
| 1     | 0.96   | 0.41  | 0.53  | 19.71  | 123.73 | 93.19 |
| 2     | 0.72   | 0.51  | 0.53  | 14.60  | 105.12 | 77.13 |
| 3     | 0.77   | 0.51  | 0.37  | 19.36  | 199.39 | 145.63|
| 4     | 0.11   | 0.84  | 0.34  | 246.19 | 245.97 | 77.86 |
| 5     | 0.07   | 0.96  | -0.12 | 126.98 | 249.99 | 57.25 |
