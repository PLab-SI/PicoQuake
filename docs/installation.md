# Installation

## Requirements

- *Windows*, *Linux* or *macOS*
- [*Python*](https://www.python.org/downloads/){:target="_blank"} *3.9* or higher
- [*pip*](https://pip.pypa.io/en/stable/installation/){:target="_blank"}

## Basic installation

Run command:

```bash
pip install picoquake
```

Recommended way to install if you don't need plotting capabilities. Only supports saving CSV data.

## Plotting capabilities

Run command:

```bash
pip install 'picoquake[plot]'
```

Enables creating diagrams in time and frequency domain. Additional dependencies will be installed:

- *NumPy*
- *SciPy*
- *Matplotlib*

## Test installation

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
