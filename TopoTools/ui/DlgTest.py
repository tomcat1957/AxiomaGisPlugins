import os

from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader


class DlgTest():
    def __init__(self,parent=None):
            loader = QUiLoader()
            path = os.path.join(os.path.dirname(__file__), "CustomDialog.ui")
            ui_file = QFile(path)
            ui_file.open(QFile.ReadOnly)
            self.window = loader.load(ui_file)
            ui_file.close()
    def show(self):
        self.window.exec()