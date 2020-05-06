import numpy
import matplotlib.markers as mmarkers
import matplotlib.cm as mcm
import matplotlib.collections as mcollections
import copy
from .base import Base, Choices, Option
from ..data import DATA_LEVEL
from ..data.data_store import DataStore


class FakeObject:
    __slot__ = ("id",)


class Data(Base):
    __slot__ = ("data",)
    BASH_COLOR = "\033[0;91m"
    QT_COLOR = "#D7D7D7"

    def __init__(self, *args, **kwargs):
        self.init_value = dict()
        self.help = dict()
        self.data = dict()
        super().__init__(*args, **kwargs)

    def summary(self, *args, **kwargs):
        text = list()
        for k, variables in self.data.items():
            v_text = list()
            for v, f in variables:
                v_text.append(f"{v} > {f}")
            text.append(f"{k} :\n        " + "\n        ".join(v_text))
        return super().summary(*args, **kwargs) + "\n    " + "\n    ".join(text)

    def build(self, mappable):
        f = FakeObject()
        f.id = self.id
        return f

    def __getitem__(self, selection):
        d = DataStore()
        data = dict()
        for k, v in self.data.items():
            data[k] = list()
            for varname, filename in v:
                data[k].append(d[filename][varname][:])
        self.merge(data)
        return data

    @staticmethod
    def merge(data):
        for k, v in data.items():
            data[k] = numpy.concatenate(v)


class MethodLegend(Base):
    __slot__ = ("target",)

    def __init__(self, *args, **kwargs):
        self.init_value = dict()
        self.help = dict()
        self.target = None
        super().__init__(*args, **kwargs)

    def copy(self):
        new = super().copy()
        new.target = self.target
        return new

    def __call__(self):
        return self

    def summary(self, *args, **kwargs):
        kwargs["extra_info"] = f"\n    {self.target}"
        return super().summary(*args, **kwargs)

    def with_options(self, options):
        new = self.__class__()
        new.init_value = self.init_value
        new.start_current_value()
        new.update_options(new.options, options)
        new.target = self.target
        return new


class Legend(MethodLegend):
    __slot__ = tuple()
    BASH_COLOR = "\033[0;95m"
    QT_COLOR = "#E769D8"

    @property
    def known_children(self):
        return []


class Method(MethodLegend):
    __slot__ = tuple()
    BASH_COLOR = "\033[0;90m"
    QT_COLOR = "#707070"

    @property
    def known_children(self):
        return [Legend]

    @property
    def renderer_class(self):
        return KNOWN_METHOD[self.target]

    @property
    def data(self):
        for item in self:
            if isinstance(item, Data):
                return item

    def build(self, ax):
        data = self.data[ax.coordinates_bbox]
        mappable = self.renderer_class.func(ax, data)
        mappable.id = self.id
        mappable.child_id = dict()
        return mappable


class BaseMethodLegend:
    __slots__ = (
        "_name",
        "help",
        "options",
    )

    def __init__(self):
        self._name = "noname"
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

    def set_options(self, **kwargs):
        self.options.update(kwargs)


class BaseMethod(BaseMethodLegend):
    __slots__ = (
        "data_accept",
        "data_need",
        "legend_available",
    )
    FILLED_MARKERS = Choices(*[f"'{i}'" for i in mmarkers.MarkerStyle.filled_markers])
    MARKERS = Choices(*[f"'{i}'" for i in mmarkers.MarkerStyle.markers.keys()])
    CMAP = Choices(*[f"'{i}'" for i in mcm.cmap_d.keys()], default="'viridis'")

    def __init__(self):
        self.legend_available = list()
        self.data_accept = None
        self.data_need = dict()
        super().__init__()

    def enable_datas(self, datatype):
        self.data_accept = DATA_LEVEL[datatype]

    def needs(self, **kwargs):
        self.data_need.update(kwargs)

    def data_structure(self):
        return {k: list() for k in self.data_need.keys()}

    def exchange_object(self):
        obj = Method()
        obj.init_value = copy.deepcopy(self.options)
        obj.start_current_value()
        obj.target = self.name
        return obj


class BaseLegend(BaseMethodLegend):
    __slots__ = tuple()

    def exchange_object(self):
        obj = Legend()
        obj.update_options(obj.init_value, self.options)
        obj.start_current_value()
        obj.target = self.name
        return obj


class Pcolormesh(BaseMethod):
    __slots__ = tuple()

    def setup(self):
        self.name = "pcolormesh_plk"
        self.enable_datas("2D")
        self.needs(x="", y="", z="")
        self.set_options(vmin="None", vmax="None", cmap="'jet'")

    @staticmethod
    def func(ax, data, **kwargs):
        ax.pcolormesh(*args, **kwargs)


class Pcolor(BaseMethod):
    __slots__ = tuple()

    def setup(self):
        self.name = "pcolor_plk"
        self.enable_datas("2DU")
        self.needs(x="", y="", z="")
        self.set_options(vmin="None", vmax="None", cmap="'jet'")

    @staticmethod
    def func(ax, data, **kwargs):
        ax.pcolor(*args, **kwargs)


class ScatterCollection(mcollections.PathCollection):
    def set_size(self, size):
        return super().set_sizes((size,))

    def get_size(self):
        return super().get_sizes()[0]

    def set_marker(self, marker):
        self.marker_plk = marker
        marker_obj = mmarkers.MarkerStyle(marker)
        path = marker_obj.get_path().transformed(marker_obj.get_transform())
        self.set_paths((path,))

    def get_marker(self):
        return getattr(self, 'marker_plk', None)


class Scatter(BaseMethod):
    __slots__ = tuple()

    def setup(self):
        self.name = "scatter_plk"
        self.enable_datas("1D")
        self.needs(x="", y="", z="")
        self.set_options(
            clim=Option(vmin="None", vmax="None"),
            cmap=self.CMAP,
            size="20",
            label="''",
            zorder="100",
            alpha="1",
            linewidths="0",
            edgecolors=Base.COLOR_K,
            marker=self.FILLED_MARKERS,
        )

    @staticmethod
    def func(ax, data, **kwargs):
        # return ScatterCollection(
        #     edge=ax.scatter(data["x"], data["y"], **kwargs),
        #     color=ax.scatter(data["x"], data["y"], c=data["z"], **kwargs),
        # )
        m = ax.scatter(data["x"], data["y"], c=data["z"], **kwargs)
        m.__class__ = ScatterCollection
        print(m)
        return m


class Plot(BaseMethod):
    __slots__ = tuple()

    def setup(self):
        self.name = "plot_plk"
        self.enable_datas("1D")
        self.needs(x="", y="", z="")
        self.set_options(
            linestyle=Base.LINESTYLE,
            linewidth="1",
            label="''",
            marker=self.MARKERS,
            markersize="1",
            color=Base.COLOR_K,
            zorder="110",
        )

    @staticmethod
    def func(ax, data, **kwargs):
        return ax.plot(data["x"], data["y"], **kwargs)[0]


KNOWN_METHOD = dict()
for cls in Pcolormesh, Scatter, Pcolor, Plot:
    m = cls()
    KNOWN_METHOD[m.name] = m


class Colorbar(BaseLegend):
    __slots__ = tuple()

    def setup(self):
        self.name = colorbar_plk
        self.set_options(label="'colorbar'")

    @staticmethod
    def func(ax, mappable, *args, **kwargs):
        matplotlib.colorbar.Colorbar(colorbar_ax, mappable, *args, **kwargs)


def best_geo_method(geo_datatype):
    return {
        DATA_LEVEL["1D"]: Scatter,
        DATA_LEVEL["2DU"]: Scatter,
        DATA_LEVEL["2D"]: Pcolormesh,
    }[geo_datatype]