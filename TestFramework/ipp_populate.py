
from common.PopulateTools import remove,load
from pymongo import MongoClient
import logging
import json
from specification.documentSpecification import Document
from specification.DateTimeUtills import DateRangeBuilder
import sys
from time import time
from math import ceil

def usage():
    print("USAGE:       python3 ipp_populate.py <n> <p>")
    print("@PARAM n:    The number of documents per-category")
    print("@PARAM p:    The period duration variable (see docs)")

def getTimeSlot(period:int,timestamp:int)->int:
    return period*(ceil((timestamp-period)/period))

def populate(mongoDBClient:object,\
        initialTimestamp:int,\
        period:int,\
        endTimestamp:int,\
        documentNumber:int,\
        scienceBranches:list,\
        documentBuilder:object)->None:

    for branch in scienceBranches:
        n=documentBuilder.massBuilder(\
                    DateRangeBuilder.\
                    simpleBuilderLambda(documentNumber,initialTimestamp,endTimestamp))

        for j in n:
            jsondict=json.loads(j)
            newTimestamp=jsondict["exp_meta"]["period"]["timestamp_start"]
            print("newTimestamp = "+str(newTimestamp)+" on timeslot "+\
                    str(getTimeSlot(period,newTimestamp)))
            mongoDBClient[str(getTimeSlot(period,newTimestamp))][branch].insert(jsondict)



def main():

    if len(sys.argv)<3:
        usage()
        exit(-1)

    documentBuilder=Document("specification/attemt1.json")
    #create the db obj
    cli=MongoClient()
    #erase previous schemas
    remove.nullDatabase()
    #load the science branches to a generator
    scienceBranches=load.loadCategories("resources/bos.json")
    
    populate(cli,1483232461,int(sys.argv[2]),1488330061,int(sys.argv[1]),scienceBranches,documentBuilder)


main()
#print(getTimeSlot(int(sys.argv[1]),int(sys.argv[2])))
