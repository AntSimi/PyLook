from PyQt5 import QtWidgets, QtGui


class TabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(TabWidget, self).__init__(parent=None, *args, **kwargs)
        self.parent = parent
        self.tabBarDoubleClicked.connect(self.onTabBarClicked)

    def onTabBarClicked(self, index):
        if self.count() > 1:
            self.make_undock(index)

    def make_undock(self, index):
        """Undock a Tab from TabWidget and promote to a Dialog."""
        window = QtWidgets.QMainWindow(self)
        widget_from_tab = self.widget(index)
        window.setWindowTitle(self.tabText(index))
        window.setGeometry(widget_from_tab.geometry())

        def closeEvent_override(event):
            """Re-dock back from Dialog to a new Tab."""
            self.insertTab(self.count() + 1, widget_from_tab, window.windowTitle())
            return event.accept()
            # msg = "<b>Do you want re-dock as a new tab?"
            # conditional = QtWidgets.QMessageBox.question(
            #     self, "Undocked Tab", msg, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            #     QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes
            # if conditional:
            #     self.insertTab(self.count() + 1, widget_from_tab, dialog.windowTitle())
            #     return event.accept()
            # else:
            #     return event.ignore()

        window.closeEvent = closeEvent_override
        self.removeTab(index)
        widget_from_tab.setParent(self.parent if self.parent else window)
        window.setCentralWidget(widget_from_tab)
        widget_from_tab.show()
        window.show()
        window.move(QtGui.QCursor.pos())
