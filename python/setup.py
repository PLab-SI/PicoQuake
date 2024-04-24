from setuptools import setup, find_packages

setup(
    name='picoquake',
    version='1.0.0',
    description='Data acquisition from a PicoQuake device.',
    packages=find_packages(),
    install_requires=[
        'pyserial',
        'protobuf',
        'cobs',
        'numpy',
        'matplotlib',
        'psutil'
    ],
    entry_points={
        'console_scripts': [
            'picoquake=picoquake.cli:main',
        ],
    },
)
