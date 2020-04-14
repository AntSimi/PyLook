import os.path
import re
from PyQt5 import QtWidgets, QtGui, QtCore
from ..data import data_store


def merged_icons(icons):
    if len(icons) == 1:
        return QtGui.QIcon(icons[0])
    else:
        pixmaps = list()
        pixmap = QtGui.QPixmap(len(icons) * 16,16)
        painter = QtGui.QPainter(pixmap)
        for i, icon in enumerate(icons):
            painter.drawPixmap(i * 16, 0, QtGui.QPixmap(icon))
        painter.end()
        return QtGui.QIcon(pixmap)


class DataTree(QtWidgets.QTreeWidget):

    def __init__(self, *args, **kwargs):
        super(DataTree, self).__init__(*args, **kwargs)
        self.data_store = data_store.DataStore()
        self.geo_icon = ":icons/images/geo.svg"
        self.depth_icon = ":icons/images/depth.svg"
        self.time_icon = ":icons/images/time.png"
        self.setIconSize(QtCore.QSize(48,16))

    def path_leaf(self, dataset):
        elt = QtWidgets.QTreeWidgetItem()
        elt.setText(0, dataset.last_name)
        elt.setToolTip(0, dataset.dirname)
        elt.setData(0, 1, dataset.key)
        for variable in dataset:
            child = QtWidgets.QTreeWidgetItem(elt)
            child.setText(0, variable.name)
            icons = list()
            if variable.geo_coordinates:
                icons.append(self.geo_icon)
            if variable.time_coordinates:
                icons.append(self.time_icon)
            if variable.depth_coordinates:
                icons.append(self.depth_icon)
            if len(icons) > 0:
                child.setIcon(0, merged_icons(icons))
        return elt
    
    def populate(self):
        files_present = [
            self.topLevelItem(i).data(0, 1) for i in range(self.topLevelItemCount())
        ]
        elts = list()
        for dataset in self.data_store:
            if dataset.key in files_present:
                continue
            elts.append(self.path_leaf(dataset))
        self.addTopLevelItems(elts)

    def update(self, event):
        sender = self.sender().objectName()
        if sender in ["data_regexp", "var_regexp"]:
            try:
                expr = re.compile(event).search
            except:
                return
            for i in range(self.topLevelItemCount()):
                elt = self.topLevelItem(i)
                if sender == "data_regexp":
                    elt.setHidden(expr(elt.data(0, 1)) is None)
        elif sender == "open_files":
            filenames, extension = QtWidgets.QFileDialog.getOpenFileNames(
                caption="File(s) to explore",
                initialFilter=self.compile_filter(self.data_store.known_extensions[:1]),
                filter=self.compile_filter(self.data_store.known_extensions),
            )
            self.data_store.add_files(filenames)
            self.populate()

    @staticmethod
    def compile_filter(filetypes):
        if len(filetypes) == 1:
            caption, extensions = filetypes[0]
            return f'{caption} ({" ".join(extensions)})'
        else:
            exps = list()
            for filetype in filetypes:
                caption, extensions = filetype
                exps.append(f'{caption} ({" ".join(extensions)})')
            return ";;".join(exps)

