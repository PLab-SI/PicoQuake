from typing import List
from random import uniform
import tempfile
from pytest import approx

from picoquake.data import *
from picoquake.configuration import *


def test_device_info():
    device_info = DeviceInfo(
        unique_id="E66368254F89A225",
        firmware="1.0.0")
    
    assert device_info.short_id == "C6E3"


def test_acquisition_data():
    device_info = DeviceInfo(
        unique_id="E66368254F89A225",
        firmware="1.0.0")
    
    config = Config(
        sample_rate=SampleRate.hz_1000,
        filter=Filter.hz_394,
        acc_range=AccRange.g_16,
        gyro_range=GyroRange.dps_2000,
    )

    samples: List[IMUSample] = []
    N = 1000
    for i in range(-N, N):
        samples.append(IMUSample(
            count=i,
            acc_x=uniform(-1, 1),
            acc_y=uniform(-2, 2),
            acc_z=uniform(-3, 3),
            gyro_x=uniform(-100, 100),
            gyro_y=uniform(-200, 200),
            gyro_z=uniform(-300, 300),
        ))

    data = AcquisitionData(
        samples=samples,
        device=device_info,
        config=config,
        start_time=datetime.now())
    
    assert data.num_samples == 2 * N
    assert data.integrity == True
    assert data.duration == approx(2 * N / 1000, 1e-3)
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        path = f.name
        print(path)
        data.csv_path = path
        data.to_csv(path)
        loaded_data = AcquisitionData.from_csv(path)
        assert data == loaded_data

    assert data.samples[0].count == -N
    data.re_centre(0)
    assert data.samples[0].count == 0
    data.re_centre(100)
    assert data.samples[0].count == -100

    data.samples.pop(N)
    assert data.integrity == False
