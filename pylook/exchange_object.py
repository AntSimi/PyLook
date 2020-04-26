import logging
import uuid
import json
import argparse
from copy import deepcopy
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from .figure import Figure as FigurePlot
from .figures_set import FigureSet as FigureSetPlot


logger = logging.getLogger("pylook")


class PyLookEncoder(json.JSONEncoder):
    INTERN_ATTR = ("building_options", "help", "id", "init_value")

    def default(self, o):
        dump = {k: v for k, v in o.__dict__.items() if k not in self.INTERN_ATTR}
        dump["__type__"] = o.__class__.__name__
        return dump


def as_pylook_object(dct):
    object_type = dct.get("__type__", None)
    for obj in (FigureSet, Figure, GeoSubplot, SimpleSubplot, Method, Data, Legend):
        if obj.__name__ == object_type:
            new_obj = obj()
            new_obj.appends(*dct["child"])
            for k, v in dct.items():
                if k in ("__type__", "child"):
                    continue
                setattr(new_obj, k, v)
            return new_obj
    return dct


class Choices(list):
    def __init__(self, *choices, default=None):
        super().__init__(choices)
        self.default = self[0] if default is None else default

    def summary(self, shorten=False):
        if shorten and len(self) > 10:
            return ", ".join(self[:6]) + ", ..."
        return ", ".join(self)


class Bool(Choices):
    def __init__(self):
        super().__init__("True", "False")


class FBool(Bool):
    def __init__(self):
        super().__init__()
        self.default = self[1]


class Base:
    __slot__ = (
        "current_value",
        "init_value",
        "child",
        "help",
        "id",
        "building_options",
    )

    COLOR = Choices(
        "'None'", "'r'", "'b'", "'y'", "'g'", "'k'", "'c'", "'w'", "'olive'"
    )
    LINESTYLE = Choices("'-'", "'--'", "'-.'")

    def __init__(self):
        super().__init__()
        self.child = list()
        self.start_current_value()
        self.id = uuid.uuid1().int
        self.building_options = tuple()

    def __new__(cls):
        return super().__new__(cls)

    def save(self, filename):
        with open(filename, "w") as f:
            json.dump(
                self, f, cls=PyLookEncoder, sort_keys=True, indent=4, ensure_ascii=False
            )

    @classmethod
    def with_options(cls, options):
        obj = cls()
        obj.update_options(obj.options, options)
        return obj

    @classmethod
    def update_options(cls, new_options, options):
        for k, v in options.items():
            if isinstance(v, dict):
                cls.update_options(new_options[k], v)
            else:
                new_options[k] = v

    def copy(self):
        new = self.__new__(self.__class__)
        new.child = [child.copy() for child in self.child]
        new.init_value = deepcopy(self.init_value)
        new.current_value = deepcopy(self.current_value)
        new.help = self.help
        new.id = self.id
        new.building_options = self.building_options
        return new

    def start_current_value(self):
        self.current_value = self.copy_options(self.init_value)

    @classmethod
    def copy_options(cls, options):
        new_options = dict()
        for k, v in options.items():
            if isinstance(v, Choices):
                v = v.default
            if isinstance(v, dict):
                v = cls.copy_options(v)
            new_options[k] = v
        return new_options

    @property
    def options_names(self):
        return list(self.current_value.keys())

    def get_option(self, name, evaluate=True):
        if evaluate:
            return eval(self.current_value[name])
        else:
            return self.current_value[name]

    @property
    def options(self):
        return self.current_value

    def __iter__(self):
        for i in self.child:
            yield i

    def pop_childs(self):
        childs = self.child
        self.child = list()
        return childs

    def append(self, elt):
        self.child.append(elt)

    def appends(self, *elt):
        self.child.extend(elt)

    def __str__(self):
        return self.summary(full=False, compress=True)

    @property
    def known_children(self):
        return []

    @classmethod
    def summary_options(cls, options, compress=False):
        if len(options):
            elts = list()
            keys = list(options.keys())
            keys.sort()
            for k in keys:
                v = options[k]
                v_dict = isinstance(v, dict)
                if v_dict:
                    v = cls.summary_options(v, compress).replace("\n", "\n    ")
                if compress:
                    if v_dict:
                        elts.append(f"\n{k}: {v}\n")
                    else:
                        elts.append(f"{k}: {v}")
                else:
                    elts.append(f"{k:8}: {v}")
            if compress:
                out = "\n" + " |".join(elts).replace("\n |", "\n").replace("|\n", "\n")
                return out.replace("\n\n", "\n")
            else:
                return "\n" + "\n".join(elts)
        else:
            return ""

    def summary(self, color_bash=True, full=True, compress=False):
        summaries = list()
        for child in self:
            summaries.append(child.summary(color_bash, full, compress))
        if len(summaries):
            synthesis = "\n    " + "\n".join(summaries).replace("\n", "\n    ")
        else:
            synthesis = ""
        c = self.BASH_COLOR if color_bash else ""
        c_escape = "\033[0;0m" if color_bash else ""
        options = self.summary_options(self.options, compress).replace(
            "\n", "\n        "
        )
        sup = f" ({self.id})" if full else ""
        return f"{c}{self.__class__.__name__}{sup}{c_escape}{options}{synthesis}"

    @property
    def name(self):
        raise Exception("must be define")

    def build(self, *args, **kwargs):
        raise Exception("must be define")

    def build_child(self, parent, ids=None):
        for item in self:
            if ids is not None and item.id not in ids:
                continue
            child = item.build(parent)
            parent.child_id[child.id] = child

    def get_set(self, item, k):
        if k in self.building_options:
            logger.debug(f"{self.__class__.__name__} : only for building : {k}")
            return None, None
        set_func = getattr(item, f"set_{k}", None)
        get_func = getattr(item, f"get_{k}", None)
        if set_func is None and hasattr(item, "has_") and item.has_(k):
            set_func, get_func = lambda value: item.set_(k, value), lambda: item.get_(k)
        if set_func is None or get_func is None:
            logger.debug(
                f"{self.__class__.__name__} : set ({set_func}) or/and get ({get_func}) doesn't exist {k}"
            )
            return None, None
        return set_func, get_func

    def apply_options(self, item, options):
        for k, v in options.items():
            if isinstance(v, dict):
                self.apply_options(item, v)
                continue
            set_func, get_func = self.get_set(item, k)
            if set_func is None:
                continue
            new_value = eval(v)
            if get_func() != new_value:
                set_func(new_value)

    def update(self, item, recursive=True):
        self.apply_options(item, self.options)
        if recursive:
            for child in self:
                if child.id not in item.child_id:
                    self.build_child(item, [child.id])
                child.update(item.child_id[child.id], recursive=recursive)


class Data(Base):
    __slot__ = tuple()
    BASH_COLOR = "\033[0;89m"
    QT_COLOR = "#D7D7D7"

    def __init__(self, *args, **kwargs):
        self.init_value = dict()
        self.help = dict()
        super().__init__(*args, **kwargs)


class Legend(Base):
    __slot__ = tuple()
    BASH_COLOR = "\033[0;95m"
    QT_COLOR = "#E769D8"

    def __init__(self, *args, **kwargs):
        self.init_value = dict()
        self.help = dict()
        super().__init__(*args, **kwargs)


class Method(Base):
    __slot__ = tuple()
    BASH_COLOR = "\033[0;90m"
    QT_COLOR = "#707070"

    def __init__(self, *args, **kwargs):
        self.init_value = dict()
        self.help = dict()
        super().__init__(*args, **kwargs)

    @property
    def known_children(self):
        return [Data, Legend]


class Subplot(Base):
    __slot__ = tuple()
    BASH_COLOR = "\033[0;93m"
    QT_COLOR = "#EDE400"

    def __init__(self, *args, **kwargs):
        self.help = dict(
            position=dict(
                doc="Axes specification must be a tuple of 3 values (nb_x, nb_y, i) or a list of 4 values [x0, y0, dx, dy] which are a fraction of figures."
            )
        )
        super().__init__(*args, **kwargs)

    @property
    def known_children(self):
        return [Method]


class SimpleSubplot(Subplot):
    __slot__ = tuple()

    def __init__(self, *args, **kwargs):
        self.init_value = dict(
            position="111",
            ylabel="''",
            xlabel="''",
            grid=Bool(),
            zorder="0",
            title="''",
        )
        super().__init__(*args, **kwargs)

    @property
    def name(self):
        return "Simple subplot"

    def build(self, figure):
        ax = figure.add_subplot(self.get_option("position"), projection="pylook_simple")
        ax.id = self.id
        return ax


class GeoSubplot(Subplot):
    __slot__ = tuple()

    def __init__(self, *args, **kwargs):
        self.init_value = dict(
            position="111",
            ylabel="''",
            xlabel="''",
            grid=Bool(),
            zorder="0",
            title="''",
            geo=dict(
                coast=dict(
                    coast=Bool(),
                    coast_color=self.COLOR,
                    coast_linewidth=".25",
                    coast_linestyle=self.LINESTYLE,
                ),
                river=dict(
                    river=FBool(),
                    river_color=self.COLOR,
                    river_linewidth=".25",
                    river_linestyle=self.LINESTYLE,
                ),
                border=dict(
                    border=FBool(),
                    border_color=self.COLOR,
                    border_linewidth=".25",
                    border_linestyle=self.LINESTYLE,
                ),
            ),
        )

        super().__init__(*args, **kwargs)
        self.help["geo"] = dict(river=dict(river=dict(doc="Display river if True")))

    @property
    def name(self):
        return "Geo subplot"

    def build(self, figure):
        ax = figure.add_subplot(self.get_option("position"), projection="plat_carre")
        ax.id = self.id
        return ax


class Figure(Base):
    __slot__ = tuple()
    BASH_COLOR = "\033[0;32m"
    QT_COLOR = "#00B31B"

    def __init__(self, *args, **kwargs):
        self.init_value = dict(
            facecolor=self.COLOR, figsize="None", suptitle="''", dpi="100"
        )
        self.help = dict(figsize=dict(doc="Will be not use in GUI"))
        super().__init__(*args, **kwargs)

    @property
    def known_children(self):
        return [GeoSubplot, SimpleSubplot]

    @property
    def name(self):
        return "Figure"

    def build(self, widget):
        fig = FigurePlot()
        fig.canvas = FigureCanvasQTAgg(fig)
        fig.toolbar = NavigationToolbar2QT(fig.canvas, widget)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(fig.canvas)
        vbox.addWidget(fig.toolbar)
        widget.setLayout(vbox)
        self.build_child(fig)
        for child in fig.child_id.values():
            child.set_callback_axes_properties(fig.axes_properties_message)
        fig.id = self.id
        return fig

    def update(self, figure, *args, **kwargs):
        super().update(figure, *args, **kwargs)
        figure.canvas.draw()


class FigureSet(Base):
    __slot__ = tuple()
    BASH_COLOR = "\033[0;36m"
    QT_COLOR = "#00A3B3"

    def __init__(self, *args, **kwargs):
        self.init_value = dict(
            coordinates=dict(
                llcrnrlon="-180",
                urcrnrlon="180",
                llcrnrlat="-90",
                urcrnrlat="90",
                projection=Choices("'plat_carre'", "'ortho'"),
            ),
        )
        self.help = dict()
        super().__init__(*args, **kwargs)

    @property
    def known_children(self):
        return [Figure]

    @property
    def name(self):
        return "Figure set"

    def build_child(self, parent):
        for item in self:
            frame = parent.get_new_frame()
            figure = item.build(frame)
            item.update(figure)
            parent.append_child(figure)

    def build(self):
        fs = FigureSetPlot()
        self.build_child(fs)
