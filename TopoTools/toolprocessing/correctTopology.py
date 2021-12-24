import math
import operator
import time
from enum import Enum

import axipy
from PySide2 import QtCore
from PySide2.QtWidgets import QProgressDialog
from axipy import Geometry, Polygon, MultiPolygon, unit, GEOMETRY_ATTR, Table, Unit, GeometryType, GeometryCollection, \
    Feature

from .FindAngleLimite import correctLimAngle
from .doblePointsTool import findDoublePoint, deleteDoublePoint
from .ui.DlgInterActive import DlgInterTopoCorrect


class TypeTopoError(Enum):
    DublePoint=0
    NoValidGeometry=1
    Overlap=2
    Gap=3
    LitePolygon=4
    LimAngle=5
    @staticmethod
    def factory(typeErr:int):
        if typeErr==0:
            return TypeTopoError.DublePoint
        if typeErr==1:
            return TypeTopoError.NoValidGeometry
        if typeErr==2:
            return TypeTopoError.Overlap
        if typeErr==3:
            return TypeTopoError.Gap
        if typeErr==4:
            return TypeTopoError.LitePolygon
        if typeErr==5:
            return TypeTopoError.LimAngle
        return None
    @staticmethod
    def Name(type_err):
        if type_err==TypeTopoError.DublePoint:
            return "DoublePoint"
        if type_err==TypeTopoError.NoValidGeometry:
            return "NoValidGeometry"
        if type_err==TypeTopoError.Overlap:
            return "Overlap"
        if type_err==TypeTopoError.Gap:
            return "Gap"
        if type_err==TypeTopoError.LitePolygon:
            return "LitePolygon"
        if type_err==TypeTopoError.LimAngle:
            return "LimAngle"
        return None



def MakeValidGeometry(source_geo:Geometry):
    if source_geo.is_valid:
        return source_geo,False
    tem_geometry=source_geo.normalize()
    source_geo=None
    source_geo=tem_geometry
    return source_geo,True
def findOvarLaps(base_ft,table_source):
    base_geo=base_ft[GEOMETRY_ATTR]
    id_ft=int(base_ft.id)
    if not base_geo.is_valid:
        base_geo=base_geo.normalize()
    bound_geo = base_geo.bounds
    mbr_fts = table_source.items(bound_geo)

    for ft in mbr_fts:
        if int(ft.id)<=id_ft:
            continue
        cur_geo=ft.geometry
        if not(isinstance(cur_geo,Polygon) or isinstance(cur_geo,MultiPolygon)):
            continue
        geo_intersect=base_geo.intersection(cur_geo)
        if geo_intersect is None:
            continue
        if not(isinstance(geo_intersect,Polygon) or isinstance(geo_intersect,MultiPolygon)):
            continue
        return {'ft':ft,'geo_intersect':geo_intersect}

    return None
def validateOnlyPolygon(geo_obj:Geometry):
    ''' Проверка что объект полигон
    Нужна при операциях вычитания полигона из полигона.
    Т.к. разработчики AxyPy данную ситуацию не обрабатывают
    '''
    if geo_obj is None:
        return None
    if geo_obj.type==GeometryType.Polygon or geo_obj.type==GeometryType.MultiPolygon:
        return geo_obj
    if geo_obj.type==GeometryType.GeometryCollection:
        out_geo_collection=GeometryCollection(geo_obj.coordsystem)
        for geo_simple in geo_obj:
            if geo_simple.type==GeometryType.Polygon:
                out_geo_collection.append(geo_simple)
        if len(out_geo_collection)==0:
            return None
        if len(out_geo_collection)==1:
            return out_geo_collection[0]
        return out_geo_collection
    return None
def correctOverlapObjects(geom_err,main_ft,list_ft,tab_correct:Table):
    list_update_ft=[]
    new_geo_main=None
    for ft_i in list_ft:
        ft=ft_i['feature']
        geom=ft.geometry
        new_geo=geom.difference(geom_err)
        poly_new_geo=validateOnlyPolygon(new_geo)
        if poly_new_geo is None:
            continue
        ft.geometry=poly_new_geo
        list_update_ft.append(ft)
    try:
        new_geo_main=main_ft.geometry.union(geom_err)
        new_geo_main_poly=validateOnlyPolygon(new_geo_main)
        if new_geo_main_poly is not None:
            main_ft.geometry=new_geo_main_poly
            list_update_ft.append(main_ft)
    except Exception as ex:
        print(ex)
    tab_correct.update(list_update_ft)
def correctOverlaps1(base_ft,geo_source_Validate,table_source):
    '''
    Корректировка перекрытия полигонов

    '''
    base_geo=base_ft.geometry
    if not geo_source_Validate:
        if not base_geo.is_valid:
            base_geo=base_geo.normalize()
            base_ft.geometry=base_geo
    bound_geo = base_geo.bounds
    area_base=base_geo.get_area(Unit.sq_m)
    mbr_fts = table_source.items(bound_geo)
    overlap_ft=[]
    for ft in mbr_fts:
        #obj_intersect=ft.geometry.intersection(base_geo)
        #is_obj_contains=ft.geometry.contains(base_geo)
        if ft.geometry is None:
            continue

        #is_obj_contains=ft.geometry.contains(base_geo.centroid())or ft.geometry.intersects(base_geo)
        is_obj_contains=ft.geometry.contains(base_geo) or ft.geometry.intersects(base_geo)
        #is_obj_contains=ft.geometry.contains(base_geo)

        if is_obj_contains:
            try:
                obj_intersect=ft.geometry.intersection(base_geo)
            except Exception as ex:

                print(ex)
                print("Error find intersection object")
                obj_intersect=None
                is_obj_contains=False

            #temp_area=obj_intersect.get_area(Unit.sq_m)
            #jkl=0

        #if obj_intersect is not None and obj_intersect.equals(base_geo):
        #if obj_intersect is not None:
        if is_obj_contains:
            geo_poly=validateOnlyPolygon(obj_intersect)
            if geo_poly is not None:
                area_geom=ft.geometry.get_area(Unit.sq_m)
                overlap_ft.append({'feature':ft,'area':area_geom})
    if len(overlap_ft)>=1:
        overlap_ft.sort(key=operator.itemgetter('area'))
    else:
        return
    count_ft=len(overlap_ft)
    main_ft=overlap_ft[count_ft-1].copy()
    overlap_ft.pop(count_ft-1)
    correctOverlapObjects(base_geo,main_ft['feature'],overlap_ft,table_source)
def correctOverlaps(base_ft,geo_source_Validate,table_source):
    '''
    Корректировка перекрытия полигонов

    '''
    base_geo=base_ft.geometry
    if not geo_source_Validate:
        if not base_geo.is_valid:
            base_geo=base_geo.normalize()
            base_ft.geometry=base_geo
    bound_geo = base_geo.bounds
    area_base=base_geo.get_area(Unit.sq_m)
    mbr_fts = table_source.items(bound_geo)
    inersect_ft=[]
    ''' Цикл по всем features пересекающимся с базовой геометрией ( можно выполнять и sql)'''
    isExistIntersect=True
    while isExistIntersect:
        if base_geo is None:
            break
        obj_intersect=findOvarLaps(base_ft,table_source)
        if obj_intersect is None:
            break
        geo_intercest=obj_intersect['geo_intersect']
        area_cur_geo_ft=obj_intersect['ft'].geometry.get_area(Unit.sq_m)
        list_update_feature=[]
        list_delete_feature=[]
        if area_base>=area_cur_geo_ft:
            ''' Добавляем область пересечения к базовой геометрии'''
            new_base_geo=base_geo.union(geo_intercest)
            ''' Удаляем из геометрии пересекающейся с базовой область пересечения'''
            new_ft_geo=obj_intersect['ft'].geometry.difference(geo_intercest)

            base_geo=new_base_geo
            '''
            if base_geo is None:
                #base_ft=None
                list_delete_feature.append(base_ft)
            else:
                base_ft.geometry=new_base_geo
                list_update_feature.append(base_ft)
            ft_curent=obj_intersect['ft']
            if new_ft_geo is not None:
                ft_curent.geometry=new_ft_geo
                list_update_feature.append(ft_curent)
            else:
                list_delete_feature.append(ft_curent)
            '''

        else:
            ''' Удаляем область пересчения из базовой геометрии'''
            new_base_geo=base_geo.difference(geo_intercest)
            ''' Добавляем область пересчения к текущей геометрии'''
            new_ft_geo=obj_intersect['ft'].geometry.union(geo_intercest)
            #base_ft.geometry=new_base_geo
            base_geo=new_base_geo
            '''
            ft_curent=obj_intersect['ft']
            ft_curent.geometry=new_ft_geo
            '''
        if base_geo is None:
            #base_ft=None
            list_delete_feature.append(base_ft)
        else:
            area_base=base_geo.get_area(Unit.sq_m)
            base_ft.geometry=new_base_geo
            list_update_feature.append(base_ft)
        ft_curent=obj_intersect['ft']
        if new_ft_geo is not None:
            ft_curent.geometry=new_ft_geo
            list_update_feature.append(ft_curent)
        else:
            list_delete_feature.append(ft_curent)
        if len(list_update_feature)>0:
            table_source.update(list_update_feature)
        if len(list_delete_feature)>0:
            for ft_del in list_delete_feature:
                table_source.remove([ft_del.id])

def correctGapError(geo_err,table_source:Table):
    base_geo=geo_err

    #if not base_geo.is_valid:
    #    base_geo=base_geo.normalize()

    bound_geo = base_geo.bounds
    mbr_fts = table_source.items(bound_geo)
    overlap_ft=[]
    for ft in mbr_fts:
        obj_intersect=ft.geometry.intersection(base_geo)
        if obj_intersect is not None:
            area_geom=ft.geometry.get_area(Unit.sq_m)
            overlap_ft.append({'feature':ft,'area':area_geom})
    if len(overlap_ft)>1:
        overlap_ft.sort(key=operator.itemgetter('area'))
    else:
        return
    count_ft=len(overlap_ft)
    main_ft=overlap_ft[count_ft-1]
    main_geometry=main_ft['feature'].geometry
    overlap_ft.pop(count_ft-1)
    new_geo=main_geometry.union(base_geo)
    feture_result=main_ft['feature']
    feture_result.geometry=new_geo
    table_source.update([feture_result])
def correctPolyAreaHoles(area_lim,geo_obj:Geometry):
    ''' Поиск hole ( дырок) площадбю равной или меньше заданной '''
    isRemove=False
    new_geo=Polygon(geo_obj.points,geo_obj.coordsystem)
    for hole in geo_obj.holes:
        temp_poly=Polygon(hole,geo_obj.coordsystem)
        if temp_poly.get_area(Unit.sq_km)<=area_lim:
            isRemove=True
            continue
        new_geo.holes.append(iter(hole))
    if not isRemove:
        return None
    return new_geo
def correctLitePolyErorr(base_ft:Feature,table_source:Table):
    area_err_poly=base_ft.geometry.get_area(Unit.sq_km)
    ft_items_source=table_source.itemsByIds([base_ft['id']])
    ft_items=list(ft_items_source)
    ft_source_err=ft_items[0]
    if ft_source_err.geometry.get_area(Unit.sq_km)<=area_err_poly:
        table_source.remove([ft_source_err.id])
        return
    if ft_source_err.geometry.type==GeometryType.Polygon :
        if len(ft_source_err.geometry.holes)==0:
            return
        else:
            new_geo=correctPolyAreaHoles(area_err_poly,ft_source_err.geometry)
            if new_geo is None:
                return
            ft_source_err.geometry=new_geo
            table_source.update([ft_source_err])
            return
    if ft_source_err.geometry.type==GeometryType.MultiPolygon or ft_source_err.geometry.type==GeometryType.GeometryCollection:
        index_geo=-1
        isUpdate=False
        for item_geo in ft_source_err.geometry:
            index_geo=index_geo+1
            if item_geo.type!=GeometryType.Polygon:
                continue
            if item_geo.coordsystem is None:
                item_geo.coordsystem=ft_source_err.geometry.coordsystem
            cur_area=item_geo.get_area(Unit.sq_km)
            if cur_area>area_err_poly:
                new_geo=correctPolyAreaHoles(area_err_poly,item_geo)
                if new_geo is not None:
                    isUpdate=True
                    ft_source_err.geometry.remove(index_geo)
            else:
                isUpdate=True
                ft_source_err.geometry.remove(index_geo)
        if isUpdate:
            if len(ft_source_err.geometry)==1:
                ft_source_err.geometry=ft_source_err.geometry[0]
            table_source.update([ft_source_err])
    return







class CorrectTopology:
    def __init__(self):
        pass
    def run(self,table_source,table_dest):
        for ft in table_source.items():
            print(ft.get('id'))
            geo_cur=ft.geometry
            new_geo,IsUpdate=MakeValidGeometry(geo_cur)
            if IsUpdate:
                ft.geometry=new_geo
                table_source.update([ft])

            if ft.get('id')==23 or ft.get('id')==17:
                jkl=0
            #correctOverlaps(ft,True,table_source)
def initProgressBar(head,message,count):
    cls_progressbar = QProgressDialog(axipy.app.mainwindow.qt_object())
    cls_progressbar.setWindowModality(QtCore.Qt.ApplicationModal)
    cls_progressbar.setWindowFlags(
        cls_progressbar.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint & ~QtCore.Qt.WindowContextHelpButtonHint)
    cls_progressbar.setWindowTitle(head)
    cls_progressbar.setLabelText(message)
    #  progdialog.canceled.connect(self.close)
    cls_progressbar.setRange(0, count)
    return cls_progressbar
def runTopoCorrect(table_topoError:Table,table_correct:Table,property,angle_lim_value,doc_widget=None):

    ''' Коррекция топологии '''
    if property is None:
        return
    angle_lim=angle_lim_value
    col_type_err='type'
    id_obj_base_tab='id'
    cls_progressbar=None
    dlgInterActive=None
    if doc_widget is None:
        cls_progressbar=initProgressBar("Коррекция топологии","Процесс ..",table_topoError.count())
        cls_progressbar.show()
        cls_progressbar.setValue(0)
    else:
        dlgInterActive=DlgInterTopoCorrect(doc_widget.widget)
    index_ft=-1
    for ft_error in table_topoError.items():
        index_ft=index_ft+1
        if cls_progressbar is not None:
            time.sleep(0.01)
            if cls_progressbar.wasCanceled():
                break
            cls_progressbar.setValue(index_ft)
        type_err_value=ft_error[col_type_err]
        type_err=TypeTopoError.factory(type_err_value)
        if type_err==None:
            continue
        if not(TypeTopoError.Name(type_err) in property):
            continue
        if dlgInterActive is not None:
            dlgInterActive.show()
        id_value=ft_error[id_obj_base_tab]
        fts_iter=table_correct.itemsByIds([id_value])
        fts=[]
        for ft_id in fts_iter:
            fts.append(ft_id)
        if fts is None or len(fts)==0 or len(fts)>1:
            print("Ошибка поиска записи id "+str(id_value))
            continue
        ft=fts[0]
        if ft.geometry is None:
            continue
        if type_err==TypeTopoError.NoValidGeometry:
            if not ft.geometry.is_valid:
                new_geo=ft.geometry.normalize()
                ft.geometry=new_geo
                table_correct.update([ft])
        if type_err==TypeTopoError.DublePoint:
            new_geometry=deleteDoublePoint(ft.geometry,ft_error.geometry)
            if new_geometry is not None:
                ft.geometry=new_geometry
                table_correct.update([ft])
        if type_err==TypeTopoError.LimAngle and angle_lim is not None:
            print(ft.id)
            print(ft_error['id'])
            new_geometry=correctLimAngle(ft.geometry,math.radians(angle_lim))
            if new_geometry is not None:
                ft.geometry=new_geometry
                table_correct.update([ft])
        if type_err==TypeTopoError.Overlap:
            ''' исправление перекрытия '''
            correctOverlaps1(ft_error,True,table_correct)
        if type_err==TypeTopoError.Gap:

            correctGapError(ft_error.geometry,table_correct)
        if type_err==TypeTopoError.LitePolygon:
            correctLitePolyErorr(ft_error,table_correct)
    if cls_progressbar is not None:
        cls_progressbar.close()
        cls_progressbar=None

def coorectLimAngle(ft_eroor,table_source:Table,lim_angle):
    ft_source_err=table_source.itemsByIds([ft_eroor['id']])
    if ft_source_err is None or len(ft_source_err)==0:
        print (" Not find feature id="+str(ft_eroor['id']))
        return False
    ft=list[iter(ft_eroor)][0]





