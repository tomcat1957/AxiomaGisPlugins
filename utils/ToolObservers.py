import axipy
#from axipy import observers


def createCustomObserver(name_observer,def_value):
    observer=None
    try:
        observer= axipy.state_manager.find(name_observer)
    except:
        pass
    if observer is not None:
        return observer,False
    observer= axipy.state_manager.create(name_observer, def_value)
    return observer,True
def ObserverCountOpenVectorTable(name_observe):
    observer,new_observer=createCustomObserver(name_observe,False)
    if not new_observer:
        return observer
    def check_observer():
        def isVector(obj):
            if not isinstance(obj, axipy.Table):
                return False
            return obj.is_spatial
        vectors = list(filter( isVector, axipy.da.catalog_manager.objects))
        if len(vectors)>0:
            observer.setValue(True)
        else:
            observer.setValue(False)
        return observer
    axipy.da.catalog_manager.updated.connect(check_observer)
    return observer