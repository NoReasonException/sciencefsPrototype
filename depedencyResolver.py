import sys
import json
import logging
import os
def main(depedenciesFileName):
    
    logging.basicConfig(level=logging.DEBUG,format="%(levelname)s:\t|%(msg)s")
    logging.info("Installing...")
    for moduleName,installCommand in loadDepedencies(depedenciesFileName).iteritems():
        for i in range(2):
            try:
                logging.info("Load "+str(moduleName))
                __import__(moduleName)
                break
            except ImportError as e:
                if i==1:
                    logging.critical("Configuration failed , Install of module "+str(moduleName)+" failed , unknown reason")
                    return -1
                logging.error("Installation Failed : %s"%str(e))
                installModule(moduleName,installCommand)

def installModule(moduleName,installCommand):
    logging.info("attemt to install "+str(moduleName))
    os.system(installCommand)

def __loadDepedencies(depedenciesFileName):
    with open(depedenciesFileName,"r") as depedenciesFile:
        return depedenciesFile.read()

def loadDepedencies(depedenciesFileName):
    return json.loads(__loadDepedencies(depedenciesFileName))

main("depedencies.json")
