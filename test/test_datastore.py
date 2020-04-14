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
        MemoryVariable("x", numpy.arange(20), attrs=dict(units="m")),
    )
)

print(d)
# print(d.summary(color_bash=True, full=True))
