import time

from PyQt5.QtCore import QCoreApplication

from TopoTools2.ui.ProgressProcess.AddProgress import BasicProcess

def calcProcent(count,curent_value):
    proc_val=(curent_value/count)*100.0
    return int(proc_val)
class TestProcess(BasicProcess):
    __count=100
    def __init__(self,count):
        super().__init__()
        self.__count=count
    @property
    def Count(self):
        return self.__count

    def run(self):
        index = 0
        #QCoreApplication.processEvents()
        print('Start')
       # self.ClsProgressBar().setTitle('Проверка')
       # self.ClsProgressBar().show()
        print('Start 1')
        last_proc=0
        while index < self.__count:
            index += 1
            time.sleep(0.5)
            cur_proc=calcProcent(self.__count,index)
            #cur_proc=self.calcProcent(index)
            if cur_proc>last_proc:
                last_proc=cur_proc
                self.countChanged.emit(cur_proc)
            #QCoreApplication.processEvents()
            if self.ClsProgressBar().isCancel:
                break
        print(index)
        #self.countChanged.emit(-1)
        self.endProcess.emit(0)

