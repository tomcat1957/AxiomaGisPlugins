import math
import time

import axipy
from axipy import Table, attr, Style, GEOMETRY_ATTR, Feature, Point

from .AxiTable import AxiTableCache
from .FindAngleLimite import findAngleLim
from .doblePointsTool import findDoublePoint
from .gapDetectionNew import GapDetection
from .polygonTopology import PolyIntersect
from .topologyTool import findSelfIntersectionGeometry, findPolygonLimitArea
from .ui.clsProgressBar.AddProgress import BasicProcess
def createMemoryTable(name_base_table,cs):
    '''
    Создание временной таблицы
    :param name_base_table: имя исходной таблицы
    :param cs: source coordsys
    :return:
    '''
    source_cs=cs.prj
    definition = {}
    name_tab=name_base_table+"_topoCheck"
    definition['src']= ''

    #schema=attr.schema(attr.integer("id"),coordsystem="prj:"+source_cs)
    #schema = axipy.da.Schema([attr.integer("id")], coordsystem="prj:" + source_cs)
    '''
    list_att=[]
    list_att.append(attr.integer("id"))
    list_att.append(attr.integer("type"))
    schema = axipy.da.Schema(list_att, coordsystem="prj:" + source_cs)
    '''
    scheme_tab=attr.schema(attr.integer("id"),coordsystem="prj:" + source_cs)
    scheme_tab.append(attr.integer("type"))
    definition['schema']=scheme_tab
    definition['dataobject']=name_tab
    newtable_mem = axipy.io.create(definition)
    return newtable_mem
def calcProcent(count,curent_value):
    proc_val=(curent_value/count)*100.0
    return int(proc_val)
class RunTopo(BasicProcess):
    __count=100
    __table=None
    __propertyes_check=None
    __result_table=None
    def __init__(self,table_source:Table,propertyes_check):
        super().__init__()
        self.__table=table_source
        self.__propertyes_check=propertyes_check
        self.__count=table_source.count()
    @property
    def Count(self):
        return self.__count

    def run(self):
        index = 0
        ''' Создаем таблицу результатов'''
        temp_mem_table = createMemoryTable(self.__table.name,self.__table.coordsystem)
        axipy.app.mainwindow.catalog.add(temp_mem_table)
        try:
            style_intersect= Style.from_mapinfo(self.__propertyes_check['self_intersect']['style'])
        except:
            pass
        try:
            style_polyIntersect=Style.from_mapinfo(self.__propertyes_check['area_intersect']['style'])
        except:
            pass
        try:
            style_polygonGap=Style.from_mapinfo(self.__propertyes_check['gap_area']['style'])
        except:
            pass
        try:
            style_db_points=Style.from_mapinfo(self.__propertyes_check['double_points']['style'])
        except:
            pass
        try:
            style_area_lim=Style.from_mapinfo(self.__propertyes_check['area_limit']['style'])
        except:
            pass
        try:
            style_angle_lim=Style.from_mapinfo(self.__propertyes_check['angle_limit']['style'])
            angle_lim_grad=float(self.__propertyes_check['angle_limit']['angle_limit'])
            angle_lim_rad=math.radians(angle_lim_grad)
            angle_lim_enable=self.__propertyes_check['angle_limit']['enable']
        except:
            angle_lim_enable=False
        poly_intesectTools=None
        poly_GapTools=None
        if self.__propertyes_check['area_intersect']['enable']:
            poly_intesectTools=PolyIntersect(self.__table)
        if self.__propertyes_check['gap_area']['enable']:
            poly_GapTools=GapDetection(self.__propertyes_check['gap_area']['area_limmit'])
        last_proc=0
        axiMem=AxiTableCache(temp_mem_table,200)
        axiMem.Start()
        for ft in self.__table.items():
            geo_obj=ft.geometry
            #obj_isValid=geo_obj.is_valid
            ''' Поиск дублирующих точек'''
            if self.__propertyes_check['double_points']['enable']:
                list_double_points=findDoublePoint(geo_obj)
                if list_double_points is not None:
                    list_ft_db=[]
                    for pt in list_double_points:
                        ft_propertyes={'id':ft.id,'type':0}

                        ft_new=Feature(ft_propertyes,geometry=pt,style=style_db_points)
                        list_ft_db.append(ft_new)
                    #temp_mem_table.insert(list_ft_db)
                    axiMem.Insert(list_ft_db)

            ''' Проверка самопресечения плигонов'''
            if self.__propertyes_check['self_intersect']['enable']:
                obj_intersect,temp_obj=findSelfIntersectionGeometry(geo_obj)
                if obj_intersect is not None:
                    ft_propertyes={'id':ft.id,'type':1}
                    #obj_copy=obj_intersect.clone()
                    ft_new=Feature(ft_propertyes,geometry=obj_intersect,style=style_intersect)
                    #temp_mem_table.insert([ft_new])
                    axiMem.Insert(ft_new)
                    ft_new=None
            ''' Поиск  вершин с углом меньше заданного'''
            if angle_lim_enable:
                points_angle=findAngleLim(geo_obj,angle_lim_rad)
                if points_angle is not None:
                    for pt_i in points_angle:
                        ft_propertyes={'id':ft.id,'type':5}
                        pt=pt_i['point']
                        point_geo=Point(pt.x,pt.y,geo_obj.coordsystem)
                        ft_new=Feature(ft_propertyes,geometry=point_geo,style=style_angle_lim)
                        axiMem.Insert(ft_new)
                        ft_new=None
            '''Проверка перекрытия полигонов'''
            if poly_intesectTools is not None:
                poly_intersect=poly_intesectTools.findPolyIntersect(ft.id,geo_obj)
                if poly_intersect is not None:
                    for poly in poly_intersect:
                        ft_propertyes={'id':ft.id,'type':2}

                        ft_new=Feature(ft_propertyes,geometry=poly,style=style_polyIntersect)
                        #temp_mem_table.insert([ft_new])
                        axiMem.Insert(ft_new)
                        ft_new=None
            ''' Проверка площади полигонов '''
            if self.__propertyes_check['area_limit']['enable']:
                if geo_obj.coordsystem is None:
                    jkl2=0
                poly_lite_objs=findPolygonLimitArea(geo_obj,self.__propertyes_check['area_limit']['area_limit'])
                if poly_lite_objs is not None:
                    for new_geo in poly_lite_objs:
                        ft_propertyes={'id':ft.id,'type':4}

                        ft_new=Feature(ft_propertyes,geometry=new_geo,style=style_area_lim)
                        #temp_mem_table.insert([ft_new])
                        axiMem.Insert(ft_new)
                        ft_new=None

            ''' Добавление объектов в поиск gap(дыр) между полигонами'''
            if poly_GapTools is not None:
                poly_GapTools.addGeo(geo_obj)
            index += 1
            time.sleep(0.00000005)
            cur_proc=calcProcent(self.__count,index)
            #cur_proc=self.calcProcent(index)
            if cur_proc>last_proc:
                last_proc=cur_proc
                self.countChanged.emit(cur_proc)
            #QCoreApplication.processEvents()
            if self.ClsProgressBar() is not None:
                if self.ClsProgressBar().isCancel:
                    break
        if self.ClsProgressBar() is not None:
            if not self.ClsProgressBar().isCancel:
                ''' Post processing gap polygons'''
                if poly_GapTools is not None:
                    geo_gaps,dif_poly,com_obj = poly_GapTools.postProcessing()
                    if geo_gaps is not None:
                        for gap_obj in geo_gaps:
                            ft_propertyes={'id':ft.id,'type':3}
                            ft_new_gap=Feature(ft_propertyes,geometry=gap_obj,style=style_polygonGap)
                            #temp_mem_table.insert([ft_new_gap])
                            axiMem.Insert(ft_new_gap)
                            ft_new_gap=None
        #self.countChanged.emit(-1)
        axiMem.End()
        axiMem=None
        if temp_mem_table.count()<=0:
            temp_mem_table.close()
            temp_mem_table=None
        else:
            self.__result_table=temp_mem_table
        self.endProcess.emit(0)

        return
    @property
    def ResultTable(self):
        return self.__result_table