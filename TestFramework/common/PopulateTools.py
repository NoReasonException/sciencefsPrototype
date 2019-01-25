import json
from pymongo import MongoClient

class load:
    @staticmethod
    def loadCategories(filename:str) -> list:
        with open(filename,"r") as tempFileObject:
            context=tempFileObject.read()
        return [x for x,y in json.loads(context).items]

class remove:
    initialDbs=['admin', 'config', 'local']
    @staticmethod
    def nullDatabase(url):
        cli=MongoClient()
        for dbName in cli.list_database_names():
            if(dbName not in remove.initialDbs):
                #cli[dbName].dropDatabase()
                print(dbName+" will deleted")

