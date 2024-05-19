from setuptools import setup, find_packages

setup(
    name='picoquake',
    version='1.0.0',
    description='Data acquisition from a PicoQuake device.',
    python_requires=">=3.9",
    packages=find_packages(),
    install_requires=[
        'pyserial',
        'protobuf',
        'cobs',
        'psutil'
    ],
    extras_require={
        'plot': ['numpy', 'scipy', 'matplotlib'],
    },
    entry_points={
        'console_scripts': [
            'picoquake=picoquake.cli:main',
        ],
    },
)
