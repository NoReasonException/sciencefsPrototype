from common.PopulateTools import remove
import sys
def getArgv(index:int)->str:
    if(len(sys.argv)<=index):
        return None
    return sys.argv[index]

print("ElasticSearch null tool v0.1")
url=getArgv(1)
print("@param url: (WARNING : ITS MANDATORY) -> "+str(url))
remove.nullDatabase(url)
print("Bye")

