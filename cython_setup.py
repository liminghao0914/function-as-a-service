from distutils.core import setup
from Cython.Build import cythonize

# setup(ext_modules = cythonize('hybrid_policy_c.pyx'))
setup(ext_modules = cythonize('generator_c.pyx'))