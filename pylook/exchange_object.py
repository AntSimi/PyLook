class Base:
    __slot__ = ("current_value", "init_value", "child")

    def __init__(self, *args, **kwargs):
        super(Base, self).__init__(*args, **kwargs)
        self.child = list()

    def __iter__(self):
        for i in self.child:
            yield i

    def append(self, elt):
        self.child.append(elt)

    def appends(self, *elt):
        self.child.extend(elt)

    def __str__(self):
        return ""

    def summary(self, color_bash=True, full=True):
        summaries = list()
        for child in self:
            summaries.append(child.summary())
        if len(summaries):
            synthesis = "\n    " + "\n".join(summaries).replace("\n", "\n    ")
        else:
            synthesis = ""
        c = self.BASH_COLOR if color_bash else ""
        c_escape = "\033[0;0m" if color_bash else ""
        return f"{c}{self.__class__.__name__}{c_escape}{synthesis}"


class FigureSet(Base):
    __slot__ = tuple()
    BASH_COLOR = "\033[0;36m"

    def __init__(self, *args, **kwargs):
        super(FigureSet, self).__init__(*args, **kwargs)
        self.init_value = dict(
            coordinates=dict(
                llcrnrlon="-180",
                urcnrlon="180",
                llcrnrlat="-90",
                urcnrlat="90",
                projection=["plat_carre", "ortho"],
            ),
        )


class Figure(Base):
    __slot__ = tuple()
    BASH_COLOR = "\033[0;32m"

    def __init__(self, *args, **kwargs):
        super(Figure, self).__init__(*args, **kwargs)
        self.default_value = dict(figsize="None", title="''", dpi="100")


class Subplot(Base):
    __slot__ = tuple()
    BASH_COLOR = "\033[0;93m"

    def __init__(self, *args, **kwargs):
        super(Subplot, self).__init__(*args, **kwargs)
        self.default_value = dict(
            position="111",
            ylabel="''",
            xlabel="''",
            grid="True",
            zorder="0",
            title="''",
        )


class Method(Base):
    __slot__ = tuple()


class Data(Base):
    __slot__ = tuple()


class Legend(Base):
    __slot__ = tuple()
