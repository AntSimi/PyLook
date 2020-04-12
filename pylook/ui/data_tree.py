import os.path
import re
from PyQt5 import QtWidgets
from ..data import data_store

class DataTree(QtWidgets.QTreeWidget):
      
    def __init__(self, *args, **kwargs):
        super(DataTree, self).__init__(*args, **kwargs)
        self.data_store = data_store.DataStore()

    def populate(self):
        files_present = [self.topLevelItem(i).data(0, 1) for i in range(self.topLevelItemCount())]
        elts = list()
        for filename in self.data_store.files:
            if filename in files_present:
                continue
            elt = QtWidgets.QTreeWidgetItem()
            elt.setText(0, os.path.basename(filename))
            elt.setToolTip(0, os.path.dirname(filename))
            elt.setData(0, 1, filename)
            elts.append(elt)
        self.addTopLevelItems(elts)

    def update(self, event):
        sender = self.sender().objectName()
        if sender in ['data_regexp', 'var_regexp']:
            try:
                expr = re.compile(event).search
            except:
                return 
            for i in range(self.topLevelItemCount()):
                elt = self.topLevelItem(i)
                if sender == 'data_regexp':
                    elt.setHidden(expr(elt.data(0,1)) is None)
        elif sender == 'open_files':
            filenames, extension = QtWidgets.QFileDialog.getOpenFileNames(
                caption='File(s) to explore',
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
            return ';;'.join(exps)

            
