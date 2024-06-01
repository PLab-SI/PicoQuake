from typing import cast
import logging
from logging.handlers import RotatingFileHandler
from serial.tools.list_ports import comports
import argparse
import sys
import os
import platform

from . import __version__
from .interface import *
from .plot import *


logger = logging.getLogger(__name__)


def equal_with_tolerance(a: float, b: float, tolerance: float = 1e-6) -> bool:
    return abs(a - b) < tolerance


def check_orientation(sample: IMUSample, target: list[float], tol: float = 0.1) -> bool:
    return all(equal_with_tolerance(getattr(sample, axis), val, tol) for axis, val in zip(['acc_x', 'acc_y', 'acc_z'], target))


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
    sample_rate: float = args.sample_rate
    filter: float = args.filter
    acc_range: float = args.acc_range
    gyro_range: float = args.gyro_range
    autostart: bool = args.autostart
    yes: bool = args.yes

    if not sample_rate >= 2 * filter:
        print("Warning: sample rate should be >= 2 * filter frequency.")
    
    # Check if the output file already exists
    if os.path.isfile(out) and not yes:
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
        logger.exception(e)
        print(f"Error: {e}")
        sys.exit(1)

    # Configure device and acquire data
    try:
        device.configure_approx(sample_rate, filter, acc_range, gyro_range)
        config = device.config
        print(f"Configured to: {config}")
    except Exception as e:
        logger.exception(e)
        print(f"Error configuring device: {e}")
        sys.exit(1)
    
    try:
        if not autostart:
            input("\nPress ENTER to start acquisition...\n")
        print("Acquiring...")
        data, exception = device.acquire(seconds)
        print("Done.")
        data.to_csv(out)
        path = os.path.abspath(out)
        print(f"Data written to {path}")  
        if exception is not None:
            print("WARNING: Acquisition failed, saved data is incomplete.")
            raise exception
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
        print("\nInterrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.exception(e)
        print(f"Error: {e}")
        sys.exit(1)  
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
        logger.exception(e)
        print(f"Error: {e}")
        sys.exit(1)
    try:   
        device.configure(SampleRate.hz_12_5, Filter.hz_42, AccRange.g_4, GyroRange.dps_250)
        device.start_continuos()
        while True:
            sample = device.read_last()
            print(sample)
            sleep(interval)
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
        print("\nInterrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.exception(e)
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        device.stop()


def _plot_psd(args):
    csv_path: str = args.csv_path
    output: str = args.output
    axis: str = args.axis
    freq_min: float = args.fmin
    freq_max: float = args.fmax
    peaks: bool = args.peaks
    title: str = args.title

    output = output if output != '.' else os.path.splitext(csv_path)[0] + "_psd.png"

    try:
        result = AcquisitionData.from_csv(csv_path)
    except Exception as e:
        logger.exception(e)
        print(f"Error loading file: {e}")
        sys.exit(1)
    try:
        plot_psd(result, output, axis, freq_min, freq_max, peaks, title)
        print(f"Plot saved to {output}")
    except ModuleNotFoundError:
        print("Plotting not supported. To enable install with 'pip install picoquake[plot]'.")
        sys.exit(1)
    except Exception as e:
        logger.exception(e)
        print(f"Error: {e}")
        sys.exit(1)

def _plot_fft(args):
    csv_path: str = args.csv_path
    output: str = args.output
    axis: str = args.axis
    freq_min: float = args.fmin
    freq_max: float = args.fmax
    peaks: bool = args.peaks
    title: str = args.title

    output = output if output != '.' else os.path.splitext(csv_path)[0] + "_fft.png"

    try:
        result = AcquisitionData.from_csv(csv_path)
    except Exception as e:
        logger.exception(e)
        print(f"Error loading file: {e}")
        sys.exit(1)
    try:
        plot_fft(result, output, axis, freq_min, freq_max, peaks, title)
        print(f"Plot saved to {output}")
    except ModuleNotFoundError:
        print("Plotting not supported. To enable install with 'pip install picoquake[plot]'.")
        sys.exit(1)
    except Exception as e:
        logger.exception(e)
        print(f"Error: {e}")
        sys.exit(1)

def _plot(args):
    csv_path: str = args.csv_path
    output: str = args.output
    axis: str = args.axis
    time_start: float = args.tstart
    time_end: float = args.tend
    title: str = args.title

    output = output if output != '.' else os.path.splitext(csv_path)[0] + "_plot.png"

    try:
        result = AcquisitionData.from_csv(csv_path)
    except Exception as e:
        logger.exception(e)
        print(f"Error loading file: {e}")
        sys.exit(1)
    try:
        plot(result, output, axis, time_start, time_end, title)
        print(f"Plot saved to {output}")
    except ModuleNotFoundError:
        print("Plotting not supported. To enable install with 'pip install picoquake[plot]'.")
        sys.exit(1)
    except Exception as e:
        logger.exception(e)
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


def _info(args):
    short_id: str = args.short_id
    try:
        device = PicoQuake(short_id)
    except DeviceNotFound:
        print(f"Device with short_id {short_id} not found.")
        sys.exit(1)
    except Exception as e:
        logger.exception(e)
        print(f"Error: {e}")
        sys.exit(1)
    try:
        info = device.device_info
        print(info)
    except Exception as e:
        logger.exception(e)
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        device.stop()


def _test(args):
    tol = 0.1
    short_id: str = args.short_id
    try:
        device = PicoQuake(short_id)
    except DeviceNotFound:
        print(f"Device with short_id {short_id} not found.")
        sys.exit(1)
    except Exception as e:
        logger.exception(e)
        print(f"Error: {e}")
        sys.exit(1)
    try:
        device.configure(SampleRate.hz_12_5, Filter.hz_42, AccRange.g_4, GyroRange.dps_250)
        device.start_continuos()
        print("Point Z up...", end="", flush=True)
        while True:
            sample = cast(IMUSample, device.read_last())
            if check_orientation(sample, [0, 0, 1], tol):
                print("OK")
                break
            sleep(0.1)
        print("Point X up...", end="", flush=True)
        while True:
            sample = cast(IMUSample, device.read_last())
            if check_orientation(sample, [1, 0, 0], tol):
                print("OK")
                break
            sleep(0.1)
        print("Point Y down...", end="", flush=True)
        while True:
            sample = cast(IMUSample, device.read_last())
            if check_orientation(sample, [0, -1, 0], tol):
                print("OK")
                break
            sleep(0.1)
        print("Successful.")
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
        print("\nInterrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.exception(e)
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        device.stop()


def _reboot_to_bootsel(args):
    short_id: str = args.short_id
    try:
        device = PicoQuake(short_id)
    except DeviceNotFound:
        print(f"Device with short_id {short_id} not found.")
        sys.exit(1)
    except Exception as e:
        logger.exception(e)
        print(f"Error: {e}")
        sys.exit(1)
    try:
        device.reboot_to_bootsel()
        print("Device rebooted to BOOTSEL.")
    except Exception as e:
        logger.exception(e)
        print(f"Error: {e}")
        sys.exit(1)


def main():
    main_parser = argparse.ArgumentParser(description="PicoQuake CLI.")
    main_parser.add_argument("-v", "--version", action="version", version=f"picoquake {__version__}")
    main_parser.add_argument("--verbose", action="store_true", help="Print log messages to console.")
    main_parser.add_argument("--debug", action="store_true", help="Set log level to debug.")
    subparsers = main_parser.add_subparsers(required=True, dest="command")

    # acquire
    acquire_parser = subparsers.add_parser("acquire", help="Acquire data from a PicoQuake device.")
    acquire_parser.add_argument("short_id", help="The 4 character ID of the device. Found on the label.")
    acquire_parser.add_argument("out", help="The output CSV file.")
    acquire_parser.add_argument("-s", "--seconds", type=float, default=2.0,
                                help="Duration of the acquisition in seconds.")
    acquire_parser.add_argument("-r", "--sample_rate", type=float, default=200.0,
                                help="Sample rate in Hz. Range 12.5 - 4000 Hz. Closest available selected.")
    acquire_parser.add_argument("-f", "--filter", type=float, default=42.0,
                                help="Filter frequency in Hz. Range 42 - 3979 Hz. Closest available selected.")
    acquire_parser.add_argument("-ar", "--acc_range", type=float, default=2.0,
                                help="Acceleration range in g. Range 2 - 16 g. Closest available selected.")
    acquire_parser.add_argument("-gr", "--gyro_range", type=float, default=250.0,
                                help="Gyro range in dps. Range 15.625 - 2000 dps. Closest available selected.")
    acquire_parser.add_argument("-a", "--autostart", action="store_true",
                                help="Start acquisition without user confirmation.")
    acquire_parser.add_argument("-y", "--yes", action="store_true",
                                help="Skip overwrite prompt.")
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

    # device info
    info_parser = subparsers.add_parser("info", help="Display device information.")
    info_parser.add_argument("short_id", help="The 4 character ID of the device. Found on the label.")
    info_parser.set_defaults(func=_info)

    # test
    test_parser = subparsers.add_parser("test", help="Test device.")
    test_parser.add_argument("short_id", help="The 4 character ID of the device. Found on the label.")
    test_parser.set_defaults(func=_test)

    # reboot to bootsel
    reboot_bootsel = subparsers.add_parser("bootsel", help="Reboot device to BOOTSEL.")
    reboot_bootsel.add_argument("short_id", help="The 4 character ID of the device. Found on the label.")
    reboot_bootsel.set_defaults(func=_reboot_to_bootsel)

    # plot PSD
    fftplot_parser = subparsers.add_parser("plot_psd", help="Plot Power Spectral Density of acquired data.")
    fftplot_parser.add_argument("csv_path", help="The CSV file containing the acquired data.")
    fftplot_parser.add_argument("output", help="The output file to save the plot to. '.' to save next to the data file.")
    fftplot_parser.add_argument("-a", "--axis", default="xyz", help="Axis to plot, must be 'x', 'y', 'z', or a combination")
    fftplot_parser.add_argument("--fmin", type=float, default=0.0, help="Minimum frequency to plot.")
    fftplot_parser.add_argument("--fmax", type=float, default=1000.0, help="Maximum frequency to plot.")
    fftplot_parser.add_argument("--peaks", action="store_true", help="Annotate peaks on the plot.")
    fftplot_parser.add_argument("--title", help="Title of the plot.", default=None)
    fftplot_parser.set_defaults(func=_plot_psd)

    # plot FFT
    fftplot_parser = subparsers.add_parser("plot_fft", help="Plot Fast Fourier Transform of acquired data.")
    fftplot_parser.add_argument("csv_path", help="The CSV file containing the acquired data.")
    fftplot_parser.add_argument("output", help="The output file to save the plot to. '.' to save next to the data file.")
    fftplot_parser.add_argument("-a", "--axis", default="xyz", help="Axis to plot, must be 'x', 'y', 'z', or a combination")
    fftplot_parser.add_argument("--fmin", type=float, default=0.0, help="Minimum frequency to plot.")
    fftplot_parser.add_argument("--fmax", type=float, default=1000.0, help="Maximum frequency to plot.")
    fftplot_parser.add_argument("--peaks", action="store_true", help="Annotate peaks on the plot.")
    fftplot_parser.add_argument("--title", help="Title of the plot.", default=None)
    fftplot_parser.set_defaults(func=_plot_fft)

    # plot
    plot_parser = subparsers.add_parser("plot", help="Plot acquired data (time series).")
    plot_parser.add_argument("csv_path", help="The CSV file containing the acquired data.")
    plot_parser.add_argument("output", help="The output file to save the plot to. '.' to save next to the data file.")
    plot_parser.add_argument("-a", "--axis", default="xyz", help="Axis to plot, must be 'x', 'y', 'z', or a combination")
    plot_parser.add_argument("--tstart", type=float, default=0.0, help="Start time of the plot.")
    plot_parser.add_argument("--tend", type=float, default=None, help="End time of the plot.")
    plot_parser.add_argument("--title", help="Title of the plot.", default=None)
    plot_parser.set_defaults(func=_plot)

    args = main_parser.parse_args()

    # logging
    log_path = os.path.join(_get_log_path("picoquake"), "picoquake.log")
    file_handler =RotatingFileHandler(log_path, mode='a', maxBytes=15*1024*1024, backupCount=5)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(file_handler)
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)
    if args.verbose:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        logging.getLogger().addHandler(stream_handler)
    
    args.func(args)
    
if __name__ == '__main__':
    main()
