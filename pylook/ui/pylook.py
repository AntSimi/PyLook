# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pylook/ui/pylook.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/images/geo.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setDockOptions(QtWidgets.QMainWindow.AllowTabbedDocks|QtWidgets.QMainWindow.AnimatedDocks|QtWidgets.QMainWindow.VerticalTabs)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setObjectName("verticalLayout")
        self.figures_tab_dock = TabWidget(self.centralwidget)
        self.figures_tab_dock.setObjectName("figures_tab_dock")
        self.verticalLayout.addWidget(self.figures_tab_dock)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 20))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.data_dock = QtWidgets.QDockWidget(MainWindow)
        self.data_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable|QtWidgets.QDockWidget.DockWidgetMovable)
        self.data_dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        self.data_dock.setObjectName("data_dock")
        self.data_widget = QtWidgets.QWidget()
        self.data_widget.setObjectName("data_widget")
        self.data_layout = QtWidgets.QVBoxLayout(self.data_widget)
        self.data_layout.setContentsMargins(4, 4, 4, 4)
        self.data_layout.setSpacing(3)
        self.data_layout.setObjectName("data_layout")
        self.checkbox_layout = QtWidgets.QHBoxLayout()
        self.checkbox_layout.setSpacing(3)
        self.checkbox_layout.setObjectName("checkbox_layout")
        self.checkbox_time = QtWidgets.QCheckBox(self.data_widget)
        self.checkbox_time.setObjectName("checkbox_time")
        self.checkbox_layout.addWidget(self.checkbox_time)
        self.checkbox_geo = QtWidgets.QCheckBox(self.data_widget)
        self.checkbox_geo.setChecked(False)
        self.checkbox_geo.setObjectName("checkbox_geo")
        self.checkbox_layout.addWidget(self.checkbox_geo)
        self.checkbox_depth = QtWidgets.QCheckBox(self.data_widget)
        self.checkbox_depth.setObjectName("checkbox_depth")
        self.checkbox_layout.addWidget(self.checkbox_depth)
        self.data_layout.addLayout(self.checkbox_layout)
        self.data_tree = DataTree(self.data_widget)
        self.data_tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.data_tree.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.data_tree.setIndentation(10)
        self.data_tree.setWordWrap(True)
        self.data_tree.setHeaderHidden(False)
        self.data_tree.setObjectName("data_tree")
        self.data_tree.headerItem().setText(0, "Variable")
        self.data_layout.addWidget(self.data_tree)
        self.filter_layout = QtWidgets.QHBoxLayout()
        self.filter_layout.setSpacing(3)
        self.filter_layout.setObjectName("filter_layout")
        self.label_path = QtWidgets.QLabel(self.data_widget)
        self.label_path.setObjectName("label_path")
        self.filter_layout.addWidget(self.label_path)
        self.data_regexp = QtWidgets.QLineEdit(self.data_widget)
        self.data_regexp.setText("")
        self.data_regexp.setObjectName("data_regexp")
        self.filter_layout.addWidget(self.data_regexp)
        self.data_layout.addLayout(self.filter_layout)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(3)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_var = QtWidgets.QLabel(self.data_widget)
        self.label_var.setObjectName("label_var")
        self.horizontalLayout.addWidget(self.label_var)
        self.var_regexp = QtWidgets.QLineEdit(self.data_widget)
        self.var_regexp.setObjectName("var_regexp")
        self.horizontalLayout.addWidget(self.var_regexp)
        self.data_layout.addLayout(self.horizontalLayout)
        self.data_dock.setWidget(self.data_widget)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.data_dock)
        self.figures_dock = QtWidgets.QDockWidget(MainWindow)
        self.figures_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable|QtWidgets.QDockWidget.DockWidgetMovable)
        self.figures_dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        self.figures_dock.setObjectName("figures_dock")
        self.figures_widget = QtWidgets.QWidget()
        self.figures_widget.setObjectName("figures_widget")
        self.figures_layout = QtWidgets.QVBoxLayout(self.figures_widget)
        self.figures_layout.setContentsMargins(4, 4, 4, 4)
        self.figures_layout.setSpacing(3)
        self.figures_layout.setObjectName("figures_layout")
        self.figures_tree = FiguresTree(self.figures_widget)
        self.figures_tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.figures_tree.setAutoFillBackground(False)
        self.figures_tree.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        self.figures_tree.setAlternatingRowColors(True)
        self.figures_tree.setIndentation(10)
        self.figures_tree.setAllColumnsShowFocus(False)
        self.figures_tree.setWordWrap(True)
        self.figures_tree.setObjectName("figures_tree")
        self.figures_tree.headerItem().setText(0, "key")
        self.figures_tree.header().setSortIndicatorShown(False)
        self.figures_layout.addWidget(self.figures_tree)
        self.figures_dock.setWidget(self.figures_widget)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.figures_dock)
        self.open_files = QtWidgets.QAction(MainWindow)
        self.open_files.setObjectName("open_files")
        self.menuFile.addAction(self.open_files)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        self.figures_tab_dock.setCurrentIndex(-1)
        self.data_regexp.textChanged['QString'].connect(self.data_tree.update)
        self.var_regexp.textChanged['QString'].connect(self.data_tree.update)
        self.open_files.triggered.connect(self.data_tree.open_files)
        self.checkbox_depth.stateChanged['int'].connect(self.data_tree.update)
        self.checkbox_geo.stateChanged['int'].connect(self.data_tree.update)
        self.checkbox_time.stateChanged['int'].connect(self.data_tree.update)
        self.data_tree.customContextMenuRequested['QPoint'].connect(self.data_tree.context_menu)
        self.figures_tree.customContextMenuRequested['QPoint'].connect(self.figures_tree.context_menu)
        self.figures_tree.itemChanged['QTreeWidgetItem*','int'].connect(self.figures_tree.item_changed)
        self.figures_tree.itemDoubleClicked['QTreeWidgetItem*','int'].connect(self.figures_tree.edit_item)
        self.figures_tree.update_figures.connect(self.figures_tab_dock.update_figures)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.data_tree, self.figures_tree)
        MainWindow.setTabOrder(self.figures_tree, self.figures_tab_dock)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.data_dock.setWindowTitle(_translate("MainWindow", "Data Store"))
        self.checkbox_time.setText(_translate("MainWindow", "Time"))
        self.checkbox_geo.setText(_translate("MainWindow", "Geo"))
        self.checkbox_depth.setText(_translate("MainWindow", "Depth"))
        self.data_tree.setSortingEnabled(True)
        self.label_path.setText(_translate("MainWindow", "Files"))
        self.data_regexp.setPlaceholderText(_translate("MainWindow", "Regexp to apply on dataset"))
        self.label_var.setText(_translate("MainWindow", "Var"))
        self.var_regexp.setPlaceholderText(_translate("MainWindow", "Regexp to apply on variable"))
        self.figures_dock.setWindowTitle(_translate("MainWindow", "Figures"))
        self.figures_tree.setSortingEnabled(False)
        self.figures_tree.headerItem().setText(1, _translate("MainWindow", "value"))
        self.open_files.setText(_translate("MainWindow", "Open"))

from .data_tree import DataTree
from .figures_tree import FiguresTree
from .tabs import TabWidget
from . import resource_rc
