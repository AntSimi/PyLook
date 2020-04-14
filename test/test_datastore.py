import numpy
from pylook.data.data_store import DataStore, MemoryDataset, MemoryVariable
from glob import glob

d = DataStore()
d.add_paths(glob("../py-eddy-tracker/share/*.nc"))
d.add_dataset(
    MemoryDataset(
        key="2D_data", x=numpy.arange(20), y=numpy.arange(30), z=numpy.ones((20, 30))
    )
)
d.add_dataset(
    MemoryDataset(
        "2D_data_fully_specified",
        MemoryVariable(
            "x", numpy.arange(20), dimensions=("x",), attrs=dict(units="degrees_east")
        ),
        MemoryVariable(
            "y", numpy.arange(20), dimensions=("y",), attrs=dict(units="degrees_west")
        ),
        MemoryVariable(
            "z",
            numpy.outer(numpy.arange(20), numpy.ones(20)),
            dimensions=("y", "x"),
            attrs=dict(units="m"),
        ),
        MemoryVariable(
            "lon", numpy.arange(20), dimensions=("a",), attrs=dict(units="degrees_east")
        ),
        MemoryVariable(
            "lat", numpy.arange(50), dimensions=("b",), attrs=dict(units="degrees_west")
        ),
        MemoryVariable(
            "grad",
            numpy.outer(numpy.arange(20), numpy.ones(50)),
            dimensions=("a", "b"),
            attrs=dict(units="m"),
        ),
    )
)
d.add_dataset(
    MemoryDataset(
        "2D_data_coordinates_wrong_name",
        MemoryVariable(
            "x", numpy.arange(20), dimensions=("x",), attrs=dict(units="degrees_east")
        ),
        MemoryVariable(
            "lat", numpy.arange(20), dimensions=("y",), attrs=dict(units="degrees_west")
        ),
        MemoryVariable(
            "z",
            numpy.outer(numpy.arange(20), numpy.ones(20)),
            dimensions=("y", "x"),
            attrs=dict(units="m"),
        ),
    )
)
d.add_dataset(
    MemoryDataset(
        "4D_data",
        MemoryVariable(
            "longitude",
            numpy.arange(20),
            dimensions=("longitude",),
            attrs=dict(units="degrees_east"),
        ),
        MemoryVariable(
            "latitude",
            numpy.arange(25),
            dimensions=("latitude",),
            attrs=dict(units="degrees_north"),
        ),
        MemoryVariable(
            "depth", numpy.arange(15), dimensions=("depth",), attrs=dict(units="m")
        ),
        MemoryVariable(
            "time", numpy.arange(10), dimensions=("time",), attrs=dict(units="day")
        ),
        MemoryVariable(
            "z",
            numpy.ones((10, 15, 20, 25)),
            dimensions=("time", "depth", "longitude", "latitude"),
            attrs=dict(units="m"),
        ),
    )
)

print(d)
# print(d.summary(color_bash=True, full=True))
