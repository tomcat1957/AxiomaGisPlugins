import math

from axipy import Geometry, GeometryType, Polygon, LineString, MultiPolygon, MultiLineString, GeometryCollection


def AngleTriangle(d1,d2,d3):
    angle_cos=0.0
    try:
        angle_cos=(d1*d1+d2*d2-d3*d3)/(2*d1*d2)
    except:
        return 0.0
    '''
    if angle_cos<=-1 or angle_cos>=1:
        return 0
    '''
    try:
        angle=math.acos(angle_cos)
    except:
        angle=0
    return angle
def findAngleLimFromPoints(points,base_cs,lim_angle_rad):
    if len(points)<=2:
        return None
    list_out_points=[]
    pt1=points[0]
    for i in range(1,len(points)-1):
        pt2=points[i]
        pt3=points[i+1]
        d1,azimut1=Geometry.distance_by_points(pt1,pt2,base_cs)
        d2,azimut2=Geometry.distance_by_points(pt2,pt3,base_cs)
        d3,azimut3=Geometry.distance_by_points(pt3,pt1,base_cs)
        angle=AngleTriangle(d1,d2,d3)
        #print(str(i)+" "+str(angle)+" grd="+str(math.degrees(angle)))
        if angle<=lim_angle_rad:
            list_out_points.append({'point':pt2,'index':i})
        pt1=pt2
    if len(list_out_points)==0:
        return None
    return list_out_points
def findAngleLim(geo:Geometry,lim_angle_rad):
    out_points=[]
    if geo.type==GeometryType.Point or geo.type==GeometryType.Line or geo.type==GeometryType.RoundedRectange or geo.type==GeometryType.Rectange or geo.type==GeometryType.Arc or geo.type==GeometryType.MultiPoint or geo.type==GeometryType.Text:
        return None
    if geo.type==GeometryType.Polygon:
        list_out_points=[]
        list_point=list(iter(geo.points))
        list_point.append(list_point[1])
        #del list_point[-1]
        tem_list_points=findAngleLimFromPoints(list_point,geo.coordsystem,lim_angle_rad)

        if tem_list_points is not None:
            list_out_points.extend(tem_list_points)

        if len(geo.holes)>0:
            for hole in geo.holes:
                list_point=list(iter(hole))
                list_point.append(list_point[1])
                tem_list_points=findAngleLimFromPoints(list_point,geo.coordsystem,lim_angle_rad)
                if tem_list_points is not None:
                    list_out_points.extend(tem_list_points)
        if len(list_out_points)==0:
            return None
        return tem_list_points
    if geo.type==GeometryType.LineString:
        list_point=list(iter(geo.points))
        tem_list_points=findAngleLimFromPoints(list_point,geo.coordsystem,lim_angle_rad)
        return tem_list_points
    if geo.type==GeometryType.MultiPolygon or geo.type==GeometryType.GeometryCollection or geo.type==GeometryType.MultiLineString:
        list_points=[]
        for geo_simple in geo:
            temp_point=findAngleLim(geo_simple,lim_angle_rad)
            if temp_point is None:
                continue
            list_points.extend(temp_point)
        return list_points
def findIndexPnt(ponts_err,index):
    return [element for element in ponts_err if element["index"] ==index]
def removePoints(list_points,list_erorr_point,isPolygon=True):
    if list_erorr_point is None or len(list_erorr_point)==0:
        return list_points
    out_points=[]
    removeFirstPoint=False
    for pt in list_erorr_point:
        index_pt=pt['index']
        if (index_pt==len(list_points)-1) and isPolygon:
            #del list_points[index_pt-1]
            del list_points[0]
            removeFirstPoint=True
    for i in range(len(list_points)):
        pnts_err=findIndexPnt(list_erorr_point,i)
        if len(pnts_err)==0:
            out_points.append(list_points[i])
        '''
        pt_err=pnts_err[0]
        if len(pt_err)==0:
            continue
        index_pt=pt_err['index']
        if index_pt==i:
            continue
        out_points.append(pt_err['point'])
        #del list_points[index_pt]
        
        if index_pt==len(list_points):
            del list_points[0]
        '''
    if len(out_points)>2 and isPolygon and removeFirstPoint:
        out_points.append(out_points[0])
    return out_points

def correctLimAngle(geo,angle_lim,base_coordsys=None):
    if geo.type==GeometryType.Point or geo.type==GeometryType.Line or geo.type==GeometryType.RoundedRectange or geo.type==GeometryType.Rectange or geo.type==GeometryType.Arc or geo.type==GeometryType.MultiPoint or geo.type==GeometryType.Text:
        return None
    out_cs=geo.coordsystem
    if out_cs is None:
        out_cs= base_coordsys
    if geo.type==GeometryType.Polygon:
        list_point=list(iter(geo.points))
        list_point.append(list_point[1])
        tem_list_points=findAngleLimFromPoints(list_point,out_cs,angle_lim)
        if (len(list_point)-1)<=4 :
            return None
        new_pts=removePoints(list(iter(geo.points)),tem_list_points)
        if len(new_pts)<=3:
            return None
        new_out_geometry=Polygon(new_pts,out_cs)
        for hole in geo.holes:
            list_point=list(iter(hole))
            list_point.append(list_point[1])
            tem_list_points=findAngleLimFromPoints(list_point,out_cs,angle_lim)
            if (len(list_point)-1)>3 :
                new_pts=removePoints(list(iter(hole)),tem_list_points)
                if len(new_pts)>3:
                    new_out_geometry.holes.append(new_pts)
        return new_out_geometry
    if geo.type==GeometryType.LineString:
        list_point=list(iter(geo.points))
        tem_list_points=findAngleLimFromPoints(list_point,out_cs,angle_lim)
        new_pts=removePoints(list(iter(geo.points)),tem_list_points,False)
        if new_pts is None or len(new_pts)<2:
            return None
        new_geo=LineString(new_pts,geo.out_cs)
        return new_geo
    out_geo=None
    if geo.type==GeometryType.MultiPolygon:
        out_geo=MultiPolygon(geo.coordsystem)
    if geo.type==GeometryType.MultiLineString:
        out_geo=MultiLineString(geo.coordsystem)
    if geo.type==GeometryType.GeometryCollection:
        out_geo=GeometryCollection(out_cs)
    if out_geo is not None:
        for poly in geo:
            new_poly=correctLimAngle(poly,angle_lim,out_cs)
            if new_poly is not None:
                out_geo.append(new_poly)
        if len(out_geo)==0:
            return None
        if len(out_geo)==1:
            return out_geo[0]
        return out_geo
    return None





