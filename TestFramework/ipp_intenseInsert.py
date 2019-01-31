
from common.PopulateTools import remove,load
from elasticsearch import Elasticsearch
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

def nMonthsUnixOffset(months:int)->int:
    return(30*24*60*60)*months


def currentTimestampGenerator(numberOfTimestamps:int)->object:
    for i in range(numberOfTimestamps):
        yield int(time())


def intenseInsertTest(elasticSearchClient:object,\
        period:int,\
        documentNumber:int,\
        scienceBranches:list,\
        documentBuilder:object)->None:

    for branch in scienceBranches:
        n=documentBuilder.massBuilder(currentTimestampGenerator(documentNumber))


        t1=time()
        for j in n:
            jsondict=json.loads(j)
            newTimestamp=jsondict["exp_meta"]["period"]["timestamp_start"]
            elasticSearchClient.index(index=(str(getTimeSlot(period,newTimestamp))),doc_type=(branch),body=jsondict)
            
        t2=time()
        print("query speed\t"+str(int(documentNumber/(t2-t1))))




def main():

    if len(sys.argv)<3:
        usage()
        exit(-1)

    documentBuilder=Document("specification/attemt1.json")
    #create the db obj
    cli=Elasticsearch(['localhost:9200'])
    #load the science branches to a generator
    scienceBranches=load.loadCategories("resources/bos.json")
    
    intenseInsertTest(cli,int(sys.argv[2]),int(sys.argv[1]),scienceBranches,documentBuilder)


main()
#print(getTimeSlot(int(sys.argv[1]),int(sys.argv[2])))
