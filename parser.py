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

    def organise(self,paramString,data):
        """
            parse the -o (organise parameter) and returns the queried data
        """
        conditions=self.__getConditions(paramString)
        logging.debug("Search Query is : %s"%conditions)

        data=self.__applyConditions(conditions,data)
        logging.debug("%d experiments qualify "%len(data))

        

    def __getStructure(self,paramString):
        pass
    def __getConditions(self,paramString):
	args=paramString.split("/")                 #split the initial string in / -> the first will be the query , the next will be the format of mount
        conditions=args[0].split("&")               #split in & in order to take the and's 
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
                equationPairLeftHand=equationPair[0].split(".")
                equationPairRightHand=equationPair[1]
                for j in equationPairLeftHand:
                    tmpData=tmpData[j]
                if tmpData!=equationPairRightHand:
                    print("%s != %s  %d.json"%(tmpData,equationPair[1],data.index(c)))
                    flag=True
                    break
            if(flag):
                flag=False
                continue
            returnlist.append(c)
                    
        return returnlist

            
            
        


    def __init__(self,argv):

        logging.basicConfig(level=logging.DEBUG,format="%(levelname)s\t|%(msg)s")
        welcomeMessage()
        s,o=0,0
        sources=None 
        try:
            s=argv.index("-s")
            o=argv.index("-o")
        except:
            usage()
            return
        logging.debug("parse the -q parameter")
        sources=self.loadsources(argv[s+1])
        logging.debug("Parse the -o parameter")
        self.organise(argv[o+1],sources)

    
    


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


