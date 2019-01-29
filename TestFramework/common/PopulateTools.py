import json
from pymongo import MongoClient

class load:
    @staticmethod
    def loadCategories(filename:str) -> list:
        with open(filename,"r") as tempFileObject:
            context=tempFileObject.read()
        return [x for x,y in json.loads(context).items()]

class remove:
    initialDbs=['admin', 'config', 'local']
    @staticmethod
    def nullDatabase(url=None):
        if url:
            return _nullDatabase(MongoClient(url))
        return remove._nullDatabase(MongoClient())

    @staticmethod    
    def _nullDatabase(databaseClientObject:object):
        for dbName in databaseClientObject.list_database_names():
            if(dbName not in remove.initialDbs):
                databaseClientObject.drop_database(dbName)
                print(dbName+" will deleted")
