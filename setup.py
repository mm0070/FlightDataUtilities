from setuptools import setup, Extension
import numpy as np


setup(
    use_scm_version={'fallback_version': '19.0.0'},
    data_files=[('', ['flightdatautilities/array.pxd'])],
    ext_modules=[
        Extension(
            'flightdatautilities.array', ['flightdatautilities/array.pyx'],
            include_dirs=[np.get_include()],
        ),
    ],
)
