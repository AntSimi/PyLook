class Base:
    __slot__ = ("current_value", "init_value", "child")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.child = list()
        self.start_current_value()

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
        return ""

    @classmethod
    def summary_options(cls, options, compress=False):
        if len(options):
            elts = list()
            keys = list(options.keys())
            keys.sort()
            for k in keys:
                v = options[k]
                if isinstance(v, dict):
                    v = cls.summary_options(v, compress).replace("\n", "\n    ")
                elts.append(f"{k:8} : {v}")
            out = "\n".join(elts)
            if compress:
                out = out.replace('\n', ' | ')
            return "\n" + out 
        else:
            return ""

    def summary(self, color_bash=True, full=True, compress=False):
        summaries = list()
        for child in self:
            summaries.append(child.summary())
        if len(summaries):
            synthesis = "\n    " + "\n".join(summaries).replace("\n", "\n    ")
        else:
            synthesis = ""
        c = self.BASH_COLOR if color_bash else ""
        c_escape = "\033[0;0m" if color_bash else ""
        options = self.summary_options(self.options, compress).replace("\n", "\n        ")
        return f"{c}{self.__class__.__name__}{c_escape}{options}{synthesis}"


class FigureSet(Base):
    __slot__ = tuple()
    BASH_COLOR = "\033[0;36m"

    def __init__(self, *args, **kwargs):
        self.init_value = dict(
            coordinates=dict(
                llcrnrlon="-180",
                urcnrlon="180",
                llcrnrlat="-90",
                urcnrlat="90",
                projection=["plat_carre", "ortho"],
            ),
        )
        super().__init__(*args, **kwargs)


class Figure(Base):
    __slot__ = tuple()
    BASH_COLOR = "\033[0;32m"

    def __init__(self, *args, **kwargs):
        self.init_value = dict(figsize="None", title="''", dpi="100")
        super().__init__(*args, **kwargs)


class Subplot(Base):
    __slot__ = tuple()
    BASH_COLOR = "\033[0;93m"

    def __init__(self, *args, **kwargs):
        self.init_value = dict(
            position="111",
            ylabel="''",
            xlabel="''",
            grid="True",
            zorder="0",
            title="''",
        )
        super().__init__(*args, **kwargs)


class Method(Base):
    __slot__ = tuple()
    BASH_COLOR = "\033[0;90m"

    def __init__(self, *args, **kwargs):
        self.init_value = dict()
        super().__init__(*args, **kwargs)


class Data(Base):
    __slot__ = tuple()
    BASH_COLOR = "\033[0;89m"

    def __init__(self, *args, **kwargs):
        self.init_value = dict()
        super().__init__(*args, **kwargs)


class Legend(Base):
    __slot__ = tuple()
    BASH_COLOR = "\033[0;95m"

    def __init__(self, *args, **kwargs):
        self.init_value = dict()
        super().__init__(*args, **kwargs)
