import sys
import logging
import json
import os
def loadsources(pathstring):
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
def organise(paramString):
    pass

def main(argv):
    
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
    loadsources(argv[s+1])
    logging.debug("Parse the -o parameter")
    organise(argv[o+1])

    
    


def usage():
    logging.critical("invalid usage")

def welcomeMessage():
    logging.info("""
        \tWelcome to sciencefs (prototype version)
        \tVersion 0
        \tStarting...
    """)
if __name__=="__main__":
    main(sys.argv)


