# Plotting

!!! note
    To enable plotting, `picoquake` must be installed with the `plot` extra. See [Installation](installation.md) for more information.

## Plot time series data

Plot time series data from a CSV file.

![Time series plot example](assets/plot_example_ts.jpg)

```bash
picoquake plot <csv_path> <output>
```

You can specify the time range to plot using the `--tstart` and `--tend` arguments.
The axes can be selected using the `-xyz` flag. Input only the desired axes in any order.

For more information about the command, see [CLI reference](cli.md#plot).

## Plot power spectral density (PSD)

Plot power spectral density (PSD) data from a CSV file.

```bash
picoquake plot_psd <csv_path> <output>
```

![PSD plot example](assets/plot_example_psd.jpg)

You can specify the frequency range to plot using the `--fmin` and `--fmax` arguments.
The axes can be selected using the `-xyz` flag. Input only the desired axes in any order.
To annotate peaks, use the `--peaks` flag.

For more information about the command, see [CLI reference](cli.md#plot_psd).

!!! note
    PSD plot filters out the DC component of the signal.

??? info "Power spectral density (PSD)"
    Power Spectral Density (PSD) represents a signal's power distribution across different frequencies. It's commonly used to analyze broadband random signals. The PSD's amplitude is normalized based on the spectral resolution used during signal digitization.

    For vibration data, the PSD is measured in units of g²/Hz. This unit allows for the comparison and overlay of random data regardless of the spectral resolution used in measurement.

