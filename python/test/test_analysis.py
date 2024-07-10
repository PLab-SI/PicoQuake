from pytest import approx

from picoquake.data import IMUSample
from picoquake.analisys import *

def test_rms():
    samples = [
        IMUSample(0, 1, 2, 3, 4, 5, 6),
        IMUSample(1, 1, 2, 3, 4, 5, 6),
        IMUSample(2, 1, 2, 3, 4, 5, 6),
    ]

    # Test for all axes
    acc_rms, gyro_rms = rms(samples, 'xyz')
    assert approx(acc_rms, 1e-3) == 3.7417
    assert approx(gyro_rms, 1e-3) == 8.775

    # Test for x axis only
    acc_rms, gyro_rms = rms(samples, 'x')
    assert approx(acc_rms, 1e-3) == 1.0
    assert approx(gyro_rms, 1e-3) == 4.0

    # Test for y axis only
    acc_rms, gyro_rms = rms(samples, 'y')
    assert approx(acc_rms, 1e-3) == 2.0
    assert approx(gyro_rms, 1e-3) == 5.0

    # Test for z axis only
    acc_rms, gyro_rms = rms(samples, 'z')
    assert approx(acc_rms, 1e-3) == 3.0
    assert approx(gyro_rms, 1e-3) == 6.0
    