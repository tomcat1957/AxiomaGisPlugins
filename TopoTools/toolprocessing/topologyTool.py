import axipy
from PySide2.QtGui import QTransform
from axipy import *

from TopoTools2.toolprocessing.gapDetectionNew import GapDetection
from TopoTools2.toolprocessing.polygonTopology import PolyIntersect


def CloneGeometry(geo_obj):
    new_geo = geo_obj.affine_transform(QTransform())
    return new_geo
def LinearRingToLineString(ring_geo):
    if isinstance(ring_geo,LineString):
        return ring_geo
    geo_lineString=LineString(ring_geo.points,ring_geo.coordsystem)
    cnt_point=geo_lineString.pointsCount()
    geo_lineString.removePoint(cnt_point-1)
    return geo_lineString
def LineStringFomPoints(points,cs):
    #return LineString(points,cs=cs)
    new_points=[]
    #for i in range(len(points)-1):
    #    new_points.append(points[i])
    for pnt in points:
        new_points.append(pnt)
    return LineString(new_points,cs=cs)
def PolygonToLineString(poly_geo):
    holes=poly_geo.holes
    count_interiors=len(holes)

    if len(holes)==0:
        #return LinearRingToLineString(poly_geo.exteriorRing())
        return LineStringFomPoints(poly_geo.points,poly_geo.coordsystem)
    multiLine=MultiLineString(poly_geo.coordsystem)
    multiLine.append(LinearRingToLineString(LineStringFomPoints(poly_geo.points,poly_geo.coordsystem)))
    for i in range(count_interiors):
        multiLine.append(LineStringFomPoints(poly_geo.holes[i],poly_geo.coordsystem))
    return multiLine
# Polygon или MultiPoligon преобразуем в LineString или MultiLineString
def preparePolygonToselfIntersect(geo_obj):
    #print(geo_obj.exportToWkt())
    if isinstance(geo_obj,Polygon):
        return PolygonToLineString(geo_obj)
    if isinstance(geo_obj,MultiPolygon):
        multiLine = MultiLineString(geo_obj.coordsystem)
        cnt=len(geo_obj)
        for i in range(cnt):
            geo_line_obj=PolygonToLineString(geo_obj[i])
            if isinstance(geo_line_obj,LineString):
                multiLine.append(geo_line_obj)
            elif isinstance(geo_line_obj,MultiLineString):
                cnt_line = len(geo_line_obj)
                for j in range(cnt_line):
                    multiLine.append(geo_line_obj[j])
            geo_line_obj=None
        return multiLine
    return None
def getEndPoints(geo_obj):
    endPointList=[]
    if isinstance(geo_obj,LineString):
    #if isinstance(geo_obj,LineString):
        points=geo_obj.points
        endPointList.append(points[0])
        endPointList.append(points[len(points)-1])
    elif isinstance(geo_obj,MultiLineString):
        count=len(geo_obj)
        for i in range(count):
            cur_geo=geo_obj[i]
            points=cur_geo.points
            endPointList.append(points[0])
            endPointList.append(points[len(points)-1])
    if len(endPointList)==0:
        return None
    obj_multipoint=MultiPoint(geo_obj.coordsystem)
    for point in endPointList:
        obj_multipoint.append(point)
    return obj_multipoint
def findIntersect(obj_geo):
    lineEndPts=getEndPoints(obj_geo)
    if lineEndPts is None:
        return None
    new_obj_geo=lineEndPts.clone()
    #nodedLine=Union(obj_geo,lineEndPts)
    nodedLine=new_obj_geo.union(obj_geo)
    nodedEndPts=getEndPoints(nodedLine)

    self_intrsect=nodedEndPts.difference(lineEndPts)
    if isinstance(self_intrsect,Point):
        #pos=self_intrsect.pos()
        #print((" x=%f y=%f" % (pos.x(),pos.y())))
        #print(self_intrsect.wkt)
        return self_intrsect,nodedEndPts
    elif isinstance(self_intrsect,MultiPoint):
        count=len(self_intrsect)
        #for i in range(count):
            #cur_geo = self_intrsect.geometryAt(i)
            #pos = cur_geo.pos()
           # print((" x=%f y=%f" % (pos.x(), pos.y())))
        return self_intrsect,nodedEndPts
    return None,None
def findSelfIntersectionGeometry(geo_obj):
    if geo_obj is None:
        return None,None
    if geo_obj.type == GeometryType.LineString or geo_obj.type == GeometryType.MultiLineString:
    #if isinstance(geo_obj,LineString) or isinstance(geo_obj,MultiLineString):
        b_is_valid=geo_obj.is_valid
        geo_intersect=findIntersect(geo_obj)
        if geo_intersect is None:
            return None,None
        #print(geo_intersect)
        #print(geo_intersect.wkt)
        return geo_intersect
    if  geo_obj.type==GeometryType.Polygon or  geo_obj.type==GeometryType.MultiPolygon:
        #if isinstance(geo_obj,Polygon) or isinstance(geo_obj,MultiPolygon):
        # полигон или мульти полигон приводим к LineString или MultiLineString
        b_is_valid=geo_obj.is_valid
        if b_is_valid:
            return None,None
        geo_multiLineString=preparePolygonToselfIntersect(geo_obj)
        if geo_multiLineString is not None:
            return findIntersect(geo_multiLineString)

    return None,None
def findPolySimpleLimitArea(geo_obj:Geometry,lim_area_km_sq):
    holes=geo_obj.holes
    if len(holes)==0:
        return None
    list_litle_area=[]
    for pol in holes:
        temp_poly=Polygon(pol,geo_obj.coordsystem)
        cur_area=temp_poly.get_area(AreaUnit.sq_km)
        if cur_area<lim_area_km_sq:
            list_litle_area.append(temp_poly)
    if len(list_litle_area)==0:
        return None
    return list_litle_area
def findPolygonLimitArea(geo_obj:Geometry,lim_area_km_sq):
    if geo_obj is None:
        return None
    type_geo_area=(geo_obj.type== GeometryType.Polygon)
    type_geo_area=type_geo_area or (geo_obj.type== GeometryType.MultiPolygon)
    type_geo_area=type_geo_area or (geo_obj.type== GeometryType.GeometryCollection)
    type_geo_area=type_geo_area or (geo_obj.type== GeometryType.Rectange)

    type_geo_area=type_geo_area or (geo_obj.type== GeometryType.Ellipse)
    type_geo_area=type_geo_area or (geo_obj.type== GeometryType.RoundedRectange)
    if not type_geo_area:
        return None
    area_obj=-1
    try:
        area_obj=geo_obj.get_area(AreaUnit.sq_km)
    except Exception as ex:
        jkl=0
    if area_obj<=lim_area_km_sq:
        return [geo_obj]
    list_geometry_out=[]
    if (geo_obj.type== GeometryType.Rectange) or (geo_obj.type== GeometryType.Ellipse) or (geo_obj.type== GeometryType.RoundedRectange):
        return None
    if geo_obj.type==GeometryType.Polygon  :
        lst_geo=findPolySimpleLimitArea(geo_obj,lim_area_km_sq)
        if lst_geo is not None:
            list_geometry_out.extend(lst_geo)
    if geo_obj.type== GeometryType.MultiPolygon:
        for sub_geo in geo_obj:
            if sub_geo.coordsystem is None:
                sub_geo.coordsystem=geo_obj.coordsystem
            lst_geo=findPolygonLimitArea(sub_geo,lim_area_km_sq)
            if lst_geo is not None:
                list_geometry_out.extend(lst_geo)
    if geo_obj.type==GeometryType.GeometryCollection:
        for sub_geo in geo_obj:
            if sub_geo.coordsystem is None:
                sub_geo.coordsystem=geo_obj.coordsystem
            lst_geo=findPolygonLimitArea(sub_geo,lim_area_km_sq)
            if lst_geo is not None:
                list_geometry_out.extend(lst_geo)
    if len(list_geometry_out)==0:
        return None
    return list_geometry_out


def createMemoryTable(table_source:Table):
    source_cs=table_source.coordsystem.prj
    definition = {}
    name_tab=table_source.name+"_topoCheck"
    definition['src']= ''

    #schema=attr.schema(attr.integer("id"),coordsystem="prj:"+source_cs)
    #schema = axipy.da.Schema([attr.integer("id")], coordsystem="prj:" + source_cs)
    list_att=[]
    list_att.append(attr.integer("id"))
    list_att.append(attr.integer("type"))
    schema = axipy.da.Schema(list_att, coordsystem="prj:" + source_cs)
    definition['schema']=schema
    definition['dataobject']=name_tab
    newtable_mem = io.create(definition)
    return newtable_mem
def runTopology(table:Table,using_tools,property_style):
    '''
    Проверка топологии
    :param table:  Исходная таблица
    : using_tools (dict) : какие свойства проверяются
    :param property_style: стили объектов
    :return:
    '''
    ''' Создаем таблицу результатов'''
    temp_mem_table = createMemoryTable(table)
    axipy.app.mainwindow.catalog().add(temp_mem_table)
    style_intersect= Style.from_mapinfo('Symbol (35,16711680,8,"MapInfo Symbols",0,0) ')
    style_polyIntersect=Style.from_mapinfo('Brush (3, 16776960, 16711680)')
    style_polygonGap=Style.from_mapinfo('Brush (3, 16776960, 16711680)')
    poly_intesectTools=None
    poly_GapTools=None
    if using_tools['PolygonIntersect']:
        poly_intesectTools=PolyIntersect(table)
    if using_tools['GapPolygon']['isRun']:
        poly_GapTools=GapDetection(using_tools['GapPolygon']['area_limmit'])
    for ft in table.items():
        geo_obj=ft[GEOMETRY_ATTR]
        print(ft.id)
        print(geo_obj.wkt)
        if using_tools['SelfIntesect']:
            obj_intersect,temp_obj=findSelfIntersectionGeometry(geo_obj)
            if obj_intersect is not None:
                ft_propertyes={'id':ft.id,'type':1}
                #obj_copy=obj_intersect.clone()
                ft_new=Feature(ft_propertyes,geometry=obj_intersect,style=style_intersect)
                temp_mem_table.insert([ft_new])
        if poly_intesectTools is not None:
            poly_intersect=poly_intesectTools.findPolyIntersect(ft.id,geo_obj)
            if poly_intersect is not None:
                for poly in poly_intersect:
                    ft_propertyes={'id':ft.id,'type':2}

                    ft_new=Feature(ft_propertyes,geometry=poly,style=style_polyIntersect)
                    temp_mem_table.insert([ft_new])
        if poly_GapTools is not None:
            poly_GapTools.addGeo(geo_obj)
    if poly_GapTools is not None:
        geo_gaps,dif_poly,com_obj = poly_GapTools.postProcessing()
        if com_obj is not None:
            ft_propertyes={'id':ft.id,'type':4}
            ft_new=Feature(ft_propertyes,geometry=com_obj,style=style_polygonGap)
            temp_mem_table.insert([ft_new])
        if dif_poly is not None:
            ft_propertyes={'id':ft.id,'type':5}
            ft_new=Feature(ft_propertyes,geometry=dif_poly,style=style_polygonGap)
            temp_mem_table.insert([ft_new])
        if geo_gaps is not None:
            for gap_obj in geo_gaps:
                ft_propertyes={'id':ft.id,'type':3}
                ft_new=Feature(ft_propertyes,geometry=gap_obj,style=style_polygonGap)
                temp_mem_table.insert([ft_new])
                #memTab.addPolyHole(gap_obj)
                pass
