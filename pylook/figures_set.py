import logging
from PyQt5 import QtWidgets, QtGui

logger = logging.getLogger("pylook")


class FigureSet:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.child_id = dict()

    def append_child(self, figure):
        self.child_id[figure.id] = figure
        figure.set_callback_axes_properties(self.axes_properties_message)

    def axes_properties_message(self, figure_id, properties):
        logger.trace(f"Receive properties from figure : {figure_id}")
        for id_, child in self.child_id.items():
            if id_ == figure_id:
                continue
            child.set_axes_with_message(properties)

    def get_new_main_window(self):
        app = QtWidgets.QApplication(list())
        app.frame = QtWidgets.QMainWindow()
        app.main_frame = QtWidgets.QWidget()
        app.frame.setCentralWidget(app.main_frame)
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/icons/images/geo.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )
        app.frame.setWindowIcon(icon)
        app.frame.resize(800, 600)
        app.frame.show()
        return app
