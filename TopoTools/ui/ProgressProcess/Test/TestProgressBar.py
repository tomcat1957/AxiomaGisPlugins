import axipy

from TopoTools2.ui.DlgProgressBar import DlgProgressBar
from TopoTools2.ui.ProgressProcess.AddProgress import RunThread
from TopoTools2.ui.ProgressProcess.Test.TestProcess import TestProcess
from TopoTools2.ui.ProgressProcess.Test.TestRunClass import SimpleProgress

#cls_import=SimpleProgress(1000)

#cls_import.initOutDs(path_out)
#base_task=RunThread(cls_import,'tttt','qqqq')
base_task=TestProcess(200)
dlg = DlgProgressBar(base_task,axipy.app.mainwindow.qt_object())
dlg.setTextProcess("Инициализация базы ..")
dlg.setTitle("Проверка топологии")
base_task.setClsProgressBar(dlg)
# b_process.setProcess([process_obj,process_obj1,process_obj2,process_objSp])

# b_process.setProcess([process_obj1])
dlg.exec(100)