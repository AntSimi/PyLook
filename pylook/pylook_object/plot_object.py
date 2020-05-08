import logging
import uuid
import json
from copy import deepcopy
from ..figure import Figure as FigurePlot
from ..figures_set import FigureSet as FigureSetPlot
from .base import Base, Choices, Option, Bool, FBool
from .method import Method


logger = logging.getLogger("pylook")


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
            xlim="0,1",
            ylim="0,1",
        )
        super().__init__(*args, **kwargs)

    @property
    def name(self):
        return "Simple subplot"

    def build(self, figure):
        ax = figure.add_subplot(self.get_option("position"), projection="standard")
        ax.id = self.id
        return ax


class GeoSubplot(Subplot):
    __slot__ = tuple()

    def __init__(self, *args, **kwargs):
        self.init_value = dict(
            position="111",
            ylabel=Option(ylabel="''", fontdict=self.fontdict()),
            xlabel=Option(xlabel="''", fontdict=self.fontdict()),
            grid=Bool(),
            zorder="0",
            title=Option(label="''", fontdict=self.fontdict()),
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
        self.build_child(ax)
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

    def build(self, widget=None, pyqt=True):
        if pyqt:
            from PyQt5 import QtWidgets
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
            from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
            fig = FigurePlot()
            fig.canvas = FigureCanvasQTAgg(fig)
            fig.toolbar = NavigationToolbar2QT(fig.canvas, widget)
            vbox = QtWidgets.QVBoxLayout()
            vbox.addWidget(fig.canvas)
            vbox.addWidget(fig.toolbar)
            widget.setLayout(vbox)
        else:
            from matplotlib import pyplot as plt
            fig = plt.figure(FigureClass=FigurePlot)
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

    def build_child(self, parent, pyqt=True):
        for item in self:
            if pyqt:
                frame = parent.get_new_frame()
                figure = item.build(frame)
            else:
                figure = item.build(pyqt=pyqt)
            item.update(figure)
            parent.append_child(figure)

    def build(self, pyqt=True):
        fs = FigureSetPlot()
        self.build_child(fs, pyqt)
        return fs
