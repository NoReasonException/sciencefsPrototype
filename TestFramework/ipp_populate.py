
from common.PopulateTools import remove,load
from pymongo import MongoClient
import logging
import json
from specification.documentSpecification import Document
from specification.DateTimeUtills import DateRangeBuilder
import sys
from time import time

a=Document("specification/attempt1.json")

#create the db obj
cli=MongoClient()
#erase previous schemas
remove.nullDatabase()
#load the science branches to a generator
scienceBranches=load.loadCategories("resource/bos.json")



