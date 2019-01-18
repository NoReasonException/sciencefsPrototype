import sys
import logging
import json
import os
from fs.ScienceFs import ScienceFs,ScienceFsThread
from fuse import FUSE,FuseOSError,Operations,LoggingMixIn
from mediator.fpmediator import ParserToFsMediator
import time
from elasticsearch import Elasticsearch
from elasticsearch.client import ClusterClient
class Parser:
     
           

    def verifyConnection(self,url):
        elasticObject=Elasticsearch([url])
        elasticClusterObject=ClusterClient(elasticObject)
        elasticClusterObject.get_settings() #force the elasticObject to start a suncronous connection
        print("ElasticSearch Node at "+url+":Connection established")
        return elasticObject

    def queryAnalyzer(self,elasticObject,query):
        retval=list()
        index_json_split=query.split("|")
        res=elasticObject.search(index=index_json_split[0],body=json.loads(index_json_split[1]))
        for hit in res['hits']['hits']:
            retval.append(hit["_source"])
        return retval




    def namespaceStructureQueryAnalyzer(self,query,data,mountpoint,fs):
        """
        namespaceStructureQueryAnalyzer

        creates the given namespace structure and fill it with query data returned by queryAnalyzer
        @param query        the user input query
        @param fs           the FUSE Filesystem Object
        @param data         the experiments who qualify
        @param mountpoint   the mountpoint of FUSE Filesystem 
        @return True on Success
        @throws Exception on any error (see message) TODO : make more specific exceptions
        """
        parsePath=query.split("/")
        tmpJsonObject=None
        """
        The actual code where creates the namespace as the user specified follows...
        """
        tmpPath=mountpoint 
        stringbuilder=""
        for experiment in data:
            for x in parsePath[:-1]:         
                tmpJsonObject=Parser.parseJsonQuery(experiment,x)
                #print("data[query] :"+str(tmpJsonObject)+" | found ")
                try:
                    self.fpMediator.mkdir(str(tmpPath)+"/"+str(tmpJsonObject))
                    logging.debug("Creating Folder "+str(tmpPath)+"/"+str(tmpJsonObject))
                except Exception as e:
                    pass
                tmpPath+="/"+tmpJsonObject

            for x in parsePath[-1].split(':'):
                print(str(experiment) + "is the experiment ")
                stringbuilder+=(Parser.parseJsonQuery(experiment,x)+":")

            x=open(tmpPath+"/results","a+")
            x.write(stringbuilder)
            x.close()
            stringbuilder=""
            tmpPath=mountpoint
            

    @staticmethod
    def parseJsonQuery(jsonRoot,query):
        """
        takes a query as second parameter of type 'element1.element2.element3.*' and returns the final JsonObject 
        @param jsonRoot     the root json object
        @param query        the query 
        @returns            a list() containing the json elements at the final layer(element3.*)
        """
        if("." not in query):
            return jsonRoot[query]
        else:
            tmpJsonObject=jsonRoot
            parsePathToJsonElement = query.split(".")
            for arrayFinder in parsePathToJsonElement:
                tmpJsonObject=tmpJsonObject[arrayFinder]
        return tmpJsonObject
            


    def verifyMountPoint(self,mountPoint):
        """
            a simple check to denode if the mountpoint exists and is a valid directory entry
            in case of error throws a OSError , and the main programm terminates
        
        """
        if( not os.path.isdir(mountPoint)):
             logging.critical("No such file or directory :%s"%mountPoint)
             raise IOError()
        logging.debug("Mountpoint Good")
        
    def loadfs(self,pathToMount):
        """
            loadfs method create a ScienceFS Operations Object and initializes the FUSE subsystem 
            throws FUSEOSError in any case of error



        """
        try:

            scienceFsObject = ScienceFs()
            logging.debug("ScienceFs object created")
	    scienceFsMainThread=ScienceFsThread(scienceFsObject,pathToMount)
            logging.debug("FUSE object created on thread")
            scienceFsMainThread.start()
            logging.debug("main thread started : mount completed at "+str(pathToMount))
            fpMediator=ParserToFsMediator(scienceFsObject,None)  #The mediator object will handle all the communication between Parser and Fusepy Filesystem(ScienceFs)
            logging.debug("Mediator Object Created")
            return fpMediator
        except Exception as e:
            logging.critical("on .loadfs(p) exception : "+str(e))
            raise e
    def __init__(self,argv):
        """
            Costructor of Parser Class
            just call the helper methods to initialize the ScienceFs Prototype

        """
        self.fs=None
        logging.basicConfig(level=logging.DEBUG,format="%(levelname)s\t|%(msg)s")
        welcomeMessage()
        n,u,q,m=0,0,0,0
        sources=None 
        try:
            q=argv.index("-q") #elasticSearch URI Query 
            u=argv.index("-u") #elasticSearch Node URL 
            n=argv.index("-n") #namespace structure
            m=argv.index("-m") #mount point
        except:
            usage()
            return


        
        
        logging.info("Parse -u parameter")
        self.elasticComObject=self.verifyConnection(argv[u+1])


        logging.info("Parse -q parameter")
        qualifyData=self.queryAnalyzer(self.elasticComObject,argv[q+1])
        

        #qualifyData need to have a JSON list of the final data
        
        logging.info("Parse -m parameter")
        self.verifyMountPoint(argv[m+1])
        logging.info("Mount Completed")
        self.fpMediator=self.loadfs(argv[m+1])
        self.fs=self.fpMediator.getFs()
        logging.info("Parse -n parameter")
        #self.fs=None
        time.sleep(1)
        self.namespaceStructureQueryAnalyzer(argv[n+1],qualifyData,argv[m+1],self.fs)
        


    
    


def usage():
    """
    A simple function return a message if some parameter is not given


    """
    logging.critical("usage -s <source> -q <searchQuery> -m <mountPoint> -n <namespaceStructure>")

def welcomeMessage():
    """
    A simple function returning a welcome message after denoting the integrity of the parameters

    """
    logging.info("""
        \tWelcome to sciencefs (prototype version)
        \tVersion 0
        \tStarting...
    """)
if __name__=="__main__":
    Parser(sys.argv)


