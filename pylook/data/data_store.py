import netCDF4
import numpy


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

    class __DataStore:

        __slots__ = ("store",)

        def __init__(self):
            self.store = dict()

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
            if color_bash:
                return f"\033[4;32m{len(elts)} dataset(s)\033[0m\n{child}"
            else:
                return f"{len(elts)} dataset(s)\n{child}"


class BaseDataset:

    CLASSIC_GEO_COORDINATES = set(
        (
            ("longitude", "latitude"),
            ("lon", "lat"),
            ("x", "y"),
            ("xc", "yc"),
            ("nav_lon", "nav_lat"),
            ("nblongitudes", "nblatitudes"),
        )
    )

    CLASSIC_GEO_COORDINATES_X = set(i[0] for i in CLASSIC_GEO_COORDINATES)
    CLASSIC_GEO_COORDINATES_Y = set(i[1] for i in CLASSIC_GEO_COORDINATES)

    CLASSIC_TIME_COORDINATES = set(("time", "time_ref",))

    CLASSIC_DEPTH_COORDINATES = set(("depth",))

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

    def summary(self, color_bash=False, full=False):
        children = "\n    ".join(
            self.children[i].summary(color_bash, full).replace("\n", "\n    ")
            for i in self.children
        )
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
        Time coordinates : {self.coordinates['time']}
        Depth coordinates : {self.coordinates['depth']}
        Geo coordinates : {self.coordinates['geo']}{attrs}
    {children}"""

    def open(self):
        raise Exception("must be define")

    def populate(self):
        raise Exception("must be define")

    def genkey(self):
        raise Exception("must be define")

    def close(self):
        raise Exception("must be define")

    @property
    def variables(self):
        return self.children.keys()

    def find_coordinates_variables(self):
        variables = set(i.lower() for i in self.variables)
        self.coordinates = dict(
            depth=variables & self.CLASSIC_DEPTH_COORDINATES,
            time=variables & self.CLASSIC_TIME_COORDINATES,
            geo=(
                variables & self.CLASSIC_GEO_COORDINATES_X,
                variables & self.CLASSIC_GEO_COORDINATES_Y,
            ),
        )


class BaseVariable:

    __slots__ = ("name", "parent", "attrs")

    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.attrs = None
        self.populate()

    def populate(self):
        raise Exception("must be define")

    def __str__(self):
        return summary(True)

    def summary(self, color_bash=False, full=False):
        if full and len(self.attrs):
            keys = list(self.attrs.keys())
            keys.sort()
            attrs = "\n    " + "\n    ".join(
                f"{key} : {self.attrs[key]}" for key in keys
            )
        else:
            attrs = ""
        if color_bash:
            return f"{self.name}\033[0;93m{self.dimensions}\033[0m{attrs}"
        else:
            return f"{self.name}{self.dimensions}{attrs}"

    @property
    def handler(self):
        raise Exception("must be define")

    @property
    def dimensions(self):
        raise Exception("must be define")


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
            self.children = {k: MemoryVariable(k, v, parent=self) for k, v in kwargs.items()}
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
        self.attrs['__dimensions'] = value.shape if dimensions is None else dimensions

    @property
    def dimensions(self):
        return self.attrs['__dimensions']


class ZarrDataset(BaseDataset):
    __slots__ = tuple()


class ZarrVariable(BaseVariable):

    __slots__ = tuple()
