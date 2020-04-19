from copy import deepcopy
import uuid


class Base:
    __slot__ = (
        "current_value",
        "init_value",
        "child",
        "help",
        "id",
        "building_options",
    )

    COLOR = ["'None'", "'r'", "'b'"]
    BOOL = ["True", "False"]

    def __init__(self):
        super().__init__()
        self.child = list()
        self.start_current_value()
        self.id = uuid.uuid1().int
        self.building_options = tuple()

    def __new__(cls):
        return super().__new__(cls)

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
            if isinstance(v, list):
                v = v[0]
            if isinstance(v, dict):
                v = cls.copy_options(v)
            new_options[k] = v
        return new_options

    @property
    def options_names(self):
        return list(self.current_value.keys())

    def get_options(self, name, evaluate=True):
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
        if not hasattr(parent, "child_id"):
            parent.child_id = dict()
        for item in self:
            if ids is not None and item.id not in ids:
                continue
            child = item.build(parent)
            parent.child_id[child.id] = child

    def apply_options(self, item, options):
        for k, v in options.items():
            if isinstance(v, dict):
                self.apply_options(item, v)
                continue
            set_func = getattr(item, f"set_{k}", None)
            get_func = getattr(item, f"get_{k}", None)
            if k in self.building_options:
                print(f"{self.__class__.__name__} : only for building : {k}")
                continue
            elif set_func is None or get_func is None:
                print(
                    f"{self.__class__.__name__} : set ({set_func}) or/and get ({get_func}) doesn't exist {k}"
                )
                continue
            else:
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
        self.init_value = dict(
            position="111",
            ylabel="''",
            xlabel="''",
            grid=self.BOOL,
            zorder="0",
            title="''",
            geo=dict(
                coast=dict(coast=self.BOOL, coast_color=self.COLOR, coast_linewidth="1"),
                border=self.BOOL,
                border_color=self.COLOR,
                river=self.BOOL,
                river_color=self.COLOR,
            ),
        )
        self.help = dict(
            position=dict(
                doc="Axes specification must be a tuple of 3 values (nb_x, nb_y, i) or a list of 4 values [x0, y0, dx, dy] which are a fraction of figures."
            )
        )
        super().__init__(*args, **kwargs)
        self.building_options = ("position",)

    @property
    def known_children(self):
        return [Method]

    @property
    def name(self):
        return "Subplot"

    def build(self, figure):
        ax = figure.add_subplot(self.get_options("position"), projection="plat_carre")
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
        self.help = dict()
        super().__init__(*args, **kwargs)

    @property
    def known_children(self):
        return [Subplot]

    @property
    def name(self):
        return "Figure"


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
                projection=["'plat_carre'", "'ortho'"],
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
