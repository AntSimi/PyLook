import argparse
import PyQt5.QtWidgets
import sys
from .ui.pylook import Ui_MainWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
import matplotlib.figure as mfigure

class MainWindow(PyQt5.QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.add_figure(self.tab)
        self.add_figure(self.tab_2)
        self.tabWidget.make_undock()
    
    def add_figure(self, tab):
        f = mfigure.Figure()
        ax = f.add_subplot(111, projection='plat_carre', coast=True) 
        ax.grid(True)
        f.canvas = FigureCanvasQTAgg(f)
        f.toolbar = NavigationToolbar2QT(f.canvas, tab)
        vbox = PyQt5.QtWidgets.QVBoxLayout()
        vbox.addWidget(f.canvas)
        vbox.addWidget(f.toolbar)
        tab.setLayout(vbox)



def pylook():
    parser = argparse.ArgumentParser('PyLook, interactive data explorer')
    args = parser.parse_args()

    app = PyQt5.QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec_()
