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

Test a device.

```bash
picoquake test [-h] short_id
```

- `short_id`: The 4 character ID of the device. Found on the label.

#### plot

Plot acquired data (time series).

```bash
picoquake plot [-h] [-a AXIS] [--tstart TSTART] [--tend TEND] [--title TITLE] csv_path output
```

- `csv_path`: The CSV file containing the acquired data.
- `output`: The output file to save the plot to. '.' to save next to the data file.
- `-a`, `--axis`: Axis to plot, must be 'x', 'y', 'z', or a combination (default: xyz).
- `--tstart`: Start time of the plot (default: 0.0).
- `--tend`: End time of the plot (default: None).
- `--title`: Title of the plot (default: None).

#### plot_psd

Plot Power Spectral Density of acquired data.

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

Plot Fast Fourier Transform of acquired data.

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
