from axipy import Table


class AxiTableCache:
    __size_cache=100
    __cache_features=None
    __axi_table=None
    def __init__(self,axiTable:Table,size_cache=100):
        self.__axi_table=axiTable
        self.__size_cache=size_cache
    def Start(self):
        self.__cache_features=[]
    def Insert(self,ft):
        if len(self.__cache_features)>=self.__size_cache:
            #temp_list=self.__cache_features
            self.__axi_table.insert(self.__cache_features)
            #self.__axi_table.insert(features=self.__cache_features)
            #temp_list=None
            self.__cache_features=[]
        if isinstance(ft,list):
            self.__cache_features.extend(ft)
        else:
            self.__cache_features.append(ft)
        return True
    def End(self):
        if len(self.__cache_features)>0:
            self.__axi_table.insert(self.__cache_features)
        self.__cache_features=None


