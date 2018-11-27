from collections import defaultdict
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit
from time import time
import inspect
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
from etc.Info import Info as info
from Node.Node import Node
import logging
import threading


class ScienceFs(Operations):
    """===========================
        ScienceFs(SF) prototype
       ==========================
        
        This is the main filesystem class of fusepy sciencefs project




        :sectionauthor : Stefanos Stefanou , University of Reading , stefannstefanou@gmail.com
        :platform      : Linux 14.x , FreeBSD 11.x
        
        TODO's 
            1) implement stat-fs to avoid read-only fs error

       """
    def __init__(self):
        self.fd=4 #Just a random number , we dont care about file desciptors because we know for the prototype that only one user will perform calls 
        self.rootNode=Node.createDirectoryFile(self,None,"/",0o755) #this is the root node

    def create(self, path, mode, fi=None):
        print(".create on "+path)
        try:
            pathsplit=path.split("/")
            filename=pathsplit[-1]
            parent=pathsplit[-2]
            node=Node.createRegularFile(self,None,filename,mode)
            if(parent==""):
                self.rootNode.addChildren(node)
            else:
                Node.pathToNodeTranslator(self.rootNode,self.__getParentPath(path)).addChildren(node)
        except Exception as e:
            print("Exception thrown : %s on create at path %s parent %s"%(str(e),path,self.__getParentPath(path)))
            raise e
        self.fd+=1;
        print("...completed")
        return self.fd

    @staticmethod
    def __getParentPath(path):
        return path[0:path.rfind('/')]


    def getattr(self, path, fh=None):
#            raise FuseOSError(ENOENT)
        
        try:
            fileref=Node.pathToNodeTranslator(self.rootNode,path)
            if(fileref==None):
                raise FuseOSError(ENOENT)
            x=fileref.toStandardDict()
            print(str(x))
            now=time()    
            print("getattr COMPLETED")
            return x


        except Exception as e:
            print(e)
            raise FuseOSError(ENOENT)

    def mkdir(self, path, mode):
        print("mkdir requested on path"+path)
        try:
            pathsplit=path.split("/")
            folder=pathsplit[-2]
            filename=pathsplit[-1]
            node=Node.createDirectoryFile(self,None,filename,mode)
            if(folder==""):
                self.rootNode.addChildren(node)
            else:
                Node.pathToNodeTranslator(self.rootNode,self.__getParentPath(path)).addChildren(node)
        except Exception as e:
            print(str(e)+"on creation (path"+path+")")
            raise e
 
        except Exception as e:
            print(e)
            raise e

    def open(self,path,fd=None):
        self.fd+=1
        return self.fd
    def opendir(self, path):
        try:
            """
                Returns an numberical file handle for a directory , simillar to open() for regular files(S_IFREG inodes)
    
            :param path: The path
            :return: a number , file descriptor , always positive and over 3(stdin=1,stdout=2,stderr=3)
            """
            print("opendir "+path)
            self.fd+=1
            return self.fd
        except Exception as e:
            print(str(e) +"on .opendir")
            raise e
    def read(self, path, size, offset, fh):
        try:
            node=Node.pathToNodeTranslator(self.rootNode,path)
            print("Data : "+node.getData()+" FROM node : "+node.getName())
            return node.getData();
        except Exception as e:
            print(str(e)+" on .read()")
            return "nodata"



    def readdir(self, path, fh):
        """
            Returns a list([]) with all files and directories available + . and .. (current and previous dir)
        :param path: the path of the dir asking the files

        WARNING , I STUCK 102810281 HOURS -> ALWAYS RETURN THE NAME OF THE FILES , WITH NO /
        AS THE FIRST CHARACTER

        :param fh: the
        :return:
        """
        print(".readdir request issued on folder"+path)
        try:
            currentNodeChildren = Node.pathToNodeTranslator(self.rootNode,path).getData()
            retval=[".",".."] + [x.getName() for x in currentNodeChildren]
            print("the returned children is "+str(retval))
            return retval
        except Exception as e:
            print(e)
            return [".",".."]

    def write(self, path, data, offset, fh):
        print("WRITE")
        try:
            print("write op on "+str(path)+" the data "+data)
            node=Node.pathToNodeTranslator(self.rootNode,path)    
            node.setSize(len(data))
            node.setData(data)
            print("node "+node.getName() +" updated with data "+node.getData())
        except Exception as e:
            print("ERR ON WRITE")
            print(str(e))
        return len(data)


class ScienceFsThread(threading.Thread):
    def __init__(self,fs,mountpoint):
        threading.Thread.__init__(self)
        self.__fs=fs
        self.__mnt=mountpoint
    def getFs(self):return self.__fs
    def run(self):
        fuse = FUSE(self.__fs,self.__mnt, foreground=True,allow_other=True)


"""import os
import sys
if __name__ == "__main__":
    
    logging.basicConfig(level=logging.DEBUG)
    fuse = FUSE(ScienceFs(), "/home/noreasonexception/Desktop/sciencefs/sciencefsPrototype/tst/"+sys.argv[1], foreground=True,allow_other=True)
    x=ScienceFs()

    x.create("/hello",0o755)
    x.write("/hello","hello",0,None)
    print(x.read("/hello",0,0,0)+" returned from /hello")

"""
