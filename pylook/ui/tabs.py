from PyQt5 import QtWidgets, QtGui
from ..figures_set import FigureSet


class FigureWidget(QtWidgets.QWidget):
    def __init__(self, object):
        super().__init__()
        self.exchange_object = object
        self.setup_widget()

    def setup_widget(self):
        self.figure = self.exchange_object.build(self)
        self.exchange_object.update(self.figure)

    @property
    def id(self):
        return self.exchange_object.id


class TabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent=None, *args, **kwargs)
        self.parent = parent
        self.tabBarDoubleClicked.connect(self.onTabBarClicked)
        self.floating_figures = dict()
        self.figure_set = dict()

    def onTabBarClicked(self, index):
        if self.count() > 1:
            self.make_undock(index)

    def make_undock(self, index):
        """Undock a Tab from TabWidget and promote to a Dialog."""
        window = QtWidgets.QMainWindow(self)
        widget_from_tab = self.widget(index)
        window.setWindowTitle(self.tabText(index))
        window.setGeometry(widget_from_tab.geometry())

        def closeEvent_override(event):
            """Re-dock back from Dialog to a new Tab."""
            self.insertTab(self.count() + 1, widget_from_tab, window.windowTitle())
            self.floating_figures.pop(widget_from_tab.id)
            return event.accept()

        window.closeEvent = closeEvent_override
        self.removeTab(index)
        widget_from_tab.setParent(self.parent if self.parent else window)
        window.setCentralWidget(widget_from_tab)
        widget_from_tab.show()
        window.show()
        window.move(QtGui.QCursor.pos())
        self.floating_figures[widget_from_tab.id] = widget_from_tab

    def __iter__(self):
        for i in range(self.count()):
            yield self.widget(i)
        for figure in self.floating_figures.values():
            yield figure

    @property
    def known_id(self):
        return [i.id for i in self]

    def figure(self, id_figure):
        for i in self:
            if i.id == id_figure:
                return i

    def update_figures(self, figure_sets):
        known_id = self.known_id
        for figure_set in figure_sets:
            self.figure_set[figure_set.id] = FigureSet()
            for figure in figure_set:
                if figure.id in known_id:
                    figure.update(self.figure(figure.id).figure)
                else:
                    fw = FigureWidget(figure)
                    self.addTab(fw, str(figure.id))
                    self.figure_set[figure_set.id].append_child(fw.figure)
