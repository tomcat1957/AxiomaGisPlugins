from axipy import Polygon, MultiPolygon, unit, AreaUnit


def CreatePolygonFromRect(mbr,cs):
    '''
    Rect to Polygon
    :param mbr: Rect
    :param cs:
    :return:
    '''
    points=[]
    points.append((mbr.xmin,mbr.ymin))
    points.append((mbr.xmin,mbr.ymax))
    points.append((mbr.xmax,mbr.ymax))
    points.append((mbr.xmax,mbr.ymin))
    points.append((mbr.xmin,mbr.ymin))
    geo_poly=Polygon(points,cs)
    return geo_poly
class GapDetection:
    __area_limit=0.0
    __obj_com_poly=None
    def __init__(self,limit_area):
        self.__area_limit=limit_area
    def addGeo(self,geo_curent):
        if self.__obj_com_poly is None:
            self.__obj_com_poly=geo_curent.clone()
        else:
            try:
                self.__obj_com_poly=self.__obj_com_poly.union(geo_curent)
            except:
                pass
        return
    def postProcessing(self):
        mbr=self.__obj_com_poly.bounds
        geo_mbr=CreatePolygonFromRect(mbr,self.__obj_com_poly.coordsystem)

        #envelope_obj=Polygon(self.__obj_com_poly.points,self.__obj_com_poly.coordsystem)
        envelope_obj=self.__obj_com_poly.convex_hull()
        geo_diff=geo_mbr.difference(self.__obj_com_poly)
        #geo_diff=envelope_obj.difference(self.__obj_com_poly)
        list_holes=[]
        if isinstance(geo_diff,Polygon):
            point_center=geo_diff.centroid()
            if envelope_obj.contains(point_center):
                list_holes.append(geo_diff)
        else:
            for poly in geo_diff:
                point_center=poly.centroid()
                if envelope_obj.contains(point_center):
                    area_gap_poly=poly.get_area(AreaUnit.sq_km)

                    if area_gap_poly<=self.__area_limit:
                        list_holes.append(poly.clone())
        if len(list_holes)==0:
            return None,geo_diff,self.__obj_com_poly
        #return list_holes,None,envelope_obj
        return list_holes,None,None
        #return None,geo_mbr,self.__obj_com_poly
        if len(list_holes)==1:
            return list_holes[0]
        result_polygons=MultiPolygon(self.__obj_com_poly.coordsystem)
        for poly in list_holes:
            result_polygons.append(poly)
        #return result_polygons,geo_diff,envelope_obj
        return None,geo_mbr,self.__obj_com_poly

