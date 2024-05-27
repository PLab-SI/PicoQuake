# PicoQuake

Python library for the *PicoQuake* USB vibration sensor.

# Installation

## Requirements

- *Windows*, *Linux* or *macOS*
- [*Python*](https://www.python.org/downloads/) *3.9* or higher
- [*pip*](https://pip.pypa.io/en/stable/installation/)

## Basic installation

```bash
pip install picoquake
```

Recommended way to install if you don't need plotting capabilities. Only supports saving CSV data.

## Plotting capabilities

```bash
pip install 'picoquake[plot]'
```

Enables creating diagrams in time and frequency domain. Additional dependencies will be installed:

- *NumPy*
- *SciPy*
- *Matplotlib*
