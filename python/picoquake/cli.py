from typing import cast
import csv
import logging
from serial.tools.list_ports import comports
import argparse
import sys
import os
import platform

from . import __version__
from .interface import *
from .plot import *

def _get_log_path(app_name):
    """
    Determines the operating system and returns the appropriate log directory path for the application.

    Args:
    app_name (str): The name of the application.

    Returns:
    str: The full path to the directory where logs should be stored.
    """
    if platform.system() == 'Windows':
        # Windows: Use LOCALAPPDATA
        log_path = os.path.join(os.environ['LOCALAPPDATA'], app_name, 'logs')
    elif platform.system() == 'Linux':
        # Linux: Use a hidden directory in the user's home directory
        log_path = os.path.join(os.path.expanduser('~'), f'.{app_name}', 'logs')
    elif platform.system() == 'Darwin':
        # macOS: Use the Library/Logs directory in the user's home directory
        log_path = os.path.expanduser(f'~/Library/Logs/{app_name}')
    else:
        # Fallback for any other unknown OS
        log_path = os.path.join(os.path.expanduser('~'), f'{app_name}_logs')

    # Create the log directory if it does not exist
    os.makedirs(log_path, exist_ok=True)
    return log_path


def _acquire(args):
    short_id: str = args.short_id
    out: str = args.out
    seconds: float = args.seconds
    data_rate: float = args.data_rate
    filter: float = args.filter
    acc_range: float = args.acc_range
    gyro_range: float = args.gyro_range
    autostart: bool = args.autostart
    overwrite: bool = args.overwrite
    verbose: bool = args.verbose

    if verbose:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        logging.getLogger().addHandler(stream_handler)
    
    # Check if the output file already exists
    if os.path.isfile(out) and not overwrite:
        usr = input(f"File {out} already exists. Overwrite? y/n: ")
        if usr.lower() != 'y':
            print("Exiting...")
            sys.exit(0)

    # Find the device
    try:
        device = PicoQuake(short_id)
    except DeviceNotFound:
        print(f"Device with short_id {short_id} not found.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error: {e}")
        print(f"Error: {e}")
        sys.exit(1)

    # Configure device and acquire data
    try:
        device.configure_approx(data_rate, filter, acc_range, gyro_range)
        config = device.config
        print(f"Configured to: {config}")
        if not autostart:
            input("\nPress ENTER to start acquisition...\n")
        print("Acquiring...")
        result = cast(AcquisitionResult, device.acquire(seconds))
        print("Done.")
        if not result.integrity:
            print(f"WARNING: Data compromised, {result.skipped_samples} samples skipped.")
    except KeyboardInterrupt:
        logging.info("Interrupted by user.")
        print("Interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error: {e}")
        print(f"Error: {e}")
        sys.exit(1)
    else:
        result.to_csv(out)
        path = os.path.abspath(out)
        print(f"Data written to {path}")   
    finally:
        device.stop()


def _live_display(args):
    short_id: str = args.short_id
    interval: float = args.interval
    if interval < 0.1:
        interval = 0.1
    elif interval > 10:
        interval = 10
    
    try:
        device = PicoQuake(short_id)
    except DeviceNotFound:
        print(f"Device with short_id {short_id} not found.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error: {e}")
        print(f"Error: {e}")
        sys.exit(1)
    try:   
        device.configure(DataRate.hz_12_5, Filter.hz_42, AccRange.g_4, GyroRange.dps_250)
        device.start_continuos()
        while True:
            sample = device.acquire()
            print(sample)
            sleep(interval)
    except KeyboardInterrupt:
        logging.info("Interrupted by user.")
        print("Interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Error: {e}")
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        device.stop()


def _plot_fft(args):
    filename: str = args.filename
    output: str = args.output
    axis: str = args.axis
    freq_min: float = args.freq_min
    freq_max: float = args.freq_max

    output = output if output != '.' else os.path.splitext(filename)[0] + "_fft.png"

    try:
        result = AcquisitionResult.from_csv(filename)
    except Exception as e:
        logging.error(f"Error loading file: {e}")
        print(f"Error loading file: {e}")
        sys.exit(1)
    try:
        plot_fft(result, output, axis, freq_min, freq_max)
        print(f"Plot saved to {output}")
    except Exception as e:
        logging.error(f"Error: {e}")
        print(f"Error: {e}")
        sys.exit(1)


def _list_devices(args):
    all_ports = args.all
    ports = comports()
    for p in ports:
        if p.vid == VID and p.pid == PID and p.serial_number:
            short_id = DeviceInfo.unique_id_to_short_id(p.serial_number)
            print(f"PicoQuake {short_id}: {p.device}")
        elif all_ports:
            print(f"Unknown device: {p.device}, description: {p.description}")


def main():
    file_logger = logging.FileHandler(os.path.join(_get_log_path("picoquake"), "picoquake.log"), mode='a')
    file_logger.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(file_logger)
    logging.getLogger().setLevel(logging.DEBUG)
    
    main_parser = argparse.ArgumentParser(description="PicoQuake CLI.")
    main_parser.add_argument("-v", "--version", action="version", version=f"picoquake {__version__}")
    subparsers = main_parser.add_subparsers(required=True, dest="command")

    # acquire
    acquire_parser = subparsers.add_parser("acquire", help="Acquire data from a PicoQuake device.")
    acquire_parser.add_argument("short_id", help="The 4 character ID of the device. Found on the label.")
    acquire_parser.add_argument("out", help="The output CSV file to write the data to.")
    acquire_parser.add_argument("-s", "--seconds", type=float, default=2.0,
                                help="Duration of the acquisition in seconds.")
    acquire_parser.add_argument("-r", "--data_rate", type=float, default=200.0,
                                help="Data rate in Hz. Range 12.5 - 4000 Hz. Closest available selected.")
    acquire_parser.add_argument("-f", "--filter", type=float, default=42.0,
                                help="Filter frequency in Hz. Range 42 - 3979 Hz. Closest available selected.")
    acquire_parser.add_argument("-ar", "--acc_range", type=float, default=2.0,
                                help="Acceleration range in g. Range 2 - 16 g. Closest available selected.")
    acquire_parser.add_argument("-gr", "--gyro_range", type=float, default=250.0,
                                help="The gyroscope range in dps. Range 15.625 - 2000 dps. Closest available selected.")
    acquire_parser.add_argument("-a", "--autostart", action="store_true",
                                help="Start acquisition without user confirmation.")
    acquire_parser.add_argument("-x", "--overwrite", action="store_true",
                                help="Overwrite is output file exists.")
    acquire_parser.add_argument("-v", "--verbose", action="store_true",
                                help="Enable verbose logging")
    acquire_parser.set_defaults(func=_acquire)

    # display
    live_disp_parser = subparsers.add_parser("display", help="Display live data from device.")
    live_disp_parser.add_argument("short_id", help="The 4 character ID of the device. Found on the label.")
    live_disp_parser.add_argument("-i", "--interval", type=float, default=1.0,
                                  help="Interval between samples in seconds. Range 0.1 - 10 s.")
    live_disp_parser.set_defaults(func=_live_display)

    # list devices
    list_devices_parser = subparsers.add_parser("list", help="List connected PicoQuake devices.")
    list_devices_parser.add_argument("-a", "--all", action="store_true", help="List all serial ports.")
    list_devices_parser.set_defaults(func=_list_devices)

    # plot fft
    fftplot_parser = subparsers.add_parser("fftplot", help="Plot FFT of acquired data.")
    fftplot_parser.add_argument("filename", help="The CSV file containing the acquired data.")
    fftplot_parser.add_argument("output", help="The output file to save the plot to. '.' to save next to the data file.")
    fftplot_parser.add_argument("-a", "--axis", default="xyz", help="Axis to plot, must be 'x', 'y', 'z', or a combination")
    fftplot_parser.add_argument("-fmin", "--freq_min", type=float, default=5.0, help="Minimum frequency to plot.")
    fftplot_parser.add_argument("-fmax", "--freq_max", type=float, default=100.0, help="Maximum frequency to plot.")
    fftplot_parser.set_defaults(func=_plot_fft)
    
    args = main_parser.parse_args()
    args.func(args)
    
if __name__ == '__main__':
    main()
