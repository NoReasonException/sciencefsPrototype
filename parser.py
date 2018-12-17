import sys
import logging
import json
import os
from fs.ScienceFs import ScienceFs,ScienceFsThread
from fuse import FUSE,FuseOSError,Operations,LoggingMixIn
from mediator.fpmediator import ParserToFsMediator
import time
import pymongo
from pymongo.errors import ConnectionFailure
class Parser:

    def initializeDB(self,url):
        """
            initializeDB

            initializes the Database Connection and verifies that the url passed is correct()

            Note : Because after MongoDB 3.0 , the connection is always performed on background , without any formal way to
            verify that the url is ok , i perform a <<ismaster>> command imidiatelly , in order to force the API to throw ConnectionFailure
            in cause of error.(This is actually the doc suggestion)
        """
        clientObject=pymongo.MongoClient();
        try:
            clientObject.admin.command("ismaster")
            pass
        except ConnectionFailure as e:
            logging.critical("MongoDB Connection failed : "+str(e));
            raise e
        return clientObject
    def parseMongoDBQuery(self,query,clientObject):
        """
        parseMongoDBQuery 
        this method parses the user given query into a standard MongoDB API call

        the given query structure is explained below

                    databaseName|collectionName|{queryInStandardJson}

        The first two parameters is straightforward , the third one is the json who will passed into the .find() method
        in this version , due to deprecation of .eval() (and because is a crappy prototype) we do not support direct
        javascript calls (such as db.bla.blablabla({...})) .


        """
        query=query.split("|")
        return [x for x in (clientObject[query[0]][query[1]].find(json.loads(query[2])))]  #i know is terrible , but i love theese pythonic ways of writing...



    def namespaceStructureQueryAnalyzer(self,query,data,mountpoint,fs):
        """
        namespaceStructureQueryAnalyzer

        creates the given namespace structure anhd fill it with query data returned by queryAnalyzer
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
        n,s,q,m=0,0,0,0
        sources=None 
        try:
            u=argv.index("-u") #mongoDB url
            q=argv.index("-q") #mongoDB query
            n=argv.index("-n") #namespace structure
            m=argv.index("-m") #mount point
        except:
            usage()
            return
        
        logging.info("Parse -u parameter")
        clientObject=self.initializeDB(argv[u+1])  
        logging.info("Connection Estabilished : "+str(argv[u+1]))
        

        

        logging.info("Parse -q parameter")
        qualifyData=self.parseMongoDBQuery(argv[q+1],clientObject)
       
       
        print(str(qualifyData))
        
        #qualifyData need to have the final data needed to form the mount point
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
    logging.critical("usage -u <mongoDB url> -q <mongoDB search query> -m <mountPoint> -n <namespaceStructure>")

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


