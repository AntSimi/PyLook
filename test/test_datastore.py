import numpy as np
from pylook.data.data_store import DataStore, MemoryDataset as MD, MemoryVariable as MV
from glob import glob


d = DataStore()
# d.add_paths(glob("../py-eddy-tracker/share/*.nc"))
d.add_dataset(
    MD(
        key="2D_data_quick",
        x=np.arange(20),
        y=np.arange(30),
        z=np.ones((20, 30)),
        time=np.arange(5),
        no_geo=np.arange(5),
        misc=np.arange(4),
    )
)
d.add_dataset(
    MD(
        "1D_data_1Hz_20Hz_name_with_extension",
        MV("lon_1hz", np.arange(20), dimensions=("1hz",)),
        MV("lat_1hz", np.arange(20), dimensions=("1hz",)),
        MV("lon_10hz", np.arange(20, 0.1), dimensions=("10hz",)),
        MV("lat_10hz", np.arange(20, 0.1), dimensions=("10hz",)),
        MV("z_10hz", np.arange(20, 0.1) * 5, dimensions=("10hz",)),
        MV("z_1hz", np.arange(20) * 5, dimensions=("1hz",)),
    )
)
d.add_dataset(
    MD(
        "2D_data_fully_specified",
        MV("x", np.arange(20), dimensions=("x",), attrs=dict(units="degrees_east")),
        MV("Y", np.arange(20), dimensions=("y",), attrs=dict(units="degrees_west")),
        MV(
            "z",
            np.outer(np.arange(20), np.ones(20)),
            dimensions=("y", "x"),
            attrs=dict(units="m"),
        ),
        MV("lon", np.arange(20), dimensions=("a",), attrs=dict(units="degrees_east")),
        MV("lat", np.arange(50), dimensions=("b",), attrs=dict(units="degrees_west")),
        MV(
            "grad",
            np.outer(np.arange(20), np.ones(50)),
            dimensions=("a", "b"),
            attrs=dict(units="m"),
        ),
        MV(
            "grad_bad_dim",
            np.outer(np.arange(20), np.ones(50)),
            dimensions=("x", "b"),
            attrs=dict(units="m"),
        ),
    )
)
d.add_dataset(
    MD(
        "2D_data_coordinates_wrong_name",
        MV("x", np.arange(20), dimensions=("x",), attrs=dict(units="degrees_east")),
        MV("lat", np.arange(20), dimensions=("y",), attrs=dict(units="degrees_west")),
        MV(
            "z",
            np.outer(np.arange(20), np.ones(20)),
            dimensions=("y", "x"),
            attrs=dict(units="m"),
        ),
    )
)
d.add_dataset(
    MD(
        "2D_data_unstruct",
        MV("lon", np.arange(20).repeat(20).reshape(20, 20), dimensions=("x", "y")),
        MV("lat", np.arange(20).repeat(20).reshape(20, 20), dimensions=("y", "x")),
        MV("z", np.outer(np.arange(20), np.ones(20)), dimensions=("y", "x"),),
    )
)
d.add_dataset(
    MD(
        "4D_data",
        MV(
            "Longitude",
            np.arange(20),
            dimensions=("longitude",),
            attrs=dict(units="degrees_east"),
        ),
        MV(
            "Latitude",
            np.arange(25),
            dimensions=("latitude",),
            attrs=dict(units="degrees_north"),
        ),
        MV("Depth", np.arange(15), dimensions=("depth",), attrs=dict(units="m")),
        MV("time", np.arange(10), dimensions=("time",), attrs=dict(units="day")),
        MV("time_ref", np.arange(10), dimensions=("time",), attrs=dict(units="day")),
        MV("t", np.arange(10), dimensions=("time_bis",), attrs=dict(units="day")),
        MV(
            "z",
            np.ones((10, 15, 20, 25)),
            dimensions=("time", "depth", "longitude", "latitude"),
            attrs=dict(units="m"),
        ),
    )
)
print(d)
