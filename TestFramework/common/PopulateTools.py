import json
from elasticsearch import Elasticsearch

class load:
    @staticmethod
    def loadCategories(filename:str) -> list:
        with open(filename,"r") as tempFileObject:
            context=tempFileObject.read()
        return [x for x,y in json.loads(context).items()]

class remove:
    @staticmethod
    def nullDatabase(url=None):
        if url:
            return remove._nullDatabase(Elasticsearch([url]))
        return remove._nullDatabase(Elasticsearch())

    @staticmethod    
    def _nullDatabase(databaseClientObject:object):
        res=databaseClientObject.indices.delete(index="_all")
        print(res)
