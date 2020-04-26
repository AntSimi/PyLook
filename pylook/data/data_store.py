import netCDF4
import numpy
import os.path


def handler_access(method):
    def wrapped(self, *args, **kwargs):
        flag = self.open()
        result = method(self, *args, **kwargs)
        if flag:
            self.close()
        return result

    return wrapped


def child_access(method):
    def wrapped(self, *args, **kwargs):
        flag = self.parent.open()
        result = method(self, *args, **kwargs)
        if flag:
            self.parent.close()
        return result

    return wrapped


class DataStore:
    """Class singleton
    """

    instance = None

    def __init__(self):
        if DataStore.instance is None:
            DataStore.instance = DataStore.__DataStore()

    def __str__(self):
        return self.instance.__str__()

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __setattr__(self, name):
        return setattr(self.instance, name)

    def __iter__(self):
        return self.instance.__iter__()

    class __DataStore:

        __slots__ = ("store",)

        def __init__(self):
            self.store = dict()

        def __iter__(self):
            for elt in self.store.values():
                yield elt

        def add_path(self, filename):
            new = NetCDFDataset(filename)
            self.store[new.key] = new
            return new.key

        def add_dataset(self, dataset):
            self.store[dataset.key] = dataset
            return dataset.key

        def add_paths(self, filenames):
            return list(self.add_path(filename) for filename in filenames)

        @property
        def files(self):
            return self.store.keys()

        @property
        def known_extensions(self):
            list_filetype = (
                ("NetCDF", ("*.nc", "*.nc.gz")),
                ("Zarr", ("*.zarr",)),
            )
            return list_filetype

        def __str__(self):
            return self.summary(color_bash=True)

        def summary(self, color_bash=False, full=False):
            elts = list()
            for key, dataset in self.store.items():
                elts.append(dataset.summary(color_bash, full))
            child = "\n".join(elts)
            c = "\033[4;32m" if color_bash else ""
            c_escape = "\033[0;0m" if color_bash else ""
            return f"{c}{len(elts)} dataset(s){c_escape}\n{child}"

        def add_demo_datasets(self):
            self.add_dataset(
                MemoryDataset(
                    "4D_data",
                    MemoryVariable("lon", numpy.arange(20), ("x",)),
                    MemoryVariable("lat", numpy.arange(25), ("y",)),
                    MemoryVariable(
                        "depth", numpy.arange(15), ("d",), attrs=dict(units="m"),
                    ),
                    MemoryVariable(
                        "time", numpy.arange(10), ("t",), attrs=dict(units="day"),
                    ),
                    MemoryVariable(
                        "z", numpy.ones((10, 15, 20, 25)), ("t", "d", "x", "y")
                    ),
                    MemoryVariable("f_depth_time", numpy.ones((10, 15)), ("t", "d")),
                )
            )
            self.add_dataset(
                MemoryDataset(
                    "time_data",
                    MemoryVariable(
                        "time", numpy.arange(10), ("t",), attrs=dict(units="day"),
                    ),
                    MemoryVariable("z", numpy.arange(5, 15), ("t",)),
                )
            )
            self.add_dataset(
                MemoryDataset(
                    "1d_geo_data",
                    MemoryVariable("x", numpy.arange(20)),
                    MemoryVariable("y", numpy.arange(20)),
                    MemoryVariable("z", numpy.arange(5, 25)),
                )
            )
            lon, lat = numpy.meshgrid(numpy.arange(25), numpy.arange(20))
            self.add_dataset(
                MemoryDataset(
                    "2d_geo_data_unregular",
                    MemoryVariable("longitude", lon),
                    MemoryVariable("latitude", lat),
                    MemoryVariable("z", numpy.ones((20, 25))),
                )
            )


class BaseDataset:

    GEO_COORDINATES = set(
        (
            ("longitude", "latitude"),
            ("lon", "lat"),
            ("x", "y"),
            ("xc", "yc"),
            ("nav_lon", "nav_lat"),
            ("nblongitudes", "nblatitudes"),
        )
    )

    GEO_COORDINATES_X = set(i[0] for i in GEO_COORDINATES)
    GEO_COORDINATES_Y = set(i[1] for i in GEO_COORDINATES)

    TIME_COORDINATES = set(("time", "time_ref", "t"))

    DEPTH_COORDINATES = set(("depth",))

    __slots__ = (
        "path",
        "children",
        "attrs",
        "handler",
        "coordinates",
        "key",
    )

    def __init__(self, path):
        self.path = path
        self.handler = None
        self.populate()
        self.find_coordinates_variables()
        self.key = self.genkey()

    def __str__(self):
        return self.summary(True)

    def __iter__(self):
        for child in self.children.values():
            yield child

    def __getitem__(self, item):
        return self.children[item]

    @staticmethod
    def repr_coordinates(values):
        return {",".join(k): v for k, v in values.items()}

    def summary(self, color_bash=False, full=False, child=True):
        if child:
            children = "\n    " + "\n    ".join(
                self.children[i].summary(color_bash, full).replace("\n", "\n    ")
                for i in self.children
            )
        else:
            children = ""
        header = f"\033[4;34m{self.path}\033[0m" if color_bash else self.path
        if full and len(self.attrs):
            keys = list(self.attrs.keys())
            keys.sort()
            attrs = "\n        " + "\n        ".join(
                f"{key} : {self.attrs[key]}" for key in keys
            )
        else:
            attrs = ""
        return f"""{header}
        Time coordinates : {self.repr_coordinates(self.coordinates['time'])}
        Depth coordinates : {self.repr_coordinates(self.coordinates['depth'])}
        Geo coordinates : {self.repr_coordinates(self.coordinates['geo'])}{attrs}{children}"""

    def open(self, *args, **kwargs):
        raise Exception("must be define")

    def populate(self, *args, **kwargs):
        raise Exception("must be define")

    def genkey(self, *args, **kwargs):
        raise Exception("must be define")

    @property
    def last_name(self):
        return os.path.basename(self.path)

    @property
    def dirname(self):
        return os.path.dirname(self.path)

    @property
    def name(self):
        return self.path

    def close(self, *args, **kwargs):
        raise Exception("must be define")

    @property
    def variables(self):
        return self.children.keys()

    @staticmethod
    def clean_name(name):
        return name.lower()

    @staticmethod
    def sort_dims(dim, key, dims):
        dim = frozenset(dim)
        if dim in dims:
            dims[dim].append(key)
        else:
            dims[dim] = [key]

    def format_coordinates(self, coordinates, inverse):
        format_coordinates = dict()
        for i in coordinates:
            if isinstance(i, tuple):
                x_, y_ = inverse[i[0]], inverse[i[1]]
                dims_x, dims_y = (
                    self.children[x_].dimensions,
                    self.children[y_].dimensions,
                )
                self.sort_dims(
                    set(dims_x).union(set(dims_y)), dict(x=x_, y=y_), format_coordinates
                )
            else:
                i_ = inverse[i]
                self.sort_dims(self.children[i_].dimensions, i_, format_coordinates)
        return format_coordinates

    def find_coordinates_variables(self):
        variables = set(self.clean_name(i) for i in self.variables)
        inverse = {self.clean_name(i): i for i in self.variables}
        group_x = variables & self.GEO_COORDINATES_X
        group_y = variables & self.GEO_COORDINATES_Y
        geo_coordinates = (
            set((x, y) for x in group_x for y in group_y) & self.GEO_COORDINATES
        )
        self.coordinates = dict(
            depth=self.format_coordinates(variables & self.DEPTH_COORDINATES, inverse),
            time=self.format_coordinates(variables & self.TIME_COORDINATES, inverse),
            geo=self.format_coordinates(geo_coordinates, inverse),
        )
        for child in self.children.values():
            child.set_coordinates()


class BaseVariable:

    __slots__ = ("name", "parent", "attrs", "coordinates")

    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.attrs = None
        self.populate()

    def populate(self, *args, **kwargs):
        raise Exception("must be define")

    def __str__(self):
        return self.summary(True)

    def summary(self, color_bash=False, full=False):
        if full and len(self.attrs):
            keys = list(self.attrs.keys())
            keys.sort()
            attrs = "\n    " + "\n    ".join(
                f"{key} : {self.attrs[key]}" for key in keys
            )
        else:
            attrs = ""
        coordinates = ""
        c_dim = "\033[0;93m" if color_bash else ""
        c_time = "\033[0;34m" if color_bash else ""
        c_depth = "\033[0;35m" if color_bash else ""
        c_geo = "\033[0;32m" if color_bash else ""
        c_escape = "\033[0;0m" if color_bash else ""
        if self.time_coordinates:
            coordinates += f"{c_time} t: {self.time_coordinates}"
        if self.depth_coordinates:
            coordinates += f"{c_depth} d: {self.depth_coordinates}"
        if self.geo_coordinates:
            coordinates += f"{c_geo} g: {self.geo_coordinates} -> {self.geo_datatype}"
        return f"{self.name}{c_dim}{self.dimensions}{coordinates}{c_escape}{attrs}"

    @property
    def handler(self):
        raise Exception("must be define")

    @property
    def dimensions(self):
        raise Exception("must be define")

    def set_coordinates(self):
        self.coordinates = dict()
        t_dims = self.parent.coordinates["time"]
        d_dims = self.parent.coordinates["depth"]
        g_dims = self.parent.coordinates["geo"]
        dims = frozenset(self.dimensions)
        if t_dims:
            for available_dims, value in t_dims.items():
                if available_dims.issubset(dims):
                    self.coordinates["time"] = value
                    break
        if d_dims:
            for available_dims, value in d_dims.items():
                if available_dims.issubset(dims):
                    self.coordinates["depth"] = value
                    break
        if g_dims:
            dims = frozenset(self.dimensions)
            for available_dims, value in g_dims.items():
                if available_dims.issubset(dims):
                    self.coordinates["geo"] = value
                    break

    @property
    def time_coordinates(self):
        return self.coordinates.get("time", [None])[0]

    @property
    def depth_coordinates(self):
        return self.coordinates.get("depth", [None])[0]

    @property
    def geo_coordinates(self):
        return self.coordinates.get("geo", [None])[0]

    @property
    def geo_datatype(self):
        g_coord = self.geo_coordinates
        if g_coord:
            dims_coord = {k: self.parent[v].dimensions for k, v in g_coord.items()}
            if dims_coord["x"] != dims_coord["y"]:
                return "2D"
            if dims_coord["x"] == dims_coord["y"] and len(dims_coord["x"]) == 1:
                return "1D"
            return "2DU"


class NetCDFDataset(BaseDataset):

    __slots__ = tuple()

    def open(self):
        if self.handler is None:
            self.handler = netCDF4.Dataset(self.path)
            return True
        return False

    def genkey(self):
        return self.path

    def close(self):
        self.handler.close()
        self.handler = None

    @handler_access
    def populate(self):
        self.children = {
            elt: NetCDFVariable(elt, self) for elt in self.handler.variables
        }
        self.attrs = {k: getattr(self.handler, k) for k in self.handler.ncattrs()}
        self.attrs["__dimensions"] = {
            k: v.size for k, v in self.handler.dimensions.items()
        }


class NetCDFVariable(BaseVariable):

    __slots__ = tuple()

    @property
    @child_access
    def handler(self):
        return self.parent.handler.variables[self.name]

    @child_access
    def populate(self):
        self.attrs = {k: getattr(self.handler, k) for k in self.handler.ncattrs()}
        self.attrs["__store_dtype"] = self.handler.dtype
        self.attrs["__chunking"] = self.handler.chunking()
        filters = self.handler.filters()
        if filters is not None:
            self.attrs["__zlib"] = filters["zlib"]
        self.attrs["__dimensions"] = self.handler.dimensions
        # I don't know how to know output dtype without try to access at the data
        # self.attrs['output_dtype'] = self.attrs['store_dtype']

    @property
    def dimensions(self):
        return self.attrs["__dimensions"]


class MemoryDataset(BaseDataset):
    __slots__ = tuple()

    def __init__(self, key, *args, **kwargs):
        self.key = key
        self.path = key
        self.attrs = dict()
        self.populate(*args, **kwargs)
        self.find_coordinates_variables()

    def populate(self, *args, **kwargs):
        if len(args) == 0:
            self.children = {
                k: MemoryVariable(k, v, parent=self) for k, v in kwargs.items()
            }
        else:
            self.children = dict()
            for variable in args:
                self.children[variable.name] = variable
                variable.parent = self


class MemoryVariable(BaseVariable):

    __slots__ = ("value",)

    def __init__(self, name, value, dimensions=None, parent=None, attrs=None):
        self.name = name
        self.parent = parent
        self.value = value
        self.attrs = dict() if attrs is None else attrs
        self.attrs["__dimensions"] = (
            set(str(i) for i in value.shape) if dimensions is None else dimensions
        )

    @property
    def dimensions(self):
        return self.attrs["__dimensions"]


class ZarrDataset(BaseDataset):
    __slots__ = tuple()


class ZarrVariable(BaseVariable):

    __slots__ = tuple()
