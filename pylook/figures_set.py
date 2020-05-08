import logging

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

    @staticmethod
    def get_new_frame():
        from PyQt5 import QtWidgets, QtGui
        frame = QtWidgets.QMainWindow()
        main_frame = QtWidgets.QWidget()
        frame.setCentralWidget(main_frame)
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/icons/images/geo.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )
        frame.setWindowIcon(icon)
        frame.resize(800, 600)
        frame.show()
        main_frame.frame = frame
        return main_frame
