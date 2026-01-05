"""
This module implements various data analysis functions.
"""

from typing import List, Tuple, Union

from .data import IMUSample


def mean(data: Union[List[float], List[int]]) -> float:
    """
    Calculate the mean of a list of values.
    
    Args:
    data: List of values.

    Returns:
    The mean of the values.
    """

    if len(data) == 0:
        return 0
    return sum(data) / len(data)


def detrend(data: Union[List[float], List[int]]) -> Union[List[float], List[int]]:
    """
    Remove the trend from a list of values.
    
    Args:
    data: List of values.

    Returns:
    List with the trend removed.
    """

    m = mean(data)
    return [x - m for x in data]


def rms(data: Union[Union[List[float], List[int]], Tuple[Union[List[float], List[int]], ...]],
        de_trend: bool=False) -> float:
    """
    Calculate the root mean square of a list of values.
    
    Args:
    data: List of values or a tuple of lists of values. 
          If a tuple is provided, the squares of the values in each list are summed.
    de_trend: If True, remove the trend from the data.

    Returns:
    The root mean square of the values.
    """
    if len(data) == 0:
        return 0
    if isinstance(data, tuple):
        new_data = [x.copy() for x in data]
    elif isinstance(data, list):
        new_data = [data.copy()]
    else:
        raise ValueError("Invalid data type. Must be a list or a tuple of lists.")
    if len(set([len(x) for x in new_data])) != 1:
        raise ValueError("All lists must have the same length.")
    length = len(new_data[0])
    if de_trend:
        new_data = [detrend(x) for x in new_data]
    return (sum([sum([x[i] ** 2 for x in new_data]) for i in range(length)]) / length) ** 0.5


def imu_rms(samples: List[IMUSample], axes: str, de_trend: bool=False) -> Tuple[float, float]:
    """
    Calculate the root mean square of the acceleration and angular velocity components for the specified axes.
    
    Args:
    samples: List of IMU samples.
    axes: String with the axes to calculate the RMS values. Must be a combination of 'x', 'y', and 'z'.
    de_trend: If True, remove the trend from the data.

    Returns:
    Tuple of the root mean square of the acceleration and angular velocity.
    """

    if len(samples) == 0:
        return (0, 0)

    acc_data = []
    gyro_data = []
    if 'x' in axes:
        acc_x = [s.acc_x for s in samples]
        acc_data.append(acc_x)
        gyro_x = [s.gyro_x for s in samples]
        gyro_data.append(gyro_x)
    if 'y' in axes:
        acc_y = [s.acc_y for s in samples]
        acc_data.append(acc_y)
        gyro_y = [s.gyro_y for s in samples]
        gyro_data.append(gyro_y)
    if 'z' in axes:
        acc_z = [s.acc_z for s in samples]
        acc_data.append(acc_z)
        gyro_z = [s.gyro_z for s in samples]
        gyro_data.append(gyro_z)

    rms_acc = rms(tuple(acc_data), de_trend)
    rms_gyro = rms(tuple(gyro_data), de_trend)
    return (rms_acc, rms_gyro)


def running_rms(data: Union[List[float], List[int]], window_size: int, de_trend:bool=False) -> List[float]:
    """
    Calculate the running root mean square of a list of values.
    
    Args:
    data: List of values.
    window_size: Size of the window for the running RMS calculation.
    de_trend: If True, remove the trend from the data.

    Returns:
    List with the running root mean square of the values.
    """
    
    ret = []
    for i in range(len(data)):
        start_idx = max(0, i - window_size)
        stop_idx = min(len(data), i)
        window = data[start_idx:stop_idx]
        if len(window) == 0:
            ret.append(0)
        else:
            ret.append(rms(data[start_idx:stop_idx], de_trend))
    return ret
