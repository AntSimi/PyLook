import os.path
import re
from PyQt5 import QtWidgets
from ..data import data_store

class DataTree(QtWidgets.QTreeWidget):
      
    def populate(self):
        d = data_store.DataStore()
        elts = list()
        for filename in d.files:
            elt = QtWidgets.QTreeWidgetItem()
            elt.setText(0, os.path.basename(filename))
            elt.setToolTip(0, os.path.dirname(filename))
            elt.setData(0, 1, filename)
            elts.append(elt)
        self.addTopLevelItems(elts)

    def update(self, event):
        sender = self.sender().objectName()
        try:
            expr = re.compile(event).search
        except:
            return 
        for i in range(self.topLevelItemCount()):
            elt = self.topLevelItem(i)
            if sender == 'data_regexp':
                elt.setHidden(expr(elt.data(0,1)) is None)
            
