from axipy import Geometry, GeometryType, Point


class DublePoints:
    __hash_table={}
    __ndigits=None
    __existDuble=False
    def __init__(self,ndigits=None):
        self.__ndigits=ndigits
        self.__hash_table={}
    def add(self,id,x,y):
        obj_point=self.__obj_points(id,x,y)
        if self.__ndigits is None:
            hash_xy=hash((x,y))
        else:
            hash_xy=hash((round(x,self.__ndigits),round(y,self.__ndigits)))
        if hash_xy in self.__hash_table:
            self.__hash_table[hash_xy].append(obj_point)
            self.__existDuble=True
            return True
        else:
            self.__hash_table[hash_xy]=[obj_point]
            return False
    def __obj_points(self,id,x,y):
        return {'id':id,'x':x,"y":y}
    @property
    def ExistDublePoints(self):
        return self.__existDuble
    def getDoublePoints(self,fullList=False):
        if not self.__existDuble:
            return None
        double_points=[]
        for hash_point in self.__hash_table.keys():
            list_point=self.__hash_table[hash_point]
            if len(list_point)==1:
                continue
            if fullList:
                double_points.extend(list_point)
            else:
                double_points.append(list_point[0])
        return double_points


def findDoblePointFromList(points,isPoly,full_list_double=False):
    cls_dbPoints=DublePoints()
    pt_count=len(points)
    if isPoly:
        pt_count=pt_count-1
    for i in range(pt_count):
        cls_dbPoints.add(i,points[i].x,points[i].y)
    if cls_dbPoints.ExistDublePoints:

        dblpoint=cls_dbPoints.getDoublePoints(full_list_double)

        '''
        geo_points=[]
        for pt in dblpoint:
            geo_points.append(Point(pt['x'],pt['y']))
        return geo_points
        '''
        if dblpoint is not None or len(dblpoint)>0:
            return dblpoint
    return None

def findDoublePoint(geom:Geometry):
    if geom is None:
        return None
    if geom.type == GeometryType.Point:
        return None
    if geom.type==GeometryType.Line:
        if geom.get_length()<=0.0:
            return Point(geom.begin)
    if geom.type==GeometryType.Polygon:
        list_points=[]
        duble_points_ext=findDoblePointFromList(geom.points,True)
        if duble_points_ext is not None:
            list_points.extend(duble_points_ext)
        count_holes_poly=len(geom.holes)
        if count_holes_poly>0:
            for hole in geom.holes:
                dbPointsHole=findDoblePointFromList(hole,True)
                if dbPointsHole is not None:
                    list_points.extend(dbPointsHole)

        if len(list_points)>0:
            list_out_geo_points=[]
            for pt_i in list_points:
                list_out_geo_points.append(Point(pt_i['x'],pt_i['y']))
            return list_out_geo_points
        return None
    return None
def deleteDoublePoint(geo_base,geo_double):
    out_geometry=None
    if geo_base is None:
        return None
    if geo_base.type == GeometryType.Point:
        return None
    if geo_base.type==GeometryType.Line:
        if geo_base.get_length()<=0.0:
            return None
    if geo_base.type==GeometryType.Polygon:
        list_points=[]
        duble_points_ext=findDoblePointFromList(geo_base.points,True,True)
        if duble_points_ext is not None:
            out_geometry=geo_base.clone()
            count_pts=len(duble_points_ext)
            for i in range(count_pts-1):
                id=count_pts-1-i
                id_point=duble_points_ext[id]['id']
                try:
                    out_geometry.points.remove(id_point)
                except Exception as ex:
                    print(ex)

        count_holes_poly=len(geo_base.holes)
        if count_holes_poly>0:
            id_hole=0
            for hole in geo_base.holes:
                duble_points_ext=findDoblePointFromList(hole,True,True)
                if duble_points_ext is not None:
                    if out_geometry is None:
                        out_geometry=geo_base.clone()
                    count_pts=len(duble_points_ext)
                    for i in range(count_pts-1):
                        id=count_pts-1-i
                        id_point=duble_points_ext[id]['id']
                        try:
                            out_geometry.holes[id_hole].remove(id_point)
                        except Exception as ex:
                            print(ex)
                id_hole=id_hole+1
        return out_geometry
    return None


