from setuptools import setup
from setuptools import find_packages

setup(
    name='radar_tools',
    version='0.0.1',
    description='Python interface to manipulate radar data',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'bufrtogeotiff = radar_tools.scripts.bufrtogeotiff:main',
        ],
    },
)
