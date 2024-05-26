# Installation

## Requirements

- *Windows*, *Linux* or *macOS*
- [*Python*](https://www.python.org/downloads/){:target="_blank"} *3.9* or higher
- [*pip*](https://pip.pypa.io/en/stable/installation/){:target="_blank"}

## Basic installation

```bash
pip install picoquake
```

Recommended way to install if you don't need plotting capabilities. Only supports saving CSV data.

## Plotting capabilities

```bash
pip install 'picoquake[plot]'
```

Enables creating diagrams in time and frequency domain. Necessary dependencies will be installed:

- *NumPy*
- *SciPy*
- *Matplotlib*
