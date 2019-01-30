from common.PopulateTools import remove,load
from elasticsearch import Elasticsearch
import logging
import json
from specification.documentSpecification import Document
from specification.DateTimeUtills import DateRangeBuilder
import sys
from time import time



def usage():
    print("USAGE : python3 po_populate.py <n> ")
    print("@param n : number of documents per category")

a=Document("specification/attemt1.json")


def main():
    if len(sys.argv)<2 :
        usage()
        exit(-1)
    #create the db obj
    cli=Elasticsearch() #TODO : make second parameter for the url

#    cli.indices.create(index='experiments')
    print("Experiment index created")
    
    #load the science branches 
    scienceBranches=load.loadCategories("resources/bos.json")
    for i in scienceBranches:
        n=a.massBuilder(DateRangeBuilder.simpleBuilderLambda(int(sys.argv[1]),1483232461,1488330061))
        t1=time()
        tmp=str()
        for j in range(int(sys.argv[1])):
            tmp=next(n)
            cli.index(index='experiments',doc_type=str(i),body=json.loads(tmp))
        t2=time()
        print(str(int(int(sys.argv[1])/(t2-t1)))+"req/sec")
main()
        

