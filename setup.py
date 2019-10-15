from pathlib import Path
from setuptools import setup, Extension

import numpy as np


setup(
    use_scm_version={'fallback_version': '19.0.0'},
    data_files=[('', [path.as_posix() for path in Path().glob('**/*.pxd')])],
    ext_modules=[
        Extension('.'.join(path.parent.parts + (path.stem,)), [path.as_posix()],
                  define_macros=[('CYTHON_TRACE_NOGIL', '1'), ('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION')],
                  include_dirs=[np.get_include()]) for path in Path().glob('**/*.pyx')],
)
