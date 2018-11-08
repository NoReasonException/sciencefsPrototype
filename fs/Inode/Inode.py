from time import time
from stat import S_IFDIR,S_IFREG
class Inode:
    """
        404: Docstring not found(i will add doc later yo!)
        but , a important note

        the field data is abstract , when it is file contains the context of file
        when it is directory has the child files

        YES! i know that a real Inode has nothing to do with the 'term' data 
        but is a prototype , give me a break :) 

        thanks
        Stefan
        [i wrote this text with 3 hours of sleep and 4 cups of coffe :) ]


    """
    @staticmethod
    def create(dentry,fs,mode,typeoffile):
        now=time()
        return Inode(dentry,now,now,now,2,fs,mode,typeoffile)
    @staticmethod
    def createRegularFile(dentry,fs,mode):
        return Inode.create(dentry,fs,mode,S_IFREG)
    @staticmethod
    def createDirectoryFile(dentry,fs,mode):
        return Inode.create(dentry,fs,mode,S_IFDIR)
    def __init__(self,dentry,atime,mtime,ctime,nlink,fs,mode,typeoffile):
        self.__dentry=dentry
        self.__size=0
        self.__data=None
        self.__atime=atime
        self.__mtime=mtime
        self.__ctime=ctime
        self.__nlink=nlink
        self.__fs=fs
        self.__mode=(mode|typeoffile)
    def getDentry   (self):return self.__dentry
    def getSize     (self):return self.__size
    def getATime    (self):return self.__atime
    def getMTime    (self):return self.__mtime
    def getCTime    (self):return self.__ctime
    def getNLink    (self):return self.__nlink
    def getFs       (self):return self.__fs
    def getMode     (self):return self.__mode
    def isFile      (self):return (self.__mode&S_IFREG)!=0
    def isDirectory (self):return (self.__mode&S_IFDIR)!=0
    def getData     (self):return self__data
    

