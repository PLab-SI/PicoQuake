# PicoQuake

A small and simple vibration analysis tool.

## Specs

- Accelerometer ranges: +-2 g, +-4 g, +-8 g, +-16 g
- Gyro range: up to +-2000 dps
- Sample rate: 12.5 Hz to 4000 Hz
- Configurable low pass (second order) filter: 42 Hz to 3979 Hz
- IMU sensor: ICM-42688-P
- Connectivity: USB 2.0 Full Speed 12Mbps CDC via USB Type-C
- Power requirement: 5 V, 50 mA
- Cable length: 1.8 m
- Dimensions: ⌀30 mm x 13 mm

## Noise performance

PicoQuake can be used to profile vibrations of very low magnitude, due to the low-noise accelerometer used. We evaluated the noise performance of a stationary PicoQuake at room temperature for two configurations:

- Low noise configuration: 500 Hz sample rate, 42 Hz filter, +-2 g range
    - X axis noise: 0.43 *mg RMS*
    - Y axis noise: 0.46 *mg RMS*
    - Z axis noise: 1.17 *mg*
- Full performance configuration: 4 kHz sample rate, 2 kHz filter, +-16 g range
    - X axis noise: 1.88 *mg RMS*
    - Y axis noise: 2.21 *mg RMS*
    - Z axis noise: 2.57 *mg RMS*
