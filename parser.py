import sys
import logging
import json
import os
from fs.ScienceFs import ScienceFs,ScienceFsThread
from fuse import FUSE,FuseOSError,Operations,LoggingMixIn
from mediator.fpmediator import ParserToFsMediator
import time
class Parser:


    
    def loadsources(self,pathstring):
        """
        loadsources 
            loads the list of .json files and returns a list of json strings to the caller
        
            @param pathstring : the directory of the files
            @Note
                every file in the given directort will be parsed as json
                so consider remove irrelevant files
        """
    
        dictionaryList=list()
        tempPath=None
        try:
            for i in os.listdir(pathstring):
                tempPath=(pathstring+i)
                with open(tempPath,"r") as filefd:
                    logging.debug("attemt to load %s"%tempPath)
                    dictionaryList.append(json.loads(filefd.read()))
        except Exception as e:
            logging.error('Exception caught : %s'%e)
            raise e
        return dictionaryList

    def queryAnalyzer(self,paramString,data):
        """
            parse the -o (organise parameter) and returns the queried data
        """
        conditions=self.__getConditions(paramString)
        logging.debug("Search Query is : %s"%conditions)

        data=self.__applyConditions(conditions,data)
        logging.debug("%d experiments qualify "%len(data))
        return data
        

    def __getConditions(self,paramString):
        conditions=paramString.split("&")               #split in & in order to take the and's 
        return conditions
    def __applyConditions(self,conditions,data):
#        print(data)
        tempPointer=None
        equationPairSplitLeftHand=None
        tmpData=data
        returnlist=list()
        flag=False
        for c in data:
            tmpData=c
            for i in conditions:
                tmpData=c
                equationPair=i.split("=")
         #       print(equationPair)
                equationPairLeftHand=equationPair[0].split(".")
                equationPairRightHand=equationPair[1]
                for j in equationPairLeftHand:
                    tmpData=tmpData[j]
                if tmpData!=equationPairRightHand:
                    #print("%s != %s  %d.json"%(tmpData,equationPair[1],data.index(c)))
                    flag=True
                    break
            if(flag):
                flag=False
                continue
            returnlist.append(c)
                    
        return returnlist

            
            
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
        n,s,q,m=0,0,0,0
        sources=None 
        try:
            s=argv.index("-s") #source of .json file
            q=argv.index("-q") #query
            n=argv.index("-n") #namespace structure
            m=argv.index("-m") #mount point
        except:
            usage()
            return
        logging.info("parse -s parameter")
        sources=self.loadsources(argv[s+1])
        logging.info("Parse -q parameter")
        qualifyData=self.queryAnalyzer(argv[q+1],sources)
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


