import logging
import pymongo
import json
import sys
from pymongo.errors import ConnectionFailure

def main(url):
    logging.basicConfig(level=logging.DEBUG,format="%(levelname)s:\t|%(msg)s")
    c=initializeDB(sys.argv[1])
    if c is None:
        return -1
    for i in range(3):
        with open("testdata/"+str(i+1)+".json") as sample:
            tmp=json.loads(sample.read())
            logging.info("Insert "+str(tmp))
            c.sciencefs.files.insert_one(tmp)

   
def initializeDB(url):
    clientObject=pymongo.MongoClient(url)
    try:
        clientObject.admin.command("ismaster")
        pass
    except ConnectionFailure as e:
        logging.critical("MongoDB Connection failed : "+str(e));
        return None
    return clientObject

main(sys.argv[1])
