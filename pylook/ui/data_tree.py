import os.path
import re
from PyQt5 import QtWidgets, QtGui, QtCore
from ..data import data_store


def merged_icons(icons):
    if len(icons) == 1:
        return QtGui.QIcon(icons[0])
    else:
        pixmaps = list()
        pixmap = QtGui.QPixmap(len(icons) * 16, 16)
        painter = QtGui.QPainter(pixmap)
        for i, icon in enumerate(icons):
            painter.drawPixmap(i * 16, 0, QtGui.QPixmap(icon))
        painter.end()
        return QtGui.QIcon(pixmap)


class DataTree(QtWidgets.QTreeWidget):

    GEO_ICON = ":icons/images/geo.svg"
    DEPTH_ICON = ":icons/images/depth.svg"
    TIME_ICON = ":icons/images/time.png"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_store = data_store.DataStore()
        self.setIconSize(QtCore.QSize(48, 16))
        self.states = dict(
            data_regexp=None,
            var_regexp=None,
            checkbox_geo=None,
            checkbox_time=None,
            checkbox_depth=None,
        )

    def path_leaf(self, dataset):
        leaf = QtWidgets.QTreeWidgetItem()
        leaf.setText(0, dataset.last_name)
        leaf.setToolTip(0, dataset.dirname)
        leaf.setData(0, 3, dataset.key)
        leaf.setIcon(0, QtGui.QIcon())
        for variable in dataset:
            self.variable_leaf(leaf, variable)
        return leaf

    @classmethod
    def variable_leaf(cls, parent, variable):
        leaf = QtWidgets.QTreeWidgetItem(parent)
        leaf.setText(0, variable.name)
        icons = list()
        if variable.geo_coordinates:
            icons.append(cls.GEO_ICON)
            leaf.setData(0, 3, True)
        if variable.time_coordinates:
            icons.append(cls.TIME_ICON)
            leaf.setData(0, 4, True)
        if variable.depth_coordinates:
            icons.append(cls.DEPTH_ICON)
            leaf.setData(0, 5, True)
        if len(icons) > 0:
            leaf.setIcon(0, merged_icons(icons))

    def populate(self):
        files_present = [
            self.topLevelItem(i).data(0, 3) for i in range(self.topLevelItemCount())
        ]
        elts = list()
        for dataset in self.data_store:
            if dataset.key in files_present:
                continue
            elts.append(self.path_leaf(dataset))
        if len(elts):
            self.addTopLevelItems(elts)
            self.apply_filter()

    def apply_filter(self):
        for i in range(self.topLevelItemCount()):
            path_leaf = self.topLevelItem(i)
            child_hiden = 0
            nb_child = path_leaf.childCount()
            for j in range(nb_child):
                var_leaf = path_leaf.child(j)
                var_name, is_geo, is_time, is_depth = (
                    var_leaf.data(0, 0),
                    var_leaf.data(0, 3),
                    var_leaf.data(0, 4),
                    var_leaf.data(0, 5),
                )
                var_match = True
                if self.states["var_regexp"]:
                    var_match = self.states["var_regexp"](var_name) is not None
                if (
                    (self.states["checkbox_geo"] and not is_geo)
                    or (self.states["checkbox_time"] and not is_time)
                    or (self.states["checkbox_depth"] and not is_depth)
                    or not var_match
                ):
                    var_leaf.setHidden(True)
                    child_hiden += 1
                    continue

                var_leaf.setHidden(False)
            file_match = True
            if self.states["data_regexp"]:
                file_match = (
                    self.states["data_regexp"](path_leaf.data(0, 3)) is not None
                )
            path_leaf.setHidden(child_hiden == nb_child or not file_match)

    def context_menu(self, event):
        menu = QtWidgets.QMenu(self)
        menu.addSeparator()
        menu.addAction("Collapse all", self.collapseAll)
        menu.addAction("Expand all", self.expandAll)
        menu.exec(self.mapToGlobal(event))

    def update(self, event):
        sender = self.sender().objectName()
        if "regexp" in sender:
            try:
                self.states[sender] = re.compile(event).search
            except:
                pass
        else:
            self.states[sender] = event != 0
        self.apply_filter()

    def open_files(self, event):
        filenames, extension = QtWidgets.QFileDialog.getOpenFileNames(
            caption="File(s) to explore",
            initialFilter=self.compile_filter(self.data_store.known_extensions[:1]),
            filter=self.compile_filter(self.data_store.known_extensions),
        )
        self.data_store.add_paths(filenames)
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
