from common.PopulateTools import remove,load
from pymongo import MongoClient
import logging
import json
from specification.documentSpecification import Document
from specification.DateTimeUtills import DateRangeBuilder
import sys
from time import time
a=Document("specification/attemt1.json")

#create the db obj
cli=MongoClient()
#erase previous schemas
remove.nullDatabase("")
#load the science branches 
scienceBranches=load.loadCategories("resources/bos.json")
for i in scienceBranches:
    n=a.massBuilder(DateRangeBuilder.simpleBuilderLambda(int(sys.argv[1]),1483232461,1488330061))
    t1=time()
    tmp=str()
    for j in range(200):
        tmp=next(n)
        cli['Experiments'][i].insert(json.loads(tmp))
        print(tmp)
    t2=time()
    print(str(int(int(sys.argv[1])/(t2-t1)))+"req/sec")
        

