import json
from PyQt5 import QtWidgets, QtGui, QtCore
from ..exchange_object import (
    FigureSet,
    Figure,
    GeoSubplot,
    Base as BaseObject,
    Bool,
    Choices,
    as_pylook_object,
)


class ComboBoxItem(QtWidgets.QComboBox):
    INDEX_PREVIOUS = 5

    def __init__(self, parent, leaf, choices):
        super().__init__(parent)
        self.leaf = leaf
        self.setEditable(True)
        self.addItems(choices)
        self.activated.connect(self.combo_done)

    def combo_done(self, event):
        value = self.currentText()
        self.leaf.setText(1, value)
        self.leaf.setData(0, self.INDEX_PREVIOUS, value)


class FiguresTree(QtWidgets.QTreeWidget):

    INDEX_INIT = 4
    INDEX_PREVIOUS = 5

    update_figures = QtCore.Signal(list)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_tree()

    @classmethod
    def get_exchange_object(cls, leaf, with_key=False):
        data = leaf.data(0, 4)
        if with_key:
            name = leaf.text(0)
            if isinstance(data, BaseObject):
                return data, [name]
            else:
                data, names = cls.get_exchange_object(leaf.parent(), with_key=with_key)
                names.append(name)
                return data, names
        else:
            return (
                data
                if isinstance(data, BaseObject)
                else cls.get_exchange_object(leaf.parent())
            )

    @classmethod
    def set_exchange_object(cls, leaf, value):
        e_object, keys = cls.get_exchange_object(leaf, with_key=True)
        cls.set_option_dict(e_object.options, keys[keys.index("options") + 1 :], value)

    @classmethod
    def set_option_dict(cls, options, keys, value):
        if len(keys) == 1:
            options[keys[0]] = value
        else:
            cls.set_option_dict(options[keys[0]], keys[1:], value)

    def edit_item(self, leaf, j):
        if j != 1:
            return False
        flags = leaf.flags()
        if flags & QtCore.Qt.ItemIsTristate:
            leaf.setData(0, self.INDEX_PREVIOUS, leaf.text(j))
            leaf.setFlags(flags | QtCore.Qt.ItemIsEditable)
            self.editItem(leaf, j)
            leaf.setFlags(flags)

    def item_changed(self, leaf, j):
        if j != 1:
            return False
        current_value = leaf.text(j)
        previous = leaf.data(0, self.INDEX_PREVIOUS)
        if leaf.flags() & QtCore.Qt.ItemIsUserCheckable:
            current_value = str(leaf.checkState(1) != 0)
            leaf.setData(0, self.INDEX_PREVIOUS, current_value)
            leaf.setText(j, str(leaf.checkState(1) != 0))
        if previous == current_value:
            return False
        try:
            eval(current_value)
        except:
            leaf.setText(j, previous)
            # FIXME : Case combobox not well manage
            return False
        self.set_exchange_object(leaf, current_value)
        self.tree_to_figures()

    def context_menu(self, event):
        leaf = self.itemAt(event)
        menu = QtWidgets.QMenu(self)
        menu.addAction("Add Figures Set", self.add_figures_set)
        # menu.addAction("test", self.tree_to_figures)
        if leaf:
            e_object = self.get_exchange_object(leaf)
            if isinstance(e_object, FigureSet):
                action = menu.addAction(
                    "Save this Figures Set", self.save_object_dialog
                )
                action.setData(leaf)
            menu.addSeparator()
            for child in e_object.known_children:
                action = menu.addAction(f"Add {child.__name__}", self.add_child)
                action.setData((leaf, child))
        menu.addSeparator()
        menu.addAction("Collapse all", self.collapseAll)
        menu.addAction("Expand all", self.expandAll)
        menu.exec(self.mapToGlobal(event))

    def add_child(self, leaf=None, class_object=None):
        if leaf is None:
            leaf, class_object = self.sender().data()
        return self.add_leaf_from_exchange_object(leaf, class_object())

    def add_figures_set(self):
        set_object = FigureSet()
        return self.add_leaf_from_exchange_object(self, set_object)

    def init_tree(self):
        leaf = self.add_figures_set()
        leaf = self.add_child(leaf, Figure)
        leaf = self.add_child(leaf, GeoSubplot)
        # self.set_options(leaf, dict(title="'Mon premier titre'", xlabel="'Longitude'"))
        return leaf

    def set_options(self, leaf, options):
        pass

    def add_options_to_a_leaf(self, leaf, options, init_options, help_):
        keys = list(options.keys())
        keys.sort()
        for k in keys:
            v = options[k]
            leaf_ = QtWidgets.QTreeWidgetItem(leaf)
            leaf_.setText(0, k)
            if isinstance(v, dict):
                self.add_options_to_a_leaf(
                    leaf_, v, init_options[k], help_.get(k, dict())
                )
            else:
                leaf_.setText(1, v)
                leaf_.setData(0, self.INDEX_INIT, v)
                leaf_.setData(0, self.INDEX_PREVIOUS, v)
                leaf_.setFlags(QtCore.Qt.ItemIsTristate | QtCore.Qt.ItemIsEnabled)
                help__ = help_.get(k, dict())
                if "doc" in help__:
                    leaf_.setToolTip(0, help__["doc"])
                    leaf_.setToolTip(1, help__["doc"])

                init_value = init_options[k]
                if isinstance(init_value, Choices):
                    if isinstance(init_value, Bool):
                        leaf_.setFlags(
                            QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled
                        )
                        leaf_.setCheckState(
                            1, QtCore.Qt.Checked if eval(v) else QtCore.Qt.Unchecked
                        )
                    else:
                        self.setItemWidget(
                            leaf_, 1, ComboBoxItem(self, leaf_, init_value)
                        )

    def add_leaf_from_exchange_object(self, parent, model):
        self.blockSignals(True)
        leaf = QtWidgets.QTreeWidgetItem(parent)
        leaf.setText(0, model.name)
        for i in range(leaf.columnCount() + 1):
            leaf.setBackground(i, QtGui.QBrush((QtGui.QColor(model.QT_COLOR))))
        leaf.setData(0, 4, model)
        leaf_options = QtWidgets.QTreeWidgetItem(leaf)
        leaf_options.setText(0, "options")
        self.add_options_to_a_leaf(
            leaf_options, model.options, model.init_value, model.help
        )
        self.blockSignals(False)
        self.expand(self.indexFromItem(leaf_options))
        self.expand(self.indexFromItem(leaf))
        return leaf

    def get_objects(self, leaf=None):
        out = list()
        for i in range(leaf.childCount() if leaf else self.topLevelItemCount()):
            child_leaf = leaf.child(i) if leaf else self.topLevelItem(i)
            data = child_leaf.data(0, 4)
            if isinstance(data, BaseObject):
                data = data.copy()
                data.appends(*self.get_objects(child_leaf))
                out.append(data)
        return out

    def tree_to_figures(self):
        self.update_figures.emit(self.get_objects())

    def save_object_dialog(self):
        figure_set = self.get_objects(self.sender().data())[0]
        filename, extension = QtWidgets.QFileDialog.getSaveFileName(
            caption="Object to save", filter="PyLook object file (*.plk)",
        )
        figure_set.save(filename)

    def load_object_dialog(self, event):
        filename, extension = QtWidgets.QFileDialog.getOpenFileName(
            caption="Object to save", filter="PyLook object file (*.plk)",
        )
        with open(filename) as f:
            loading_object = json.load(f, object_hook=as_pylook_object)
        print(loading_object)
