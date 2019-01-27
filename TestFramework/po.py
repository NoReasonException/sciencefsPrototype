from common.PopulateTools import remove,load
from pymongo import MongoClient
import logging

#create the db obj
cli=MongoClient()
#erase previous schemas
remove.nullDatabase("")
#load the science branches 
scienceBranches=load.loadCategories("resources/bos.json")
for i in scienceBranches:
    cli['Experiments'][i].insert({"hello":"world "})
    print(i)


