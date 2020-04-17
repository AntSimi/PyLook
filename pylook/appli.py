import argparse
import PyQt5.QtWidgets
import sys

# FIXME if remove problem with signal ?
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from .ui.pylook import Ui_MainWindow
from .data.data_store import DataStore


class MainWindow(PyQt5.QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.figures_tree.tree_to_figures()


class GenericParser(argparse.ArgumentParser):
    def standard_argument(self):
        self.add_argument(
            "-v",
            "--verbose",
            default="WARNING",
            choices=("DEBUG", "INFO", "WARNING", "ERROR"),
            # action=,
        )

    def parse_args(self, *args, **kwargs):
        args = super().parse_args(*args, **kwargs)
        return args


class PyLookParser(GenericParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.standard_argument()
        group = self.add_argument_group("Data")
        group.add_argument("filenames", nargs="*")
        group.add_argument("--demo_datasets", action="store_true")

    def parse_args(self, *args, **kwargs):
        args = super().parse_args(*args, **kwargs)
        d = DataStore()
        d.add_paths(args.filenames)
        if args.demo_datasets:
            d.add_demo_datasets()
        return args


def pylook():
    parser = PyLookParser("PyLook, interactive data explorer")
    args = parser.parse_args()

    app = PyQt5.QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.data_tree.populate()
    main_window.show()
    app.exec_()


def dataheader():
    parser = PyLookParser("PyLook, interactive data explorer")
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    d = DataStore()
    print(d.summary(color_bash=True, full=args.full))
