from PyQt5 import QtWidgets, QtGui, QtCore
from ..exchange_object import FigureSet, Figure, Subplot, Base as BaseObject


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
    def get_exchange_object(cls, leaf):
        data = leaf.data(0, 4)
        name = leaf.text(0)
        if data:
            return data
        else:
            return cls.get_exchange_object(leaf.parent()), name

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
        if previous == current_value:
            return False
        try:
            eval(current_value)
        except:
            leaf.setText(j, previous)
            # FIXME : Case combobox not well manage
            return False

    def context_menu(self, event):
        leaf = self.itemAt(event)
        menu = QtWidgets.QMenu(self)
        menu.addSeparator()
        menu.addAction("Add Figures Set", self.add_figures_set)
        if leaf and leaf.data(0, 4):
            e_object = leaf.data(0, 4)
            menu.addSeparator()
            for child in e_object.known_children:
                action = menu.addAction(f"Add {child.__name__}", self.add_child)
                action.setData((leaf, child))
        menu.exec(self.mapToGlobal(event))

    def add_child(self, leaf=None, class_object=None):
        if leaf is None:
            sender = self.sender()
            leaf, class_object = sender.data()
        return self.add_leaf_from_exchange_object(leaf, class_object())

    def add_figures_set(self):
        set_object = FigureSet()
        return self.add_leaf_from_exchange_object(self, set_object)

    def init_tree(self):
        leaf = self.add_figures_set()
        leaf = self.add_child(leaf, Figure)
        return self.add_child(leaf, Subplot)

    def add_options_to_a_leaf(self, leaf, options, init_options):
        keys = list(options.keys())
        keys.sort()
        for k in keys:
            v = options[k]
            leaf_ = QtWidgets.QTreeWidgetItem(leaf)
            leaf_.setText(0, k)
            if isinstance(v, dict):
                self.add_options_to_a_leaf(leaf_, v, init_options[k])
            else:
                leaf_.setText(1, v)
                leaf_.setData(0, self.INDEX_INIT, v)
                leaf_.setData(0, self.INDEX_PREVIOUS, v)
                leaf_.setFlags(leaf_.flags() | QtCore.Qt.ItemIsTristate)
                init_value = init_options[k]
                if isinstance(init_value, list):
                    self.setItemWidget(leaf_, 1, ComboBoxItem(self, leaf_, init_value))

    def add_leaf_from_exchange_object(self, parent, model):
        leaf = QtWidgets.QTreeWidgetItem(parent)
        leaf.setText(0, model.name)
        for i in range(leaf.columnCount() + 1):
            leaf.setBackground(i, QtGui.QBrush((QtGui.QColor(model.QT_COLOR))))
        # leaf.setToolTip(0, dataset.summary(child=False, full=True))
        leaf.setData(0, 4, model)
        leaf_options = QtWidgets.QTreeWidgetItem(leaf)
        leaf_options.setText(0, "options")
        self.add_options_to_a_leaf(leaf_options, model.options, model.init_value)
        self.expand(self.indexFromItem(leaf_options))
        self.expand(self.indexFromItem(leaf))
        return leaf

    def get_objects(self, leaf=None):
        out = list()
        for i in range(leaf.childCount() if leaf else self.topLevelItemCount()):
            child_leaf = leaf.child(i) if leaf else self.topLevelItem(i)
            data = child_leaf.data(0, 4)
            if isinstance(data, BaseObject):
                data.appends(*self.get_objects(child_leaf))
                out.append(data)
        return out

    def tree_to_figures(self):
        self.update_figures.emit(self.get_objects())
