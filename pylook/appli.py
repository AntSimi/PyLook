import PyQt5.QtWidgets
import sys
import logging
from .ui.pylook import Ui_MainWindow
from .data.data_store import DataStore
from .exchange_object import FigureSet
from .parser import GenericParser


class MainWindow(PyQt5.QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.figures_tree.tree_to_figures()
        # TO DO : ugly fix to connect logging with statusbar
        logging.getLogger("pylook").handlers[0].set_statusbar(self.statusbar)


class PyLookParser(GenericParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        group = self.add_argument_group("Figures")
        group.add_argument("--figures_set_files", type=str, nargs="+")
        group.add_argument("--display_figures", action="store_true")


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
    if args.display_figures:
        f_tree.tree_to_figures()
    main_window.show()
    app.exec_()


def data_header():
    parser = GenericParser("DataHeader, give a summary of data file")
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    d = DataStore()
    print(d.summary(color_bash=True, full=args.full))
