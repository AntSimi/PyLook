import argparse
import PyQt5.QtWidgets
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
import matplotlib.figure as mfigure
from .ui.pylook import Ui_MainWindow
from .data.data_store import DataStore

class MainWindow(PyQt5.QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.add_figure(self.start_tab)
        self.figures_tree.expandAll()

    @staticmethod
    def add_figure(tab):
        f = mfigure.Figure()
        # ax = f.add_axes([0,0,1,1], projection='plat_carre', coast=True) 
        ax = f.add_subplot(111, projection='plat_carre', coast=True, maximize_screen=True) 
        ax.grid(True)
        f.canvas = FigureCanvasQTAgg(f)
        f.toolbar = NavigationToolbar2QT(f.canvas, tab)
        vbox = PyQt5.QtWidgets.QVBoxLayout()
        vbox.addWidget(f.canvas)
        vbox.addWidget(f.toolbar)
        tab.setLayout(vbox)


class GenericParser(argparse.ArgumentParser):
    
    def standard_argument(self):
        self.add_argument(
            '-v', '--verbose',
            default='WARNING',
            choices=('DEBUG', 'INFO', 'WARNING', 'ERROR'),
            # action=,
            )

    def parse_args(self, *args, **kwargs):
        args = super(GenericParser, self).parse_args(*args, **kwargs)
        return args

class PyLookParser(GenericParser):

    def __init__(self, *args, **kwargs):
        super(PyLookParser, self).__init__(*args, **kwargs)
        self.standard_argument()
        group = self.add_argument_group('Data')
        group.add_argument('filenames', nargs='+')

    def parse_args(self, *args, **kwargs):
        args = super(GenericParser, self).parse_args(*args, **kwargs)
        d = DataStore()
        d.add_files(args.filenames)
        return args


def pylook():
    parser = PyLookParser('PyLook, interactive data explorer')
    args = parser.parse_args()

    app = PyQt5.QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.data_tree.populate()
    main_window.show()
    app.exec_()
