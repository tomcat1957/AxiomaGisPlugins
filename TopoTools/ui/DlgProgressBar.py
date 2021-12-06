import os
import time

from PySide2 import QtCore
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QDialog


class DlgProgressBar(QDialog):
    __clsRunProcess=None
    __isCancel=False
    __time_start = None
    __def_title="Process"
    __isRunProcess=True
    __text_process=None
    __curentValue=0
    __lastLabel=None
    def __init__(self,runCls=None,parent=None):
        self.__clsRunProcess=runCls
        self.__parent=parent
        self.load_ui()
        self.window.pb_cancel.clicked.connect(self.__cancel)
    def __cancel(self):
        #print("Click Cancel")
        self.__isCancel=True
    @property
    def isCancel(self):
        return self.__isCancel
    def setTitle(self,title_text):
        self.__def_title=title_text
        self.window.setWindowTitle(title_text)
    def setSize(self,width,height):
        self.window.resize(width,height)
    def setTextProcess(self,text):
        print(text)
        self.__text_process=text
    def exec(self,count=100):

        self.__count=count
        self.window.prg_bar.setMaximum(count)

        self.__clsRunProcess.countChanged.connect(self.onCountChanged)
        self.__clsRunProcess.endProcess.connect(self.processEnd)
        self.__clsRunProcess.updateHead.connect(self.processUpdateHead)
        self.__clsRunProcess.updateNameProcess.connect(self.processUpdateProcessName)

        self.__time_start = time.time()
        self.window.prg_bar.setValue(0)
        self.setTitle(self.__def_title)
        self.__clsRunProcess.start()
        self.show()


        #self.__clsRunProcess.start()
    def onCountChanged(self, value):
        #print("Change progressar value:"+str(value))
        if value<0:
            self.window.prg_bar.setValue(self.__count)
            self.close()
            return
        self.__curentValue=value
        self.window.prg_bar.setValue(value)
        curDeltaTime = (time.time() - self.__time_start)
        timeToEnd = self.__calcTimeToEnd(curDeltaTime, value)
        str_label = str(float("{0:.1f}".format((curDeltaTime)))) + " " + "(" + "{0:.1f}".format(timeToEnd) + ") sec"
        if self.__text_process is not None:
            str_label=self.__text_process+"  "+str_label
            self.__lastLabel=str_label
        self.window.label_time.setText(str_label)
    def __calcTimeToEnd(self, curent_delta_time, value):
        if value <= 0.0:
            return 0
        time_to_tic = curent_delta_time / value
        timeToEnd = (self.__count - value) * time_to_tic
        return timeToEnd
    def processUpdateHead(self,head_text):
        if head_text is not None:
            self.__def_title = head_text
            self.windows.setWindowTitle(head_text)
    def processEnd(self,type_end):
        #print ("processEnd")
        self.__isRunProcess=False
        self.window.prg_bar.setValue(self.__count)
        #self.self.__clsRunProcess.countChanged.disconnect(self.onCountChanged)
        self.window.close()
    def processUpdateProcessName(self,text):
        self.window.label_time.setText(text)
    def load_ui(self):
        loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), "DlgProgressBar.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.window  = loader.load(ui_file,self.__parent)
        ui_file.close()
        #self.window.setWindowModality(QtCore.Qt.ApplicationModal)
        self.window.setWindowFlags(
            self.window.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint & ~QtCore.Qt.WindowContextHelpButtonHint)
    def show(self):
        #self.window.setParent(self.__parent)
        self.window.exec_()


