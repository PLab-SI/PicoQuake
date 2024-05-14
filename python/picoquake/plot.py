from itertools import permutations

from .data import *

def plot_supported() -> bool:
    try:
        import numpy
        import matplotlib
        return True
    except ImportError:
        return False

def plot_fft(result: AcquisitionResult, output_file: str, axis: str = "xyz",
             freq_min: float = 0., freq_max: float = 0.):
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib import mlab
    
    combinations = set(''.join(p) for i in range(1, 4) for p in permutations("xyz", i))
    if axis not in combinations:
        raise ValueError("Invalid axis, must be 'x', 'y', 'z', or a combination.")
    if not result.integrity:
        print(f"WARNING: Data integrity compromised, {result.skipped_samples} samples skipped.")
    
    acc_x = np.array([s.acc_x for s in result.samples])
    acc_y = np.array([s.acc_y for s in result.samples])
    acc_z = np.array([s.acc_z for s in result.samples])

    plt.figure(figsize=(10, 8))  # Increase figure size. You can adjust the values as needed.
    if "x" in axis:
        spec_x, freq_x, _ = mlab.specgram(acc_x, Fs=result.config.data_rate.param_value, NFFT=result.num_samples, mode="psd")
        plt.plot(freq_x, spec_x, label="x", linewidth=0.5)
    if "y" in axis:
        spec_y, freq_y, _ = mlab.specgram(acc_y, Fs=result.config.data_rate.param_value, NFFT=result.num_samples, mode="psd")
        plt.plot(freq_y, spec_y, label="y", linewidth=0.5)
    if "z" in axis:
        spec_z, freq_z, _ = mlab.specgram(acc_z, Fs=result.config.data_rate.param_value, NFFT=result.num_samples, mode="psd")
        plt.plot(freq_z, spec_z, label="z", linewidth=0.5)

    plt.xlabel("Frequency (Hz)")
    plt.ylabel("PSD (g^2/Hz)")
    plt.yscale("log")
    plt.xlim((freq_min, freq_max))
    plt.grid(True, "both")  # Add grid
    plt.minorticks_on()  # Add minor ticks
    plt.legend(loc="upper right")
    plt.autoscale(enable=True, axis='y', tight=True)
    plt.savefig(output_file)
