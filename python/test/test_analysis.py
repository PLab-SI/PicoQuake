from pytest import approx
import numpy as np

from picoquake.data import IMUSample
from picoquake.analysis import *


def test_mean():
    data = [1., 2., 3., 4., 5.]
    assert approx(mean(data), 1e-3) == 3.0

    data = [1., 1., 1., 1., 1.]
    assert approx(mean(data), 1e-3) == 1.0

    data = [0., 0., 0., 0., 0.]
    assert approx(mean(data), 1e-3) == 0.0

    data = [0.]
    assert approx(mean(data), 1e-3) == 0.0

    data = [np.sin(2 * np.pi * i / 120) for i in range(1200)]
    assert approx(mean(data), 1e-3) == 0.0

    data = [5 * np.sin(2 * np.pi * i / 120) for i in range(1200)]
    assert approx(mean(data), 1e-3) == 0.0
    
    data = [5 * np.sin(2 * np.pi * i / 120) + 3.0 for i in range(1200)]
    assert approx(mean(data), 1e-3) == 3.0

    assert mean([]) == 0


def test_detrend():
    data = [1, 2, 3, 4, 5]
    expected = [-2, -1, 0, 1, 2]
    assert detrend(data) == expected

    data = [10, 20, 30, 40, 50]
    expected = [-20, -10, 0, 10, 20]
    assert detrend(data) == expected

    data = [5, 5, 5, 5, 5]
    expected = [0, 0, 0, 0, 0]
    assert detrend(data) == expected

    data = [-1, 0, 1]
    expected = [-1, 0, 1]
    assert detrend(data) == expected

    assert detrend([]) == []


def test_rms():
    data = [1., 2., 3., 4., 5.]
    assert approx(rms(data), 1e-3) == np.sqrt(np.sum(np.square(data)) / 5)
    data_dtr = np.array(data) - np.mean(data)
    assert approx(rms(data, de_trend=True), 1e-3) == np.sqrt(np.sum(np.square(data_dtr)) / 5)

    data = [1, 2, 3]
    assert approx(rms(data), 1e-3) == np.sqrt(np.sum(np.square(data)) / 3)
    data_dtr = np.array(data) - np.mean(data)
    assert approx(rms(data, de_trend=True), 1e-3) == np.sqrt(np.sum(np.square(data_dtr)) / 3)

    data = [1., 1., 1., 1., 1.]
    assert approx(rms(data), 1e-3) == 1.0

    data = [0., 0., 0., 0., 0.]
    assert approx(rms(data), 1e-3) == 0.0

    data = [0.]
    assert approx(rms(data), 1e-3) == 0.0

    data = [np.sin(2 * np.pi * i / 120) for i in range(1200)]
    assert approx(rms(data), 1e-3) == 0.707
    assert approx(rms(data[:120]), 1e-3) == 0.707
    assert approx(rms(data[:60]), 1e-3) == 0.707

    data = [5 * np.sin(2 * np.pi * i / 120) for i in range(1200)]
    assert approx(rms(data), 1e-3) == 5 * 0.707
    assert approx(rms(data[:120]), 1e-3) == 5 * 0.707

    assert rms([]) == 0

    data = ([1., 2., 3., 4., 5.], [1., 2., 3., 4., 5.])
    assert approx(rms(data), 1e-3) == 4.69
    assert approx(rms(data, de_trend=True), 1e-3) == 2.0


def test_imu_rms():
    pass
    samples = [
        IMUSample(0, 1, 2, 5, 8, 1, 4),
        IMUSample(1, 2, 3, 6, 9, 2, 5),
        IMUSample(2, 3, 4, 7, 0, 3, 6),
    ]

    # Test for all axes
    acc_rms, gyro_rms = imu_rms(samples, 'xyz')
    ex_acc_sum = (1 ** 2 + 2 ** 2 + 5 ** 2) + (2 ** 2 + 3 ** 2 + 6 ** 2) + (3 ** 2 + 4 ** 2 + 7 ** 2)
    ex_acc_rms = (ex_acc_sum / 3) ** 0.5
    assert approx(acc_rms, 1e-3) == ex_acc_rms
    ex_gyro_sum = (8 ** 2 + 1 ** 2 + 4 ** 2) + (9 ** 2 + 2 ** 2 + 5 ** 2) + (0 ** 2 + 3 ** 2 + 6 ** 2)
    ex_gyro_rms = (ex_gyro_sum / 3) ** 0.5
    assert approx(gyro_rms, 1e-3) == ex_gyro_rms
    
    acc_rms, gyro_rms = imu_rms(samples, 'xyz', de_trend=True)
    acc_x = np.array([1, 2, 3])
    acc_x = acc_x - np.mean(acc_x)
    acc_y = np.array([2, 3, 4])
    acc_y = acc_y - np.mean(acc_y)
    acc_z = np.array([5, 6, 7])
    acc_z = acc_z - np.mean(acc_z)
    ex_acc_rms = np.sqrt(sum([sum([x[i] ** 2 for x in [acc_x, acc_y, acc_z]]) for i in range(3)]) / 3)
    assert approx(acc_rms, 1e-3) == ex_acc_rms
    gyro_x = np.array([8, 9, 0])
    gyro_x = gyro_x - np.mean(gyro_x)
    gyro_y = np.array([1, 2, 3])
    gyro_y = gyro_y - np.mean(gyro_y)
    gyro_z = np.array([4, 5, 6])
    gyro_z = gyro_z - np.mean(gyro_z)
    ex_gyro_rms = np.sqrt(sum([sum([x[i] ** 2 for x in [gyro_x, gyro_y, gyro_z]]) for i in range(3)]) / 3)
    assert approx(gyro_rms, 1e-3) == ex_gyro_rms

    # Test for x axis only
    acc_rms, gyro_rms = imu_rms(samples, 'x')
    ex_acc_sum = (1 ** 2) + (2 ** 2) + (3 ** 2)
    ex_acc_rms = (ex_acc_sum / 3) ** 0.5
    assert approx(acc_rms, 1e-3) == ex_acc_rms
    ex_gyro_sum = (8 ** 2) + (9 ** 2) + (0 ** 2)
    ex_gyro_rms = (ex_gyro_sum / 3) ** 0.5
    assert approx(gyro_rms, 1e-3) == ex_gyro_rms

    # Test for y axis only
    acc_rms, gyro_rms = imu_rms(samples, 'y')
    ex_acc_sum = (2 ** 2) + (3 ** 2) + (4 ** 2)
    ex_acc_rms = (ex_acc_sum / 3) ** 0.5
    assert approx(acc_rms, 1e-3) == ex_acc_rms
    ex_gyro_sum = (1 ** 2) + (2 ** 2) + (3 ** 2)
    ex_gyro_rms = (ex_gyro_sum / 3) ** 0.5
    assert approx(gyro_rms, 1e-3) == ex_gyro_rms

    # Test for z axis only
    acc_rms, gyro_rms = imu_rms(samples, 'z')
    ex_acc_sum = (5 ** 2) + (6 ** 2) + (7 ** 2)
    ex_acc_rms = (ex_acc_sum / 3) ** 0.5
    assert approx(acc_rms, 1e-3) == ex_acc_rms
    ex_gyro_sum = (4 ** 2) + (5 ** 2) + (6 ** 2)
    ex_gyro_rms = (ex_gyro_sum / 3) ** 0.5
    assert approx(gyro_rms, 1e-3) == ex_gyro_rms

    assert imu_rms([], 'xyz') == (0, 0)

def test_running_rms():
    sine_1 = [np.sin(np.pi * i / 10) for i in range(100)]
    sine_2 = [2 * np.sin(np.pi * i / 10) for i in range(100)]
    sine_3 = [3 * np.sin(np.pi * i / 10) for i in range(100)]
    sine = np.concatenate([sine_1, sine_2, sine_3]).tolist()
    rms_values = running_rms(sine, 4)
    assert approx(rms_values[0], 1e-3) == 0.0
    assert approx(rms_values[20], 1e-3) == 0.707
    assert approx(rms_values[120], 1e-3) == 2 * 0.707
    assert approx(rms_values[220], 1e-3) == 3 * 0.707

    assert running_rms([], 10) == []
