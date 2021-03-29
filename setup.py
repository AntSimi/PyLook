#!/usr/bin/env python
from setuptools import setup, find_packages
import versioneer

min_version = (3, 7)

setup(
    name="pylook-map",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Python Distribution Utilities",
    author="Antoine Delepoulle",
    author_email="delepoulle.a@gmail.com",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "matplotlib",
        "netCDF4",
        "pyproj",
        "numba",
        "zarr"
    ],
    python_requires=f'>={".".join(str(i) for i in min_version)}',
    package_data={"pylook": ["gshhs_backup/*.nc"]},
    entry_points=dict(
        console_scripts=[
            "PyLook = pylook.appli.pylook:pylook",
            "DHeader = pylook.appli.data_header:data_header",
            "DataLook = pylook.appli.data_look:data_look",
        ]
    ),
)
