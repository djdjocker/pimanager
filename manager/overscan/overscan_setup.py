from distutils.core import setup, Extension

# usage 
#     python overscan_setup.py build_ext --inplace
#     import overscan
#     [top, bottom, left, right] = overscan.get()
#     [top, bottom, left, right] = overscan.set([top, bottom, left, right])

# define the extension module
overscan = Extension('overscan', sources=['overscan.c'])

# run the setup
setup(ext_modules=[overscan])
