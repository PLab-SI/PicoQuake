# Usage

## Mounting

Mount *PicoQuake* to the object you want to measure as rigidly as possible.
You can use the included releasable zip tie and zip tie adapter.

For more demanding applications, it's recommended to design a custom 3D printed mount.

Using double sided tape is fine, but it might dampen higher frequency vibrations.

!!! tip "Axes orientation"
    Orientation of the axes is marked on the device. Make note of is so you can later interpret the data correctly.

!!! note "Small objects"
    Measuring vibrations of small objects, that are not much larger than the *PicoQuake* itself, can be challenging. The vibrations of the object will be dampened by the device itself.


## Connection

Connect *PicoQuake* to your computer's USB port. Multiple devices can be connected at the same time.

!!! info "Short ID"
    Each *PicoQuake* has a 4 character ID that is used to identify it. It's printed on the label. All commands that require device identification use this ID.

## Commands

*PicoQuake* is controlled using the command line interface (CLI).

For detailed information on all the available commands run `picoquake --help` or browse the [CLI reference](cli.md).

It's also possible to interface the device using the Python API. For more information, see the [Python API reference](python_api/interface.md).

## List connected devices

List all connected *PicoQuake* devices with their Short ID and serial port.

```bash
picoquake list
```

## Live display

Display live data from a *PicoQuake* device. Useful for quick checks and debugging.

```bash
picoquake display <short_id>
```

##  Data acquisition

Acquire data from a *PicoQuake* device. The data is saved to a CSV file.

```bash
picoquake acquire <short_id> <output_file> [options]
```

### Examples

Acquire data for 10 seconds at 100 Hz sample rate. Filter set to 42 Hz. Save it to `data.csv`.

```bash
picoquake acquire D4E9 data.csv -s 10 -r 100 -f 42
```

Acquire data for 2 seconds at 4000 Hz sample rate. Filter set to 1000 Hz.
Accelerometer range set to +-16 g, gyro range set to +-2000 dps. Save it to `data.csv`.

```bash
picoquake acquire D4E9 data.csv -s 2 -r 4000 -f 1000 -ar 16 -gr 2000
```

!!! warning
    Specified sampling rate, filter frequency, accelerometer range, and gyro range are not guaranteed. The actual values may differ due to hardware limitations and are rounded to the nearest supported value. The actual values are printed in the console output.

!!! info "Start prompt"
    After pressing enter, you will be prompted to start the acquisition. This is done to be able to better control the start time. To skip the prompt, add the `-a` flag.

!!! info "Overwrite prompt"
    If the CSV file already exists, you will be prompted to overwrite it. To skip the prompt, add the `-y` flag.
