#!/usr/bin/env python
from setuptools import setup

min_version = (3, 7)

setup(name='pylook',
      version='0.0',
      description='Python Distribution Utilities',
      author='Antoine Delepoulle',
      author_email='delepoulle.a@gmail.com',
      packages=['pylook'],
      install_requires=[
            'numpy',
            'matplotlib',
            'netCDF4',
            'pyproj',
            'numba',
      ],
      python_requires=f'>={".".join(str(i) for i in min_version)}'
      )