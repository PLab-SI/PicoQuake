from itertools import permutations

from .data import *

def plot_psd(result: AcquisitionData, output_file: str, axis: str = "xyz",
             freq_min: float = 0, freq_max: Optional[float] = None,
             show_peaks: bool = False, title=None) -> None:
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.signal import welch, find_peaks

    combinations = set(''.join(p) for i in range(1, 4) for p in permutations("xyz", i))
    if axis not in combinations:
        raise ValueError("Invalid axis, must be 'x', 'y', 'z', or a combination.")
    if not result.integrity:
        print(f"Warning: Data integrity compromised, {result.skipped_samples} samples skipped.")

    # check Nyquist criterion
    if result.config.sample_rate.param_value < 2 * result.config.filter.param_value:
        print(f"Warning: sample rate {result.config.sample_rate.param_value} Hz is "
              f"not >= 2 * filter frequency {result.config.filter.param_value} Hz.")
    
    # check frequency range
    if freq_max is None:
        freq_max = result.config.sample_rate.param_value // 2
    elif freq_max > result.config.sample_rate.param_value // 2:
        print(f"Warning: freq_max ({freq_max} Hz) is greater "
              f"than 0.5 x sample rate ({result.config.sample_rate.param_value} Hz). "
              f"Limiting to {result.config.sample_rate.param_value // 2} Hz.")
        freq_max = result.config.sample_rate.param_value // 2

    if freq_min >= freq_max:
        raise ValueError("freq_min must be less than freq_max.")

    acc_x = np.array([s.acc_x for s in result.samples])
    acc_y = np.array([s.acc_y for s in result.samples])
    acc_z = np.array([s.acc_z for s in result.samples])

    # calculate segment length based on plot frequency range
    nperseg = min(int((100 * result.config.sample_rate.param_value) // (freq_max - freq_min)), len(acc_x))

    plt.figure(figsize=(10, 8))  # Increase figure size. You can adjust the values as needed.
    for ax, acc, color in zip(['x', 'y', 'z'], [acc_x, acc_y, acc_z], ["red", "green", "blue"]):
        if ax in axis:
            f, p_den = welch(acc, fs=result.config.sample_rate.param_value, nperseg=nperseg, scaling="density")
            mask = (f >= freq_min) & (f <= freq_max)
            f = f[mask]
            p_den = p_den[mask]
            plt.plot(f, p_den, label=ax, linewidth=1.0, color=color)
            if show_peaks:
                peaks, _ = find_peaks(p_den)
                if len(peaks) > 0:
                    peak_heights = p_den[peaks]
                    top_peaks = peaks[np.argsort(peak_heights)[-3:]]
                    for peak in top_peaks:
                        plt.annotate(f'{f[peak]:.1f} Hz', 
                                    (f[peak], p_den[peak]), 
                                    textcoords="offset points", 
                                    xytext=(0,30), 
                                    ha='center', 
                                    color=color,
                                    arrowprops=dict(facecolor=color, shrink=0.1, width=3, headwidth=6, headlength=6),
                                    bbox=dict(boxstyle="round,pad=0.3", edgecolor=color, facecolor='white', alpha=1.0))

    if title is not None:
        plt.title(title, pad=40)
    elif result.filename is not None:
        plt.title(result.filename, pad=40)
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("PSD [g$^2$/Hz]")
    plt.yscale("log")
    plt.grid(True, "both")
    plt.minorticks_on()
    plt.legend(loc="upper right")
    plt.autoscale(enable=True, axis='y', tight=False)
    plt.savefig(output_file, dpi=200)

def plot_fft(result: AcquisitionData, output_file: str, axis: str = "xyz",
             freq_min: float = 0, freq_max: Optional[float] = None,
             show_peaks: bool = False, title=None) -> None:
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.fft import fft, fftfreq
    from scipy.signal import find_peaks
    from scipy.signal.windows import hann

    combinations = set(''.join(p) for i in range(1, 4) for p in permutations("xyz", i))
    if axis not in combinations:
        raise ValueError("Invalid axis, must be 'x', 'y', 'z', or a combination.")
    if not result.integrity:
        print(f"Warning: Data integrity compromised, {result.skipped_samples} samples skipped.")

    # check Nyquist criterion
    if result.config.sample_rate.param_value < 2 * result.config.filter.param_value:
        print(f"Warning: sample rate {result.config.sample_rate.param_value} Hz is "
              f"not >= 2 * filter frequency {result.config.filter.param_value} Hz.")
    
    # check frequency range
    if freq_max is None:
        freq_max = result.config.sample_rate.param_value // 2
    elif freq_max > result.config.sample_rate.param_value // 2:
        print(f"Warning: freq_max ({freq_max} Hz) is greater "
              f"than 0.5 x sample rate ({result.config.sample_rate.param_value} Hz). "
              f"Limiting to {result.config.sample_rate.param_value // 2} Hz.")
        freq_max = result.config.sample_rate.param_value // 2

    if freq_min >= freq_max:
        raise ValueError("freq_min must be less than freq_max.")

    acc_x = np.array([s.acc_x for s in result.samples])
    acc_y = np.array([s.acc_y for s in result.samples])
    acc_z = np.array([s.acc_z for s in result.samples])


    plt.figure(figsize=(10, 8))  # Increase figure size. You can adjust the values as needed.
    for ax, acc, color in zip(['x', 'y', 'z'], [acc_x, acc_y, acc_z], ["red", "green", "blue"]):
        if ax in axis:
            N = len(acc)
            T = 1.0 / result.config.sample_rate.param_value
            # Apply a window function
            window = hann(len(acc))
            acc = acc * window
            yf = fft(acc)
            xf = fftfreq(N, T)
            mask = (xf >= freq_min) & (xf <= freq_max)
            xf = xf[mask]
            yf = yf[mask]
            plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]), label=ax, linewidth=1.0, color=color)
            if show_peaks:
                peaks, _ = find_peaks(2.0/N * np.abs(yf[0:N//2]))
                if len(peaks) > 0:
                    peak_heights = 2.0/N * np.abs(yf[0:N//2])[peaks]
                    top_peaks = peaks[np.argsort(peak_heights)[-3:]]
                    for peak in top_peaks:
                        plt.annotate(f'{xf[peak]:.1f} Hz', 
                                    (xf[peak], 2.0/N * np.abs(yf[0:N//2])[peak]), 
                                    textcoords="offset points", 
                                    xytext=(0,30), 
                                    ha='center', 
                                    color=color,
                                    arrowprops=dict(facecolor=color, shrink=0.1, width=3, headwidth=6, headlength=6),
                                    bbox=dict(boxstyle="round,pad=0.3", edgecolor=color, facecolor='white', alpha=1.0))


    if title is not None:
        plt.title(title, pad=40)
    elif result.filename is not None:
        plt.title(result.filename, pad=40)
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Amplitude [g]")
    plt.yscale("log")
    plt.grid(True, "both")
    plt.minorticks_on()
    plt.legend(loc="upper right")
    plt.autoscale(enable=True, axis='y', tight=False)
    plt.savefig(output_file, dpi=200)

def plot(result: AcquisitionData, output_file: str, axis: str = "xyz",
         tstart: float = 0, tend: float = float("inf"), title=None) -> None:
    import numpy as np
    import matplotlib.pyplot as plt

    combinations = set(''.join(p) for i in range(1, 4) for p in permutations("xyz", i))
    if axis not in combinations:
        raise ValueError("Invalid axis, must be 'x', 'y', 'z', or a combination.")
    if not result.integrity:
        print(f"Warning: Data integrity compromised, {result.skipped_samples} samples skipped.")

    acc_x = np.array([s.acc_x for s in result.samples])
    acc_y = np.array([s.acc_y for s in result.samples])
    acc_z = np.array([s.acc_z for s in result.samples])

    plt.figure(figsize=(10, 6))  # Increase figure size. You can adjust the values as needed.

    t = np.linspace(0, len(acc_x) / result.config.sample_rate.param_value, len(acc_x))
    if(tend == None):
        tend = len(acc_x) / result.config.sample_rate.param_value
    mask = (t >= tstart) & (t <= tend)
    t = t[mask]
    for ax, acc, color in zip(['x', 'y', 'z'], [acc_x, acc_y, acc_z], ["red", "green", "blue"]):
        if ax in axis:
            acc = acc[mask]
            plt.plot(t, acc, label=ax, linewidth=1.0, color=color)

    if title is not None:
        plt.title(title, pad=20)
    elif result.filename is not None:
        plt.title(result.filename, pad=20)
    plt.xlabel("Time [s]")
    plt.ylabel("Acceleration [g]")
    plt.grid(True, "both")
    plt.minorticks_on()
    plt.legend(loc="upper right")
    plt.autoscale(enable=True, axis='y', tight=False)
    plt.savefig(output_file, dpi=200)


