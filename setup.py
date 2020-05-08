#!/usr/bin/env python
from setuptools import setup, find_packages

min_version = (3, 7)

setup(
    name="pylook",
    version="0.0",
    description="Python Distribution Utilities",
    author="Antoine Delepoulle",
    author_email="delepoulle.a@gmail.com",
    packages=find_packages(),
    install_requires=["numpy", "matplotlib", "netCDF4", "pyproj", "numba", "zarr", 'PyQt5'],
    python_requires=f'>={".".join(str(i) for i in min_version)}',
    package_data={"pylook": ["gshhs_backup/*.nc"]},
    entry_points=dict(
        console_scripts=[
            "PyLook = pylook.appli:pylook",
            "DHeader = pylook.appli:data_header",
            "DataLook = pylook.data_look:data_look",
        ]
    ),
)
