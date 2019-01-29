from common.PopulateTools import remove,load
from pymongo import MongoClient
import logging
import json
from specification.documentSpecification import Document
from specification.DateTimeUtills import DateRangeRetriever,Utills
import sys
from time import time
import random
import pprint



def usage():
    print("USAGE:       python3 po_query.py <p(x)> <s>")
    print("@PARAM p(x)  the maximum fetched probabillity")
    print("@PARAM s     the step (smaller step more queries :P)")
def main():

    if len(sys.argv) <3:
        usage()
        exit(-1)
    cli=MongoClient()
    scienceBranches=load.loadCategories("resources/bos.json")
    sb=chooseScienceBranch(scienceBranches)
    print("Random Science Branch :"+sb)
    
    b=DateRangeRetriever.getMaxOfGivenPercent(float(sys.argv[1]),1483232461,1488330061)

    print("The max 8601 : "+Utills._to8601(b)+" has P(x)="+sys.argv[1])

    print("Starting from zero with step "+sys.argv[2])

    db=cli['Experiments'][sb]
    
    i=0.01
    while(i<float(sys.argv[1])):
        t1=time()
        b=DateRangeRetriever.getMaxOfGivenPercent(i,1483232461,1488330061)
        query=db.find({"exp_meta.period.timestamp_start":{"$lt":b}})
        print("percentile "+str(i)+" by performing "+str(int(1/(time()-t1)))+ " que/sec ")
        i+=float(sys.argv[2])


def chooseScienceBranch(scienceBranches:list)->str:
    return scienceBranches[random.randint(0,len(scienceBranches))]

main()
