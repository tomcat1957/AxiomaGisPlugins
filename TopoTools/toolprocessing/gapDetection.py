from axioma_dynload._core_geometry import area
from axipy import Collection, Polygon, MultiPolygon, Line, AreaUnit, LinearUnit, unit, LineString

def CreatePolygonFromRect(mbr,cs):
    points=[]
    points.append((mbr.xmin,mbr.ymin))
    points.append((mbr.xmin,mbr.ymax))
    points.append((mbr.xmax,mbr.ymax))
    points.append((mbr.xmax,mbr.ymin))
    points.append((mbr.xmin,mbr.ymin))
    geo_poly=Polygon(points,cs)
    return geo_poly
def customUnCombine(geo_collection):
    if not isinstance(geo_collection,Collection):
        return None
    list_obj_col=[]
    count=geo_collection.collectionSize()
    for i in range(count):
        list_obj_col.append(geo_collection[i])
    return list_obj_col
def calcArea( line_ring, str_unit="sq km"):
    geo_poly = Polygon(line_ring)
    area_poly = geo_poly.area
    area_unit_km=AreaUnit.sq_kilometer
    area=geo_poly.get_area(area_unit_km)

    return area_poly
def keySort(item):
    return item[1]
def buildExteriorPolygon(geo_obj):
    if isinstance(geo_obj,Polygon):
       return geo_obj.clone()
    if not isinstance(geo_obj,MultiPolygon):
        return None
    if isinstance(geo_obj,LineString):
        return None
    count_poly=len(geo_obj)
    list_poly_ring=[]
    curent_poly=None
    for i in range(count_poly):
        curent_poly=geo_obj[i]
        #cur_ring=curent_poly.exteriorRing()
        obj_area=calcArea(curent_poly)
        item_ring=[curent_poly,obj_area]
        list_poly_ring.append(item_ring)
    if len(list_poly_ring)==1:
        return Polygon(curent_poly)
    # сортируем по площади
    v_sort=sorted(list_poly_ring,key=keySort,reverse=True)
    base_item=list_poly_ring[0]
    base_polygon=Polygon(base_item[0],base_item.coorsystem)
    result_geo=None
    for i in range(1,len(list_poly_ring)):
        item_poly=Polygon(list_poly_ring[i][0])
        if item_poly.within(base_polygon):
            continue
        if result_geo is None:
            result_geo=base_polygon.clone().union(item_poly)
        else:
            result_geo=result_geo.clone().union(item_poly)
    if result_geo is None:
        result_geo=base_polygon
    return result_geo
def calcWidthBufFromMeterInUnitCoordSys(mbr,coord_sys,width_m):
    xmax=mbr.xmax
    xmin=mbr.xmin
    ymidl=mbr.center.y
    geo_line_midl=Line((xmin,ymidl),(xmax,ymidl),coord_sys)

    width_bound=geo_line_midl.get_length(unit.m);
    coef=(xmax-xmin)/width_bound
    width_bound=1.0*coef
    return width_bound
def getMbrAndBuffer(geo_obj,width_buf_m=0.5):
    mbr=geo_obj.bounds
    width_buffer=calcWidthBufFromMeterInUnitCoordSys(mbr,geo_obj.coordsystem,width_buf_m)

    geo_mbr=CreatePolygonFromRect(mbr,geo_obj.coordsystem)

    #geo_buffer = Buffer(geo_mbr, width_buffer, 3)
    geo_buffer = geo_mbr.buffer(width_buffer,3)
    return geo_buffer
class GapDetection:
    __commom_geo=None
    __area_limit=None
    __geo_comm_buff=None
    __list_result=None
    def __init__(self,limit_area):
        self.__area_limit=limit_area
        self.__geo_comm_buff=None
        self.__geo_dif_obj=None
    def calcCommPolygon(self,next_obj_geo):
        if next_obj_geo is None:
            return
        if not (isinstance(next_obj_geo,Polygon) or isinstance(next_obj_geo,MultiPolygon)):
            return
        b_valid = next_obj_geo.is_valid
        if not b_valid:
            # базовая геометрия не валидна
            geo_obj = next_obj_geo.normalize()
        else:
            geo_obj=next_obj_geo
        curent_geo_poly = Polygon(geo_obj.points,geo_obj.coordsystem)
        if self.__commom_geo is None:
            self.__commom_geo = curent_geo_poly
        else:
            self.__commom_geo = self.__commom_geo.clone().union( curent_geo_poly)
    def calcCommPolygonMbr(self,next_obj_geo):
        if next_obj_geo is None:
            return
        if not (isinstance(next_obj_geo,Polygon) or isinstance(next_obj_geo,MultiPolygon)):
            return
        b_valid = next_obj_geo.is_valid
        if not b_valid:
            # базовая геометрия не валидна
            geo_obj = next_obj_geo.normalize()
        else:
            geo_obj=next_obj_geo
        geo_obj_mbr_buffer = getMbrAndBuffer(geo_obj)
        if self.__geo_comm_buff is None:
            self.__geo_comm_buff = geo_obj_mbr_buffer
        else:
            self.__geo_comm_buff = self.__geo_comm_buff.clone().union( geo_obj_mbr_buffer)
    @property
    def commonBuffer(self):
        return self.__geo_comm_buff
    def prepareCommonObj(self):
        if self.__commom_geo is None:
            return False
        if not(isinstance(self.__commom_geo,Polygon) or isinstance(self.__commom_geo,MultiPolygon)):
            return False
        b_valid = self.__commom_geo.is_valid
        if not b_valid:
            # базовая геометрия не валидна
            self.__commom_geo = self.__commom_geo.normalize()
        self.__geo_dif_obj = buildExteriorPolygon(self.__commom_geo)

        return True
    def diffSourceFromCommon(self,source_geo):
        b_valid = source_geo.is_valid
        if not b_valid:
            geo_obj = source_geo.normalize()
        else:
            geo_obj=source_geo
        self.__geo_dif_obj = self.__geo_dif_obj.difference(geo_obj)
    def diffSourceFromMbrCommon(self,source_geo):
        b_valid = source_geo.is_valid
        if not b_valid:
            geo_obj = source_geo.normalize()
        else:
            geo_obj=source_geo
        if self.__geo_dif_obj is None:
            self.__geo_dif_obj=self.__geo_comm_buff
        geo_dif_obj_1 = self.__geo_dif_obj.difference(geo_obj)
        self.__geo_dif_obj = None
        self.__geo_dif_obj = geo_dif_obj_1
    def diffSourceFromCommon(self,source_geo):
        b_valid = source_geo.is_valid
        if not b_valid:
            geo_obj = source_geo.is_valid
        else:
            geo_obj=source_geo
        curent_geo_poly = buildExteriorPolygon(geo_obj)
        geo_dif_obj_1 = self.__geo_dif_obj.difference( curent_geo_poly)
        self.__geo_dif_obj = None
        self.__geo_dif_obj = geo_dif_obj_1
    @property
    def getExteriorPolygon(self):
        return self.__commom_geo
    def getDifPrepare(self):
        return self.__geo_dif_obj
    @property
    def resultPolygon(self):
        return self.__geo_dif_obj
    def prepareResutl(self):
        if isinstance(self.__geo_dif_obj,Polygon):
            return None
        area_unit="sq km"
        self.__geo_dif_obj.removePolygonAt(0)
        if isinstance(self.__geo_dif_obj,Polygon):
            if self.__area_limit<0:
                return [self.__geo_dif_obj]
            area_obj=area(self.__geo_dif_obj,area_unit)
            if area_obj<=self.__area_limit:
                return [self.__geo_dif_obj]
            return None
        list_result=[]
        for i in range(self.__geo_dif_obj.collectionSize()):
            geo_item=self.__geo_dif_obj.geometryAt(i)
            area_obj = area(geo_item, area_unit)
            if area_obj<=self.__area_limit or (self.__area_limit<0):
                list_result.append(geo_item)

        return list_result

