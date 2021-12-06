import os

import axipy
from PySide2 import QtCore
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader


class DlgAddTable:
    __statusIsOk=False
    __name_tab=None
    def __init__(self,name_tab):
        self.__name_tab=name_tab
        self.__parentWin=axipy.app.mainwindow.qt_object()
        self.load_ui()
        self.window.label_name_table.setText(self.__name_tab)
        self.__initOpenMap()
        self.window.pb_cancel.clicked.connect(self.__close)
        self.window.pb_add.clicked.connect(self.__add_table)
    def load_ui(self):
        loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), "DlgAddTableToMap.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.window  = loader.load(ui_file,self.__parentWin)
        ui_file.close()
        #self.window.setWindowModality(QtCore.Qt.ApplicationModal)
        self.window.setWindowFlags(
          self.window.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint & ~QtCore.Qt.WindowContextHelpButtonHint)
    def show(self):
        self.window.exec()
    def __add_table(self):
        self.__statusIsOk=True
        self.window.close()
    @property
    def nameMapView(self):
        if not self.__statusIsOk:
            return None
        return self.window.cb_list_map_windows.currentText()
    def __close(self):
        self.__statusIsOk=False
        self.window.close()
    def __initOpenMap(self):
        for view_map in axipy.gui.view_manager.views:
            if isinstance(view_map,axipy.MapView):
                name=view_map.widget.windowTitle()
                self.window.cb_list_map_windows.addItem(name)
