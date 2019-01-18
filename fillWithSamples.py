from elasticsearch import Elasticsearch
from elasticsearch.client import ClusterClient
import logging
import json
import sys
def main(url):
    logging.basicConfig(level=logging.INFO,format="%(levelname)s:\t|%(msg)s")
    c=initializeDB(sys.argv[1])
    if c is None:
        return -1
    for i in range(3):
        with open("testdata/"+str(i+1)+".json") as sample:
            tmp=json.loads(sample.read())
            logging.info("Insert "+str(tmp))
            c.index(index="experiments16001700", doc_type='Physics', body=tmp)


   
def initializeDB(url):
    clientObject=Elasticsearch([url])
    try:
        ClusterClient(clientObject).get_settings()
    except ConnectionFailure as e:
        logging.critical("Connection to ES Node failed : "+str(e));
        return None
    return clientObject

main(sys.argv[1])
