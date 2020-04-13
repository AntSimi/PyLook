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

        def add_file(self, filename):
            self.store[filename] = NetCDFDataset(filename)

        def add_files(self, filenames):
            for filename in filenames:
                self.add_file(filename)

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
            elts = list()
            for key, dataset in self.store.items():
                elts.append(dataset.__str__())
            return "\n".join(elts)

        def summary(self, color_bash=False):
            elts = list()
            for key, dataset in self.store.items():
                elts.append(dataset.summary(color_bash))
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

    CLASSIC_TIME_COORDINATES = set(("time", "time_ref",))

    CLASSIC_DEPTH_COORDINATES = set(("depth",))

    __slots__ = (
        "path",
        "children",
        "attrs",
        "handler",
        "coordinates",
    )

    def __init__(self, path):
        self.path = path
        self.handler = None
        self.children = None
        self.attrs = None
        self.coordinates = None
        self.populate()
        self.find_coordinates_variables()

    def __str__(self):
        children = "\n\t".join(
            str(self.children[i]).replace("\n", "\n\t") for i in self.children
        )
        keys = list(self.attrs.keys())
        keys.sort()
        attrs = "\n\t\t".join(f"{key} : {self.attrs[key]}" for key in keys)
        return f"{self.path}\n\t\t{attrs}\n\t{children}"

    def summary(self, color_bash=False):
        children = "\n\t".join(
            self.children[i].summary(color_bash) for i in self.children
        )
        if color_bash:
            return f"\033[4;34m{self.path}\033[0m\n\t{children}"
        else:
            return f"{self.path}\n\t{children}"

    def open(self):
        raise Exception("must be define")

    def populate(self):
        raise Exception("must be define")

    def close(self):
        raise Exception("must be define")

    @property
    def variables(self):
        return self.children.keys()

    def find_coordinates_variables(self):
        variables = set(self.variables)
        self.coordinates = dict(
            depth=variables & self.CLASSIC_DEPTH_COORDINATES,
            time=variables & self.CLASSIC_TIME_COORDINATES,
        )
        print(self.CLASSIC_GEO_COORDINATES)
        print(variables)
        self.coordinates["geo"] = None


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
        keys = list(self.attrs.keys())
        keys.sort()
        attrs = "\n\t".join(f"{key} : {self.attrs[key]}" for key in keys)
        return f"{self.name}\n\t{attrs}"

    def summary(self, color_bash):
        if color_bash:
            return f"{self.name}\033[0;93m{self.dimensions}\033[0m"
        else:
            return f"{self.name}{self.dimensions}"

    @property
    def handler(self):
        return Exception("must be define")

    @property
    def dimensions(self):
        return Exception("must be define")


class NetCDFDataset(BaseDataset):

    __slots__ = tuple()

    def open(self):
        if self.handler is None:
            self.handler = netCDF4.Dataset(self.path)
            return True
        return False

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

