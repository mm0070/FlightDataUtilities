from pathlib import Path

import numpy as np
import setuptools

setuptools.setup(
    data_files=[('', [path.as_posix() for path in Path().glob('**/*.pxd')])],
    ext_modules=[setuptools.Extension('.'.join(path.parent.parts + (path.stem,)), [path.as_posix()],
                                      define_macros=[('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION')],
                                      include_dirs=[np.get_include()]) for path in Path().glob('**/*.pyx')],
    use_scm_version={'fallback_version': '19.0.0'},
)
