from pathlib import Path

import axipy

path_tab="E:\\temp\\testCs.tab"
name_tab="source"
table=axipy.da.catalog_service.find(name_tab)
cs_source=table.coordsystem
attrs=[]
attrs.append(axipy.attr.integer('id_point'))
attrs.append(axipy.attr.integer('id_point2'))
schema= axipy.Schema(attrs, coordsystem=cs_source)
name_tab=Path(path_tab).stem
definition={
    'src':path_tab,
    'schema':schema,
    'dataobject':name_tab
}
table_out= axipy.io.create(definition)
ft= axipy.Feature()
ft['id_point']=1
ft.geometry= axipy.Point(2220609, 458300,cs_source)
table_out.insert([ft])