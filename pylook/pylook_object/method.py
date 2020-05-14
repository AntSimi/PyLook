import numpy
import matplotlib.markers as mmarkers
import matplotlib.cm as mcm
import matplotlib.collections as mcollections
import matplotlib.contour as mcontour
import matplotlib.colorbar as mcolorbar
import copy
import logging
from .base import Base, Choices, Option
from ..data import DATA_LEVEL
from ..data.data_store import DataStore


logger = logging.getLogger("pylook")


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

    def copy(self):
        new = super().copy()
        new.data = self.data
        return new

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

    @staticmethod
    def merge_indexs(indexs):
        indexs_ = dict()
        for filename, group in indexs.items():
            if filename not in indexs_:
                indexs_[filename] = dict()
            for index in group:
                for axes, v in index.items():
                    if axes not in indexs_[filename]:
                        indexs_[filename][axes] = v
                    else:
                        indexs_[filename][axes] *= v
        return indexs_

    def __getitem__(self, selection):
        d = DataStore()
        data = dict()
        indexs = dict()
        for k in set(self.data.keys()) & set(selection.keys()):
            for varname, filename in self.data[k]:
                if filename not in indexs:
                    indexs[filename] = list()
                indexs[filename].append(
                    d[filename][varname].get_selection(selection[k])
                )
        indexs = self.merge_indexs(indexs)
        for k, v in self.data.items():
            data[k] = list()
            for varname, filename in v:
                data[k].append(d[filename][varname][indexs[filename]])
        self.merge(data)
        logger.info(",".join(f"{k} : {v.shape}" for k, v in data.items()))
        return data

    @staticmethod
    def merge(data):
        for k, v in data.items():
            if len(v) > 1:
                data[k] = numpy.concatenate(v)
            else:
                data[k] = v[0]


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
        new.building_options = self.building_options
        return new


class Legend(MethodLegend):
    __slot__ = tuple()
    BASH_COLOR = "\033[0;95m"
    QT_COLOR = "#E769D8"

    @property
    def known_children(self):
        return []

    @property
    def renderer_class(self):
        return KNOWN_LEGEND[self.target]

    def build(self, mappable):
        legend = self.renderer_class.func(mappable)
        legend.id = self.id
        legend.pylook_object = self.copy()
        return legend


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
        data = self.data[dict(x=ax.coordinates_bbox[0], y=ax.coordinates_bbox[1])]
        mappable = self.renderer_class.func(ax, data)
        mappable.id = self.id
        mappable.pylook_object = self.copy()
        mappable.child_id = dict()
        return mappable


class BaseMethodLegend:
    __slots__ = (
        "_name",
        "help",
        "options",
        "building_options",
    )

    def __init__(self):
        self._name = "noname"
        self.options = dict()
        self.building_options = list()
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
        obj.building_options = tuple(self.building_options)
        return obj


class BaseLegend(BaseMethodLegend):
    __slots__ = tuple()

    def exchange_object(self):
        obj = Legend()
        obj.update_options(obj.init_value, self.options)
        obj.start_current_value()
        obj.target = self.name
        return obj


class Colorbar(mcolorbar.Colorbar):
    def get_label(self):
        return self._label


class ColorbarL(BaseLegend):
    __slots__ = tuple()

    def setup(self):
        self.name = "colorbar_plk"
        self.set_options(label="''", ticks="None")

    @staticmethod
    def func(mappable, **kwargs):
        ax = mappable.axes
        v = ax.get_position()
        cax = ax.figure.add_axes((v.x1 + 0.02, v.y0, 0.01, v.height))
        cb = Colorbar(cax, mappable, **kwargs)
        return cb


class ContourCollection(mcontour.QuadContourSet):
    def remove(self):
        for collection in self.collections:
            collection.remove()


class Contour(BaseMethod):
    __slots__ = tuple()

    def setup(self):
        self.name = "contour_plk"
        self.enable_datas("2D")
        self.needs(x="", y="", z="")
        self.set_options(cmap=self.CMAP, alpha="None")

    @staticmethod
    def func(ax, data, **kwargs):
        m = ax.contour(data["x"], data["y"], data["z"].T, **kwargs)
        m.__class__ = ContourCollection
        return m


class ContourF(BaseMethod):
    __slots__ = tuple()

    def setup(self):
        self.name = "contourf_plk"
        self.enable_datas("2D")
        self.needs(x="", y="", z="")
        self.building_options.append("levels")
        self.set_options(cmap=self.CMAP, alpha="None", levels=None)

    @staticmethod
    def func(ax, data, **kwargs):
        m = ax.contourf(data["x"], data["y"], data["z"].T, **kwargs)
        m.__class__ = ContourCollection
        return m


class Pcolormesh(BaseMethod):
    __slots__ = tuple()

    def setup(self):
        self.name = "pcolormesh_plk"
        self.enable_datas("2D")
        self.needs(x="", y="", z="")
        self.set_options(
            clim=Option(vmin="None", vmax="None"),
            cmap=self.CMAP,
            zorder="0",
            alpha="None",
            linewidths="None",
            edgecolors=Base.COLOR,
        )
        self.legend_available.append("colorbar_plk")

    @staticmethod
    def func(ax, data, **kwargs):
        return ax.pcolormesh(data["x"], data["y"], data["z"].T, **kwargs)


class HexBin(BaseMethod):
    __slots__ = tuple()

    def setup(self):
        self.name = "hexbin_plk"
        self.enable_datas("1D")
        self.needs(x="", y="", z="")
        self.set_options(
            clim=Option(vmin="None", vmax="None"),
            cmap=self.CMAP,
            zorder="0",
            alpha="None",
            mincnt="2",
            linewidths="None",
            edgecolors=Base.COLOR,
        )
        # self.legend_available.append("colorbar_plk")

    @staticmethod
    def func(ax, data, **kwargs):
        kwargs["gridsize"] = (100, 50)
        return ax.hexbin(data["x"], data["y"], data["z"], **kwargs)


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
        return getattr(self, "marker_plk", None)


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
            alpha="None",
            linewidths="0",
            edgecolors=Base.COLOR_K,
            marker=self.FILLED_MARKERS,
        )

    @staticmethod
    def func(ax, data, **kwargs):
        m = ax.scatter(data["x"], data["y"], c=data["z"], **kwargs)
        m.__class__ = ScatterCollection
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
            markersize="1.",
            color=Base.COLOR_K,
            zorder="110",
        )

    @staticmethod
    def func(ax, data, **kwargs):
        return ax.plot(data["x"], data["y"], **kwargs)[0]


KNOWN_METHOD = dict()
for cls in Pcolormesh, Scatter, Pcolor, Plot, Contour, ContourF, HexBin:
    m = cls()
    KNOWN_METHOD[m.name] = m

KNOWN_LEGEND = dict()
for cls in (ColorbarL,):
    m = cls()
    KNOWN_LEGEND[m.name] = m


def best_geo_method(geo_datatype):
    return {
        DATA_LEVEL["1D"]: Scatter,
        DATA_LEVEL["2DU"]: Scatter,
        DATA_LEVEL["2D"]: Pcolormesh,
    }[geo_datatype]
