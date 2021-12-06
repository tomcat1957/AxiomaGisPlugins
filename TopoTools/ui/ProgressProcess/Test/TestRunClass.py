import time

from TopoTools2.ui.ProgressProcess.AddProgress import BasicProcess


class SimpleProgress(BasicProcess):
    __count=0
    def __init__(self,count):
        super().__init__(count)
        self.__count=count
    #self.initDb(pathbaseDb)

    def setCoordSsStyle(self,cs_wkt,propert_style):
        self.__out_cs_wkr=cs_wkt
        self.__propertyStyle=propert_style
    @property
    def Count(self):
        return self.__count
    def setProcess(self,lst_process):
        self.__listProcess=lst_process
    @property
    def Process(self):
        return self.__listProcess
    def setDopProperty(self,property:dict):
        self.__dopProperty=property
    def statusProgressBar(self,i_procent):
        print("statusProgressBar:"+str(i_procent))
        if self.ClsProgressBar.isCancel:
            return False
        if self.ClsProgressBar.CurentValue>=i_procent:
            return True
        #print("Send :" + str(i_procent))
        self.countChanged.emit(i_procent)
        return True
    def run(self):
        print('Start 0')

        self.ClsProgressBar.setTextProcess(self.__listProcess[0].NameProcess)
        index = 0
        # QCoreApplication.processEvents()
        print('Start')
        self.ClsProgressBar().setTitle('Проверка Head')
        # self.ClsProgressBar().show()
        self.ClsProgressBar.setTextProcess("Проверка")
        for id_pr in range(self.__count):
            if self.ClsProgressBar().isCancel:
                break
            time.sleep(1)


            index += 1
            #time.sleep(0.005)

            #self.countChanged.emit(index)
            # QCoreApplication.processEvents()
            print(self.ClsProgressBar)
            #if self.ClsProgressBar().isCancel:
            #    break
            print("End Run Process:"+str(index))
        # self.countChanged.emit(-1)

        self.endProcess.emit(0)
