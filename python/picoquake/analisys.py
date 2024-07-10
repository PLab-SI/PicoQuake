"""
This module implements various data analysis functions.
"""

from typing import List, Tuple

from .data import IMUSample


# def rms(samples: List[IMUSample]) -> Tuple[float, float, float, float, float, float]:
#     """
#     Calculate the root mean square of the acceleration and angular velocity components.
    
#     Args:
#     samples: List of IMU samples.
    
#     Returns:
#     Tuple of the root mean square of the acceleration and angular velocity components in the order:
#     (rms_ax, rms_ay, rms_az, rms_gx, rms_gy, rms_gz)
#     """
#     rms_ax = (sum([sample.acc_x ** 2 for sample in samples]) / len(samples)) ** 0.5
#     rms_ay = (sum([sample.acc_y ** 2 for sample in samples]) / len(samples)) ** 0.5
#     rms_az = (sum([sample.acc_z ** 2 for sample in samples]) / len(samples)) ** 0.5
#     rms_gx = (sum([sample.gyro_x ** 2 for sample in samples]) / len(samples)) ** 0.5
#     rms_gy = (sum([sample.gyro_y ** 2 for sample in samples]) / len(samples)) ** 0.5
#     rms_gz = (sum([sample.gyro_z ** 2 for sample in samples]) / len(samples)) ** 0.5
#     return (rms_ax, rms_ay, rms_az, rms_gx, rms_gy, rms_gz)

# def rms_combined(samples: List[IMUSample]) -> Tuple[float, float]:
#     """
#     Calculate the root mean square of the combined acceleration and angular velocity components.
    
#     Args:
#     samples: List of IMU samples.

#     Returns:
#     Tuple of the root mean square of the combined acceleration and angular velocity components in the order:
#     (rms_a, rms_g)
#     """
#     rms_a = (sum([sample.acc_x ** 2 + sample.acc_y ** 2 + sample.acc_z ** 2 for sample in samples]) / len(samples)) ** 0.5
#     rms_g = (sum([sample.gyro_x ** 2 + sample.gyro_y ** 2 + sample.gyro_z ** 2 for sample in samples]) / len(samples)) ** 0.5
#     return (rms_a, rms_g)

def rms(samples: List[IMUSample], axes: str) -> Tuple[float, float]:
    """
    Calculate the root mean square of the acceleration and angular velocity components for the specified axes.
    
    Args:
    samples: List of IMU samples.
    axes: String with the axes to calculate the RMS values. Must be a combination of 'x', 'y', and 'z'.

    Returns:
    Tuple of the root mean square of the acceleration and angular velocity.
    """

    x = int('x' in axes)
    y = int('y' in axes)
    z = int('z' in axes)

    rms_acc = (sum([sample.acc_x ** 2 * x + sample.acc_y ** 2 * y + sample.acc_z ** 2 * z for sample in samples]) / len(samples)) ** 0.5
    rms_gyro = (sum([sample.gyro_x ** 2 * x + sample.gyro_y ** 2 * y + sample.gyro_z ** 2 * z for sample in samples]) / len(samples)) ** 0.5
    return (rms_acc, rms_gyro)