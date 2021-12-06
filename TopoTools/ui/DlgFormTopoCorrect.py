import os

import axipy
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader

from ..toolprocessing.correctTopology import runTopoCorrect


class FormTopoCorrect:

    def __init__(self,parent=None):
        self.__list_topo_correct=None
        self.__parentWin=parent
        self.load_ui('DlgCorrectTopo.ui')
        self.window.cb_tab_topo.currentIndexChanged.connect(self.__change_topo_err_tab)
        self.window.ch_db_points.stateChanged.connect(self.__change_status_code)
        self.window.ch_self_intersect.stateChanged.connect(self.__change_status_code)
        self.window.ch_overlap.stateChanged.connect(self.__change_status_code)
        self.window.ch_lim_area.stateChanged.connect(self.__change_status_code)
        self.window.ch_lim_angle.stateChanged.connect(self.__change_status_code)
        self.window.ch_gap.stateChanged.connect(self.__change_status_code)
        self.window.pb_run.clicked.connect(self.__run_correct_topo)

    def load_ui(self,name_resource):
        loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__),name_resource)
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.window  = loader.load(ui_file,self.__parentWin)
        ui_file.close()
    @property
    def widget(self):
        return self.window
    def show(self):
        self.window.showMaximized()
        self.window.show()
    def update(self,list_topo_data):
        self.__list_topo_correct=list_topo_data
        self.__init_data()
    def __init_data(self):
        if self.__list_topo_correct is None or len(self.__list_topo_correct)==0:
            return
        self.window.cb_tab_topo.clear()
        for table_topo in self.__list_topo_correct:
            name=table_topo['source']
            self.window.cb_tab_topo.addItem(name)
        self.window.cb_tab_topo.setCurrentIndex(0)
    def __change_topo_err_tab(self):
        curent_index=self.window.cb_tab_topo.currentIndex()
        tab_error=self.__list_topo_correct[curent_index]['result']
        self.window.ln_topo_erro.setText(tab_error)
        self.__setStatusError(curent_index)
    def __setStatusError(self,index):
        #print("Set Status Erorr")
        name_tab=self.__list_topo_correct[index]['result']
        tab_err=axipy.app.mainwindow.catalog.find(name_tab)
        list_count=self.__countErorrCode(tab_err)
        self.window.ch_db_points.setEnabled(list_count[0]>0)
        self.window.ch_db_points.setChecked(list_count[0]>0)
        self.window.ch_self_intersect.setEnabled(list_count[1]>0)
        self.window.ch_self_intersect.setChecked(list_count[1]>0)
        self.window.ch_overlap.setEnabled(list_count[2]>0)
        self.window.ch_overlap.setChecked(list_count[2]>0)
        self.window.ch_lim_area.setEnabled(list_count[4]>0)
        self.window.ch_lim_area.setChecked(list_count[4]>0)
        self.window.ch_lim_angle.setEnabled(list_count[5]>0)
        self.window.ch_lim_angle.setChecked(list_count[5]>0)
        if list_count[5]>0:
            self.window.ln_angle.setText(str(self.__list_topo_correct[index]['angle_lim']))
        else:
            self.window.ln_angle.setText("")
        self.window.ch_gap.setEnabled(list_count[3]>0)
        self.window.ch_gap.setChecked(list_count[3]>0)
        '''
        count_dpoint_points=self.__getCountErorCode(tab_err,0)
        self.window.ch_db_points.setEnabled(count_dpoint_points>0)
        count_self_intersect=self.__getCountErorCode(tab_err,1)
        self.window.ch_self_intersect.setEnabled(count_self_intersect>0)
        count_overlap=self.__getCountErorCode(tab_err,2)
        self.window.ch_overlap.setEnabled(count_overlap>0)
        count_gap=self.__getCountErorCode(tab_err,3)
        self.window.ch_gap.setEnabled(count_gap>0)
        '''

    def __run_correct_topo(self):
        index_sel_table=self.window.cb_tab_topo.currentIndex()
        name_topo_err=self.__list_topo_correct[index_sel_table]['result']
        name_base_tab=self.__list_topo_correct[index_sel_table]['source']
        list_topo_erorr=[]
        if self.window.ch_db_points.isChecked():
            list_topo_erorr.append('DoublePoint')
        if self.window.ch_self_intersect.isChecked():
            list_topo_erorr.append('NoValidGeometry')
        if self.window.ch_overlap.isChecked():
            list_topo_erorr.append('Overlap')
        if self.window.ch_lim_area.isChecked():
            list_topo_erorr.append('LitePolygon')
        if self.window.ch_gap.isChecked():
            list_topo_erorr.append('Gap')
        angle_lim=None
        if self.window.ch_lim_angle.isChecked():
            list_topo_erorr.append('LimAngle')
            angle_lim=self.__list_topo_correct[index_sel_table]['angle_lim']
        tab_erro_topo=axipy.da. data_manager.find(name_topo_err)
        base_tab=axipy.da. data_manager.find(name_base_tab)
        self.window.pb_run.setEnabled(False)
        '''
        try:
            runTopoCorrect(tab_erro_topo,base_tab,list_topo_erorr,None)
        except  Exception as ex:
            print(ex)
        '''
        runTopoCorrect(tab_erro_topo,base_tab,list_topo_erorr,angle_lim,None)
        self.window.pb_run.setEnabled(True)
        '''
        tab_erro_topo=axipy.da.catalog_service.find(name_topo_err)
        base_tab=axipy.da.catalog_service.find(name_base_tab)
        prop_cor=['DoublePoint','Overlap','NoValidGeometry',"Gap"]
        runTopoCorrect(tab_erro_topo,base_tab,prop_cor)
        '''
    def __countErorrCode(self,table):
        sql ="select type,Count(*) as count from "+table.name+" group by type"
        print(sql)
        res_sql_tab= axipy.io.query(sql, table)
        out_list_count=[0]*6
        for ft in res_sql_tab.items():
            type=ft[0]
            count=ft[1]
            out_list_count[type]=count
        return out_list_count
    def __getCountErorCode(self,table,code):
        sql="select Count(*) from "+table.name+" where type="+str(code)
        #res_sql_tab=axipy.app.mainwindow.catalog.query(sql)
        res_sql_tab= axipy.io.query(sql, table)
        if res_sql_tab is None:
            return 0
        count=res_sql_tab.itemsByIds([0]).__next__()[0]
        return count
    def __change_status_code(self):
        if self.window.ch_db_points.isChecked() or self.window.ch_self_intersect.isChecked() or self.window.ch_overlap.isChecked() or self.window.ch_lim_area.isChecked() or self.window.ch_lim_angle.isChecked() or self.window.ch_gap.isChecked():
            self.window.pb_run.setEnabled(True)
        else:
            self.window.pb_run.setEnabled(False)




