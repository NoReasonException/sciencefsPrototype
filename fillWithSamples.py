import logging
import pymongo
import json
import sys


def main(url):
    logging.basicConfig(level=logging.DEBUG,format="%(levelname)s:\t|%(msg)s")
    c=pymongo.MongoClient(url)
    for i in range(3):
        with open("testdata/"+str(i+1)+".json") as sample:
            tmp=json.loads(sample.read())
            logging.info("Insert "+str(tmp))
            c.sciencefs.files.insert_one(tmp)

    
main(sys.argv[1])
