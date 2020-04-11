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
        MainWindow.setDockOptions(QtWidgets.QMainWindow.AllowTabbedDocks|QtWidgets.QMainWindow.AnimatedDocks|QtWidgets.QMainWindow.VerticalTabs)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.figures_tab_dock = TabWidget(self.centralwidget)
        self.figures_tab_dock.setObjectName("figures_tab_dock")
        self.start_tab = QtWidgets.QWidget()
        self.start_tab.setObjectName("start_tab")
        self.figures_tab_dock.addTab(self.start_tab, "")
        self.verticalLayout.addWidget(self.figures_tab_dock)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
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
        self.data_layout.setObjectName("data_layout")
        self.data_tree = QtWidgets.QTreeWidget(self.data_widget)
        self.data_tree.setObjectName("data_tree")
        self.data_tree.headerItem().setText(0, "1")
        self.data_layout.addWidget(self.data_tree)
        self.data_dock.setWidget(self.data_widget)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.data_dock)
        self.figures_dock = QtWidgets.QDockWidget(MainWindow)
        self.figures_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable|QtWidgets.QDockWidget.DockWidgetMovable)
        self.figures_dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        self.figures_dock.setObjectName("figures_dock")
        self.figures_widget = QtWidgets.QWidget()
        self.figures_widget.setObjectName("figures_widget")
        self.figures_layout = QtWidgets.QVBoxLayout(self.figures_widget)
        self.figures_layout.setObjectName("figures_layout")
        self.figures_tree = QtWidgets.QTreeWidget(self.figures_widget)
        self.figures_tree.setObjectName("figures_tree")
        self.figures_tree.headerItem().setText(0, "1")
        self.figures_layout.addWidget(self.figures_tree)
        self.figures_dock.setWidget(self.figures_widget)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.figures_dock)
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.menuFile.addAction(self.actionOpen)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        self.figures_tab_dock.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.data_tree, self.figures_tree)
        MainWindow.setTabOrder(self.figures_tree, self.figures_tab_dock)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.figures_tab_dock.setTabText(self.figures_tab_dock.indexOf(self.start_tab), _translate("MainWindow", "Tab 1"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.data_dock.setWindowTitle(_translate("MainWindow", "Data Store"))
        self.figures_dock.setWindowTitle(_translate("MainWindow", "Figures"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))

from .tabs import TabWidget
