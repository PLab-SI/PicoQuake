# CLI Reference

## Usage

```bash
picoquake [-h] [-v] [--verbose] [--debug] {acquire,display,list,test,plot_psd,plot} ...
```

### Global Options

- `-v`, `--version`: Show the version of the CLI.
- `--debug`: Set log level to debug.
- `--verbose`: Print log messages to console.

### Commands

#### acquire

Acquire data from a PicoQuake device.

```bash
picoquake acquire [-h] [-s SECONDS] [-r SAMPLE_RATE] [-f FILTER] [-ar ACC_RANGE] [-gr GYRO_RANGE] [-a] [-y] short_id out
```

- `short_id`: The 4 character ID of the device. Found on the label.
- `out`: The output CSV file.
- `-s`, `--seconds`: Duration of the acquisition in seconds (default: 2.0).
- `-r`, `--sample_rate`: Sample rate in Hz. Range 12.5 - 4000 Hz. Closest available selected (default: 200.0).
- `-f`, `--filter`: Filter frequency in Hz. Range 42 - 3979 Hz. Closest available selected (default: 42.0).
- `-ar`, `--acc_range`: Acceleration range in g. Range 2 - 16 g. Closest available selected (default: 2.0).
- `-gr`, `--gyro_range`: Gyro range in dps. Range 15.625 - 2000 dps. Closest available selected (default: 250.0).
- `-a`, `--autostart`: Start acquisition without user confirmation.
- `-y`, `--yes`: Skip overwrite prompt.

#### trigger

Start acquisition at a RMS threshold trigger.

```bash
picoquake trigger [-h] [-r SAMPLE_RATE] [-f FILTER] [-ar ACC_RANGE]
                       [-gr GYRO_RANGE] [--rms_threshold RMS_THRESHOLD]
                       [--pre_seconds PRE_SECONDS] [--post_seconds POST_SECONDS]
                       [--source {accel,gyro}] [-a AXIS] [--rms_window RMS_WINDOW]
                       [-y] short_id out
```

- `short_id`: The 4 character ID of the device. Found on the label.
- `out`: The output CSV file.
- `-r`, `--sample_rate`: Sample rate in Hz. Range 12.5 - 4000 Hz. Closest available selected (default: 200.0).
- `-f`, `--filter`: Filter frequency in Hz. Range 42 - 3979 Hz. Closest available selected (default: 42.0).
- `-ar`, `--acc_range`: Acceleration range in g. Range 2 - 16 g. Closest available selected (default: 2.0).
- `-gr`, `--gyro_range`: Gyro range in dps. Range 15.625 - 2000 dps. Closest available selected (default: 250.0).
- `--rms_threshold`: RMS threshold for triggering.
- `--pre_seconds`: Duration before trigger in seconds (default: 0.0).
- `--post_seconds`: Duration after trigger in seconds (default: 1.0).
- `--source`: Source for triggering, must be 'accel' or 'gyro' (default: 'accel').
- `-a`, `--axis`: Axis to plot, must be 'x', 'y', 'z', or a combination (default: 'xyz').
- `--rms_window`: Window size for RMS calculation (default: 1.0).
- `-y`, `--yes`: Skip overwrite prompt.


#### run

Run acquisition from a TOML configuration file. Supports advanced options like trigger and continuous acquisition.

```bash
picoquake run [-h] config
```

- `config`: TOML configuration file.

Example configuration file:

```toml
# Example configuration file for 'run' command
# either [acquire] or [trigger] section is required

[device]
short_id = "C6E3" # short id of the device

[config]
sample_rate = 1000 # sample rate in Hz. Range 12.5 - 4000 Hz. Closest available selected.
filter = 100 # filter frequency in Hz. Range 42 - 3979 Hz. Closest available selected.
acc_range = 16 # acceleration range in g. Range 2 - 16 g. Closest available selected.
gyro_range = 1000 # gyro range in dps. Range 15.625 - 2000 dps. Closest available selected.

[acquire]
# define duration in seconds or number of samples
seconds = 3
# n_samples = 10000

# [trigger]
# rms_threshold = 1.0 # RMS threshold for trigger
# pre_seconds = 1 # duration before trigger
# post_seconds = 2 # duration after trigger
# source = "accel" # trigger source: "accel" or "gyro"
# axis = "xyz" # trigger axis, must be 'x', 'y', 'z', or a combination
# rms_window = 1.0 # window for RMS calculation in seconds

[output]
path = "pq_acq.csv" # output file path or directory if use_timestamp is true
confirm_overwrite = true # require confirmation before overwriting
sequential = true # add sequence number to filename
use_timestamp = false # use timestamp as filename

# [continuous] # continuous acquisition if this section is defined
# interval = 0 # interval in seconds, 0 for continuous acquisition
```

#### display

Display live data from a device.

```bash
picoquake display [-h] [-i INTERVAL] short_id
```

- `short_id`: The 4 character ID of the device. Found on the label.
- `-i`, `--interval`: Interval between samples in seconds. Range 0.1 - 10 s (default: 1.0).

#### list

List connected PicoQuake devices.

```bash
picoquake list [-h] [-a]
```

- `-a`, `--all`: List all serial ports.

#### info

Display device information.

```bash
picoquake info [-h] short_id
```

- `short_id`: The 4 character ID of the device. Found on the label.

#### test

Test device.

```bash
picoquake test [-h] short_id
```

- `short_id`: The 4 character ID of the device. Found on the label.

#### bootsel

Put device in BOOTSEL mode.

```bash
picoquake bootsel [-h] short_id
```

- `short_id`: The 4 character ID of the device. Found on the label.

#### plot

Plot acquired acceleration data (time series).

```bash
picoquake plot [-h] [-a AXIS] [--tstart TSTART] [--tend TEND] [--title TITLE] csv_path output
```

- `csv_path`: The CSV file containing the acquired data.
- `output`: The output file to save the plot to. '.' to save next to the data file.
- `-a`, `--axis`: Axis to plot, must be 'x', 'y', 'z', or a combination (default: xyz).
- `--tstart`: Start time of the plot (default: 0.0).
- `--tend`: End time of the plot (default: None).
- `--title`: Title of the plot (default: None).
- `--rms`: Calculate and display RMS values.
- `--rms_detrend`: Detrend the data before calculating RMS.
- `--rms_window`: Window size for RMS calculation (default: 1.0 s).

#### plot_psd

Plot Power Spectral Density of acquired acceleration data.

```bash
picoquake plot_psd [-h] [-a AXIS] [--fmin FMIN] [--fmax FMAX] [--peaks] [--title TITLE] csv_path output
```

- `csv_path`: The CSV file containing the acquired data.
- `output`: The output file to save the plot to. '.' to save next to the data file.
- `-a`, `--axis`: Axis to plot, must be 'x', 'y', 'z', or a combination (default: xyz).
- `--fmin`: Minimum frequency to plot (default: 0.0).
- `--fmax`: Maximum frequency to plot (default: 1000.0).
- `--peaks`: Annotate peaks on the plot.
- `--title`: Title of the plot (default: None).

#### plot_fft

Plot Fast Fourier Transform of acquired acceleration data.

```bash
picoquake plot_fft [-h] [-a AXIS] [--fmin FMIN] [--fmax FMAX] [--peaks] [--title TITLE] csv_path output
```

- `csv_path`: The CSV file containing the acquired data.
- `output`: The output file to save the plot to. '.' to save next to the data file.
- `-a`, `--axis`: Axis to plot, must be 'x', 'y', 'z', or a combination (default: xyz).
- `--fmin`: Minimum frequency to plot (default: 0.0).
- `--fmax`: Maximum frequency to plot (default: 1000.0).
- `--peaks`: Annotate peaks on the plot.
- `--title`: Title of the plot (default: None).
