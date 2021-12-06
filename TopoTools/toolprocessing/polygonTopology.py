from axipy import Polygon, MultiPolygon, GEOMETRY_ATTR, GeometryCollection, GeometryType


#from TopologyTools.process.utils.toolSelfIntersection import geoIntersectToPolygons

def geoIntersectToPolygons(geo_obj_intersect):
    if isinstance(geo_obj_intersect,Polygon) or isinstance(geo_obj_intersect,MultiPolygon):
        return geo_obj_intersect
    if not (isinstance(geo_obj_intersect,Collection)):
        return None
    list_geo_poly=[]
    cnt=geo_obj_intersect.collectionSize()
    for i in range(cnt):
        item_geo=geo_obj_intersect.geometryAt(i)
        if isinstance(item_geo,Polygon) or isinstance(item_geo,MultiPolygon):
            list_geo_poly.append(item_geo)
    if len(list_geo_poly)==0:
        return None
    if len(list_geo_poly)==1:
        return list_geo_poly[0]
    resul_geo=MultiPolygon(geo_obj_intersect.coordsystem)
    for geo_item in list_geo_poly:
        resul_geo.append(geo_item)
    return resul_geo
class PolyIntersect:
    __def_table=None

    def __init__(self,table_sourec):
        self.__def_table=table_sourec

    # поиск перекрытий между полигонами
    def findPolyIntersect(self,id_ft,base_geo_source):
        base_geo=base_geo_source
        if base_geo is None:
            return None

        b_valid=base_geo_source.is_valid
        if not b_valid:
            # базовая геометрия не валидна
            base_geo=base_geo_source.normalize()
        bound_geo = base_geo.bounds
        mbr_fts = self.__def_table.items(bound_geo)

        intresect_polygons=[]
        for ft in mbr_fts:
            if int(ft.id)<=id_ft:
                continue
            cur_geo=ft[GEOMETRY_ATTR]
            if not(isinstance(cur_geo,Polygon) or isinstance(cur_geo,MultiPolygon)):
                continue
            if not cur_geo.is_valid:
                cur_geo=cur_geo.normalize()
            geo_intersect=base_geo.intersection(cur_geo)
            #geo_poly_intersect=geoIntersectToPolygons(geo_intersect)
            #if not (isinstance(geo_intersect,Polygon) or isinstance(geo_intersect,MultiPolygon) or isinstance(geo_intersect,GeometryCollection)):
            if geo_intersect is None:
                continue
            if not (geo_intersect.type==GeometryType.Polygon or geo_intersect.type==GeometryType.MultiPolygon or geo_intersect.type==GeometryType.GeometryCollection):
                continue
            if geo_intersect.type==GeometryType.GeometryCollection:
                out_geo_collection=GeometryCollection(geo_intersect.coordsystem)
                for geo_simle in geo_intersect:
                    if geo_simle.type==GeometryType.Polygon or geo_simle.type==GeometryType.MultiPolygon:
                        out_geo_collection.append(geo_simle)
                if len(out_geo_collection)>0:
                    if len(out_geo_collection)>1:
                        geo_intersect=out_geo_collection
                    else:
                        geo_intersect=out_geo_collection[0]
                else:
                    geo_intersect=None
            if geo_intersect is not None:
                intresect_polygons.append(geo_intersect)
        if len(intresect_polygons)==0:
            return None
        return intresect_polygons
