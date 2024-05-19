from itertools import permutations

from .data import *

def plot_supported() -> bool:
    try:
        import numpy as np
        import matplotlib.pyplot as plt
        from scipy.signal import welch, find_peaks
        return True
    except ModuleNotFoundError:
        return False

def plot_fft(result: AcquisitionResult, output_file: str, axis: str = "xyz",
             freq_min: float = 0, freq_max: float = float("inf"),
             show_peaks: bool = False, title=None) -> None:
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.signal import welch, find_peaks

    combinations = set(''.join(p) for i in range(1, 4) for p in permutations("xyz", i))
    if axis not in combinations:
        raise ValueError("Invalid axis, must be 'x', 'y', 'z', or a combination.")
    if not result.integrity:
        print(f"WARNING: Data integrity compromised, {result.skipped_samples} samples skipped.")
    
    acc_x = np.array([s.acc_x for s in result.samples])
    acc_y = np.array([s.acc_y for s in result.samples])
    acc_z = np.array([s.acc_z for s in result.samples])

    plt.figure(figsize=(10, 8))  # Increase figure size. You can adjust the values as needed.

    for ax, acc, color in zip(axis, [acc_x, acc_y, acc_z], ["red", "green", "blue"]):
        f, p_den = welch(acc, fs=result.config.data_rate.param_value, nperseg=2048, scaling="density")
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
    plt.savefig(output_file)
