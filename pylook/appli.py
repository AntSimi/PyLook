import argparse
import PyQt5.QtWidgets
import sys
import logging

# FIXME if remove problem with signal ?
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from .ui.pylook import Ui_MainWindow
from .data.data_store import DataStore
from .logger import start_logger


class MainWindow(PyQt5.QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.figures_tree.tree_to_figures()
        # TO DO : ugly fix to connect logging with statusbar
        logging.getLogger("pylook").handlers[0].set_statusbar(self.statusbar)


class GenericParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = start_logger()

    def standard_argument(self):
        self.add_argument(
            "-v",
            "--verbose",
            default="WARNING",
            choices=("TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
        )

    def parse_args(self, *args, **kwargs):
        args = super().parse_args(*args, **kwargs)
        self.logger.setLevel(logging.getLevelName(args.verbose.upper()))
        return args


class PyLookParser(GenericParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.standard_argument()
        group = self.add_argument_group("Data")
        group.add_argument("filenames", nargs="*")
        group.add_argument("--demo_datasets", action="store_true")
        group.add_argument("--figures_set_files", type=str, nargs="+")
        group.add_argument("-d", "--dipslay_tree", action="store_true")

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
    f_tree = main_window.figures_tree
    if args.figures_set_files is None:
        f_tree.init_tree()
    else:
        for filename in args.figures_set_files:
            f_tree.load_object(filename)
    if args.dipslay_tree:
        f_tree.tree_to_figures()
    main_window.show()
    app.exec_()


def dataheader():
    parser = PyLookParser("PyLook, interactive data explorer")
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    d = DataStore()
    print(d.summary(color_bash=True, full=args.full))
