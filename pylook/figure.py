import logging
import matplotlib.figure as mfigure
from PyQt5 import QtWidgets
from .axes import MapAxes

logger = logging.getLogger("pylook")


class Figure(mfigure.Figure):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.callback_axes_properties = None
        self.child_id = dict()

    def set_callback_axes_properties(self, callback):
        self.callback_axes_properties = callback

    def set_suptitle(self, title):
        self.suptitle(title)

    def get_suptitle(self):
        text = self._suptitle
        return text if text is None else text.get_text()

    def axes_properties_message(self, axes_id, properties):
        logger.trace(f"figure {self.id} receive properties from axes : {axes_id}")
        for id_, child in self.child_id.items():
            if id_ == axes_id or not isinstance(child, MapAxes):
                continue
            child.set_axes_with_message(properties)
        if self.callback_axes_properties is not None:
            self.callback_axes_properties(self.id, properties)

    def set_axes_with_message(self, properties):
        for id_, child in self.child_id.items():
            if not isinstance(child, MapAxes):
                continue
            child.set_axes_with_message(properties)
        self.canvas.draw()


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
