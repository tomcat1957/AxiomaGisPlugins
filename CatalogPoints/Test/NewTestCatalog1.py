import axipy

from CatalogPoints.toolprocessing.SimpleGeometryCatalog import BuildCatalog

property_out={}
name_table='TestData'
#name_table='TestData1'
table=axipy.app.mainwindow.catalog.find(name_table)
property_out['source_table']=name_table
property_out['out_coordSys']=table.coordsystem
property_out['key_field']="ID"
property_out['out_path']="E:\\Support\\AxiomaTesting\\CatalogPoints\\points.tab"
property_out['out_path']="E:\\Support\\AxiomaTesting\\CatalogPoints\\pointsEx.xlsx"
property_out['out_path']="E:\\Support\\AxiomaTesting\\CatalogPoints\\Points"
property_out['all_one_files']=False
property_out['out_format']="MapInfo"
#property_out['out_format']="Excel(xlsx)"
BuildCatalog(property_out)