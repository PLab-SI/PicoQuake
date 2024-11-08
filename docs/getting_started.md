# Getting Started

## Requirements

A computer with:

- *Windows*, *Linux* or *macOS*
- [*Python*](https://www.python.org/downloads/){:target="_blank"} *3.9* or higher
- [*pip*](https://pip.pypa.io/en/stable/installation/){:target="_blank"}

## Install

### Basic installation

Run command:

```bash
pip install picoquake
```

The recommended way to install if you don't need plotting capabilities. Only supports saving CSV data.

### Plotting capabilities

Run command:

```bash
pip install 'picoquake[plot]'
```

Enables creating diagrams in time and frequency domain. Additional dependencies will be installed:

- *NumPy*
- *SciPy*
- *Matplotlib*

### Test Installation

Run command:

```bash
picoquake --version
```

The above command should print the installed version of the package.
If you see an error, try the alternative:

```bash
python -m picoquake --version
```

!!! note
    `python -m` prefix is needed if the python scripts directory is not in the system PATH. It depends on your OS and the way *Python* was installed. Check the official *Python* documentation for more information.

## Connect

 Connect *PicoQuake* to your computer. The green LED will light up.

 Run command:

```bash
picoquake --list
```

It will print a list of connected devices:

```
PicoQuake C6E3: /dev/cu.usbmodem1101
...
```

!!! info "No devices"
    If you don't see any devices, check the connection and try again. You can also try another USB port.

!!! note "Short ID"
    All further commands require a `Short ID` of the device. It's printed on the device label, or can be read by the `--list` command.

## Test



Run command:

```bash
picoquake display c6e3
```

Orange LED will light up, and realtime data will be displayed in the terminal. Try to move the device to see the changes.


## What's next?

See [Usage](usage.md) for detailed instructions. 

Run `picoquake --help` to see all available commands.