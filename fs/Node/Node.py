from time import time
from stat import S_IFDIR,S_IFREG
class Node:
    """
        404: Docstring not found(i will add doc later yo!)
        but , a important note

        the field data is abstract , when it is file contains the context of file
        when it is directory has the child files

        thanks
        Stefan
        [i wrote this text with 3 hours of sleep and 4 cups of coffe :) ]


    """
    @staticmethod
    def create(fs,parent,name,mode,typeoffile):
        now=time()
        return Node(parent,name,now,now,now,2,fs,mode,typeoffile)
    @staticmethod
    def createRegularFile(fs,parent,name,mode):
        return Node.create(fs,parent,name,mode,S_IFREG)
    @staticmethod
    def createDirectoryFile(fs,parent,name,mode):
        return Node.create(fs,parent,name,mode,S_IFDIR)
    def __init__(self,parent,name,atime,mtime,ctime,nlink,fs,mode,typeoffile):
        self.__parent=parent
        self.__name=name
        self.__size=0
        self.__atime=atime
        self.__mtime=mtime
        self.__ctime=ctime
        self.__nlink=nlink
        self.__fs=fs
        self.__mode=(mode|typeoffile)
        if(typeoffile==S_IFDIR):
            self.__data=list()
        else:
            self.__data=None
    @staticmethod
    def pathToNodeTranslator(rootNode,path):
        tmp=rootnode
        pathelements=path.split('/')
        
            
    
    def getFullPath (self):
        retval=[self.getName()]
        tmp=self
        
        while(not tmp.isRoot()):
            tmp=tmp.getParent()
            retval.append(tmp.getName())
            
        """
        reverse and convert to standard path
        """
        return str(retval[::-1]).\
                        replace("[","").\
                        replace("]","").\
                        replace(",","").\
                        replace("'","").\
                        replace(" ","/")[1:]

    def getName     (self):return self.__name
    def getParent   (self):return self.__parent
    def getSize     (self):return self.__size
    def getATime    (self):return self.__atime
    def getMTime    (self):return self.__mtime
    def getCTime    (self):return self.__ctime
    def getNLink    (self):return self.__nlink
    def getFs       (self):return self.__fs
    def getMode     (self):return self.__mode
    def isFile      (self):return (self.__mode&S_IFREG)!=0
    def isDirectory (self):return (self.__mode&S_IFDIR)!=0
    def getData     (self):return self.__data
    def isRoot      (self):return self.__parent==None

    def setData     (self,data):self.__data=data
    def getChildren (self):
        if self.isFile():
            raise Exception('Regular files cant have children')
        return tuple(self.getData())
    def addChildren(self,child):
        if self.isFile():
            raise Exception('Regular files cant have children')
        self.__data.append(child)
        child.__parent=self
        return child

