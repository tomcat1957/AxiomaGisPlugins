import inspect
import os

from PyQt5.uic import loadUi
from PySide2 import QtCore
from PySide2.QtCore import QFile
from PySide2.QtGui import Qt

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QDialog

class DlgTopo(QDialog):
    def __init__(self, parent=None):
        self.__parent=parent
        #super(DlgTopo, self).__init__(parent)
        #self.setWindowModality(QtCore.Qt.ApplicationModal)

        # cwd = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        '''Load config'''
        # ui_file = self.iface.local_file('ui', 'ImportXmlPkkDlg.ui')

        # self.__ui = QUiLoader().load(os.path.join(cwd, "ImportXmlPkkDlg.ui"))
        # loadUi(os.path.join(cwd, "ImportXmlPkkDlg.ui"), self)
        self.load_ui()

    def load_ui(self):
        loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), "DlgTest2.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.window  = loader.load(ui_file,self.__parent)
        ui_file.close()
        #self.window.setWindowModality(QtCore.Qt.ApplicationModal)
        self.window.setWindowFlags(
            self.window.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint & ~QtCore.Qt.WindowContextHelpButtonHint)
    def show(self):
        #self.window.setParent(self.__parent)
        self.window.exec()