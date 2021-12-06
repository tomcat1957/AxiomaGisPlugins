from PySide2.QtCore import QThread, Signal



class SimpleProgress:
    __isOk=True
    def __init__(self,parent_cls):
        self.__parent=parent_cls

    def show(self):
        self.__parent.ClsProgressBar().show()
    def setValue(self,value):
        self.__parent.countChanged.emit(value)
        self.__isOk=not self.__parent.ClsProgressBar().isCancel
    def setCount(self,count):
        self.__parent.ClsProgressBar().setCount(count)
    def setEnabled(self,value):
        self.__parent.ClsProgressBar().CancelEnabled(value)

    @property
    def isOk(self):
        return self.__isOk
class BasicProcess(QThread):
    countChanged = Signal(int)
    endProcess=Signal(int)

    updateHead = Signal(str)
    updateNameProcess = Signal(str)
    __count=None
    __clsProgress=None

    def setClsProgressBar(self,cls_progressBar):
        self.__clsProgress=cls_progressBar
    def run(self):
        pass
    def calcProcent(self,curent_value):
        proc_val=(curent_value/self.__count)*100.0
        return int(proc_val)
    @property
    def Count(self):
        return self.__count
    def ClsProgressBar(self):
        return self.__clsProgress
class RunThread(BasicProcess):
    __run_method=None
    __count_method=None
    __count=0
    def __init__(self,cls_main,name_method,text_progress):
        self.__base_cls=cls_main
        self.__name_method=name_method
        self.__textHeader=text_progress
        super().__init__()
    def prepare(self):
        try:
            self.__run_method=getattr(self.__base_cls,self.__name_method)
            self.__count_method=getattr(self.__base_cls,"Count")
            self.__count=self.__count_method()
            return True
        except:
            return False

    @property
    def Count(self):
        return self.__count

    def __isCancel(self):
        self.endProcess.emit(0)

    def run(self):
        print('Start Run')

        self.ClsProgressBar().setTextProcess(self.__textHeader)
        self.__base_cls.run()
        self.endProcess.emit(0)