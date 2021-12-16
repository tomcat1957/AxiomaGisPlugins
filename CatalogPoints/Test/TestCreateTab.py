from axipy import attr, CoordSystem

from CatalogPoints.toolprocessing.Utils import createCatalogSchema, createTab

att_key=attr.integer('key_field')
path_out_tab="E:/temp/test1Z.tab"
cs_out=CoordSystem.from_prj('1, 104')
schema_tab=createCatalogSchema(att_key,cs_out)
tab=createTab(path_out_tab,schema_tab)
pass