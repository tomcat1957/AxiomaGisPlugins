from axipy import attr, Schema, io, CoordSystem

path_out_tab="E:/temp/test1Z.tab"
cs_out=CoordSystem.from_prj('1, 104')
att_key=attr.integer('key_field')
attrs=[]
attrs.append(att_key)
attrs.append( attr.double('x'))
attrs.append( attr.double('y'))
schema_tab=Schema(attrs)
definition={
    'src':path_out_tab,
    'schema':schema_tab
}
try:
    table= io.create(definition)
    print("Table create ")
except Exception as ex:
    print(ex)