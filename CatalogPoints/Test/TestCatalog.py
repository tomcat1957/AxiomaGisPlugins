import axipy

from CatalogPoints.toolprocessing.SimpleGeometryCatalog import PointCatalog
from CatalogPoints.toolprocessing.Utils import createCatalogSchema, createTab, CartesianObjectDistance

name_tab="ВСЕ_ЗОНЫ"
table=axipy.da.catalog_service.find(name_tab)
cs_source=table.coordsystem
att_id=table.schema[0]
tab_out_schema=createCatalogSchema(att_id,cs_source,True,False)
path_table_out="E:\\temp\\catalog_points.tab"
tab_out=createTab(path_table_out,tab_out_schema)
dist_unit_m= axipy.cs.unit.m
cls_distance=CartesianObjectDistance(dist_unit_m)
pt_catalog=PointCatalog(table,0,tab_out,cls_distance)
pt_catalog.run()