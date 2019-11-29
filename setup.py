from pathlib import Path
import sys

import numpy as np
import setuptools


filenames = set()
index = sys.argv.index('build_ext')
if index:
    index += 1
    while index <= len(sys.argv) - 2:
        if sys.argv[index] == '--filename':
            filenames.add(sys.argv[index + 1])
            sys.argv[index:index + 2] = []
        else:
            index += 1


setuptools.setup(
    use_scm_version={'fallback_version': '19.0.0'},
    data_files=[('', [path.as_posix() for path in Path().glob('**/*.pxd')])],
    ext_modules=[setuptools.Extension('.'.join(path.parent.parts + (path.stem,)), [path.as_posix()],
                                      define_macros=[('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION')],
                                      include_dirs=[np.get_include()]) for path in Path().glob('**/*.pyx')
                 if not filenames or path.name in filenames],
)
