
from PyQt5 import QtWidgets, QtGui

class TabWidget(QtWidgets.QTabWidget):

    """Custom tab widget."""

    def __init__(self, parent=None, *args, **kwargs):
        super(TabWidget, self).__init__(parent=None, *args, **kwargs)
        self.parent = parent

    def make_undock(self):
        """Undock a Tab from TabWidget and promote to a Dialog."""
        dialog, index = QtWidgets.QDialog(self), self.currentIndex()
        widget_from_tab = self.widget(index)
        dialog.setWindowTitle(self.tabText(index))
        dialog_layout = QtWidgets.QVBoxLayout(dialog)
        dialog.setGeometry(widget_from_tab.geometry())

        def closeEvent_override(event):
            """Re-dock back from Dialog to a new Tab."""
            msg = "<b>Close this Floating Tab Window and Re-Dock as a new Tab?"
            conditional = QtWidgets.QMessageBox.question(
                self, "Undocked Tab", msg, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes
            if conditional:
                self.insertTab(self.count() + 1, widget_from_tab, dialog.windowTitle())
                return event.accept()
            else:
                return event.ignore()

        dialog.closeEvent = closeEvent_override
        self.removeTab(index)
        widget_from_tab.setParent(self.parent if self.parent else dialog)
        dialog_layout.addWidget(widget_from_tab)
        dialog.setLayout(dialog_layout)
        widget_from_tab.show()
        dialog.show()  # exec_() for modal dialog, show() for non-modal dialog
        dialog.move(QtGui.QCursor.pos())

