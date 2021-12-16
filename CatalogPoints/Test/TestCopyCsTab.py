from pathlib import Path

import axipy

path_tab_out="E:\\temp\\testCsCopy.tab"
'''
name_tab="source"
table=axipy.da.catalog_service.find(name_tab)
'''
path_source_tab="E:\\Support\\GIS_CAD\\0_ВСЕ\\0_ВСЕ.tab"
table= axipy.io.openfile(path_source_tab)
cs_source=table.coordsystem
attrs=[]
attrs.append(axipy.attr.integer('id_point'))
attrs.append(axipy.attr.integer('id_point2'))
schema= axipy.Schema(attrs, coordsystem=cs_source)
name_tab=Path(path_tab_out).stem
definition={
    'src':path_tab_out,
    'schema':schema,
    'dataobject':name_tab
}
table_out= axipy.io.create(definition)
ft= axipy.Feature()
ft['id_point']=1
ft.geometry= axipy.Point(2205312, 519617,cs_source)
table_out.insert([ft])