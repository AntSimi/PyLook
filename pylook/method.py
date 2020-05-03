import matplotlib.axes as maxes
from .exchange_object import Method


class Base:
    __slots__ = (
        "_name",
        "data_accept",
        "help",
        "data_need",
        "legend_available",
        "options",
    )

    DATA_LEVEL = {"1D": 10, "2DU": 20, "2D": 30}

    def __init__(self):
        self._name = "noname"
        self.legend_available = list()
        self.data_accept = None
        self.data_need = dict()
        self.options = dict()
        self.help = dict()
        self.setup()

    @classmethod
    def func(cls, *args, **kwargs):
        raise Exception(f"Must be define in {cls.__name__}")

    @classmethod
    def setup(cls):
        raise Exception(f"Must be define in {cls.__name__}")

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, state):
        self._name = state

    def enable_datas(self, datatype):
        self.data_accept = self.DATA_LEVEL[datatype]

    def needs(self, **kwargs):
        self.data_need.update(kwargs)

    def set_options(self, **kwargs):
        self.options.update(kwargs)

    # def __call__(self, *args, **kwargs):
    #     return self

    def exchange_object(self):
        return Method.with_options(self.options)


class Pcolormesh(Base):
    __slots__ = tuple()

    def setup(self):
        self.name = "pcolormesh_plk"
        self.enable_datas("2D")
        self.needs(x="", y="", z="")
        self.set_options(vmin="None", vmax="None", cmap="'jet'")

    @staticmethod
    def func(ax, *args, **kwargs):
        maxes.Axes.pcolormesh(ax, *args, **kwargs)


class Pcolor(Base):
    __slots__ = tuple()

    def setup(self):
        self.name = "pcolor_plk"
        self.enable_datas("2DU")
        self.needs(x="", y="", z="")
        self.set_options(vmin="None", vmax="None", cmap="'jet'")

    @staticmethod
    def func(ax, *args, **kwargs):
        maxes.Axes.pcolor(ax, *args, **kwargs)


class Scatter(Base):
    __slots__ = tuple()

    def setup(self):
        self.name = "scatter_plk"
        self.enable_datas("1D")
        self.needs(x="", y="", z="")
        self.set_options(vmin="None", vmax="None", cmap="'jet'", s="20")

    @staticmethod
    def func(ax, *args, **kwargs):
        maxes.Axes.scatter(ax, *args, **kwargs)


KNOWN_METHOD = dict()
for cls in Pcolormesh, Scatter, Pcolor:
    m = cls()
    KNOWN_METHOD[m.name] = m


def best_geo_method(geo_datatype):
    return {
        Base.DATA_LEVEL["1D"]: Scatter,
        Base.DATA_LEVEL["2DU"]: Scatter,
        Base.DATA_LEVEL["2D"]: Pcolormesh,
    }[geo_datatype]

