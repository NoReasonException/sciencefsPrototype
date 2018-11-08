import sys
import logging
import json
import os


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

            
            
    def namespaceStructureQueryAnalyzer(self,query,fs):
        pass

    def verifyMountPoint(self,mountPoint):
        if( not os.path.isdir(mountPoint)):
             logging.critical("No such file or directory :%s"%mountPoint)
             raise IOError()
        
    def loadfs(self,pathToMount):
        return None

    def __init__(self,argv):
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
        logging.debug("parse -s parameter")
        sources=self.loadsources(argv[s+1])
        logging.debug("Parse -q parameter")
        qualifyData=self.queryAnalyzer(argv[q+1],sources)
        logging.debug("Parse -m parameter")
        self.verifyMountPoint(argv[m+1])
        logging.debug("create  sciencefs object")
        self.fs=self.loadfs(argv[m+1])
        logging.debug("Parse -n parameter")
        self.namespaceStructureQueryAnalyzer(argv[n+1],self.fs)



    
    


def usage():
    logging.critical("invalid usage")

def welcomeMessage():
    logging.info("""
        \tWelcome to sciencefs (prototype version)
        \tVersion 0
        \tStarting...
    """)
if __name__=="__main__":
    Parser(sys.argv)


