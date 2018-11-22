from collections import defaultdict
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit
from time import time
import inspect
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
from etc.Info import Info as info
from Node.Node import Node




class ScienceFs(LoggingMixIn, Operations):
    """===========================
        ScienceFs(SF) prototype
       ==========================
        
        This is the main filesystem class of fusepy sciencefs project




        :sectionauthor : Stefanos Stefanou , University of Reading , stefannstefanou@gmail.com
        :platform      : Linux 14.x , FreeBSD 11.x
        


       """
    def __init__(self):
        self.fd=14 #Just a random number , we dont care about file desciptors because we know for the prototype that only one user will perform calls 
        self.rootNode=Node.createDirectoryFile(self,None,"/",0o755) #this is the root node

    def chmod(self, path, mode):
        print("chmod "+path)


    def chown(self, path, uid, gid):
        print("chown "+path)

    def create(self, path, mode, fi=None):
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

    @staticmethod
    def __getParentPath(path):
        return path[0:path.rfind('/')]



    def destroy(self, path):
        print("destroy "+path)

    def flush(self, path, fh):
        print("flush "+path)

    def fsync(self, path, datasync, fh):
        print("fsync "+path)

    def fsyncdir(self, path, datasync, fh):
        print("fsyncdir "+path)

    def getattr(self, path, fh=None):
#            raise FuseOSError(ENOENT)
        try:
            fileref=Node.pathToNodeTranslator(self.rootNode,path)
            if(fileref==None):
                raise FuseOSError(ENOENT)
            return fileref.toStandardDict()
        except Exception as e:
            print(e)
            raise FuseOSError(ENOENT)
    
    def getxattr(self, path, name, position=0):
        print("getxattr "+path)
        return dict()

    
    def ioctl(self, path, cmd, arg, fip, flags, data):
        print("ioctl "+path)

    def link(self, target, source):
        print("link "+target+" | "+source)

    def listxattr(self, path):
        print("listxattr "+path)

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


    def mknod(self, path, mode, dev):
        print("mknod "+path)

    def open(self,path):
        self.fd+=1
        return self.fd
    def opendir(self, path):
        """
            Returns an numberical file handle for a directory , simillar to open() for regular files(S_IFREG inodes)

        :param path: The path
        :return: a number , file descriptor , always positive and over 3(stdin=1,stdout=2,stderr=3)
        """
        print("opendir "+path)
        self.fd+=1
        return self.fd

    def read(self, path, size, offset, fh):
        
        return 0

    def readdir(self, path, fh):
        """
            Returns a list([]) with all files and directories available + . and .. (current and previous dir)
        :param path: the path of the dir asking the files

        WARNING , I STUCK 102810281 HOURS -> ALWAYS RETURN THE NAME OF THE FILES , WITH NO /
        AS THE FIRST CHARACTER , THE DOCUMENTATION IN COMPLETELY FUCKED

        :param fh: the
        :return:
        """
        try:

            print(path+" readdir")

        
            currentNodeChildren = Node.pathToNodeTranslator(self.rootNode,path).getData()
        
            #print("readdir "+path +" returned children list is :"+currentNodeChildren)
            return [".",".."] + [x.getName() for x in currentNodeChildren] 
        except Exception as e:
            print(e)
            return [".",".."]

    def readlink(self, path):
        print("readlink "+path)

    def release(self, path, fh):
        print("release "+path)

    def releasedir(self, path, fh):
        print("releasedir "+path)

    def removexattr(self, path, name):
        print("removextattr "+path)

    def rename(self, old, new):
        print("rename "+old+" | "+new)
    def rmdir(self, path):
        print("rmdir "+path)
    def setxattr(self, path, name, value, options, position=0):
        print("setxattr "+path)

    def statfs(self, path):
        print("stats "+path)

    def symlink(self, target, source):
        print("symlink "+target+" | "+source)

    def truncate(self, path, length, fh=None):
        print("trunc "+path)

    def unlink(self, path):
        print("unlink "+path)

    def utimens(self, path, times=None):
        print("utimens "+path)

    def write(self, path, data, offset, fh):
        pass
"""import os
if __name__ == "__main__":
    fuse = FUSE(ScienceFs(), "/home/noreasonexception/Desktop/sciencefs/sciencefsPrototype/tst/mount", foreground=True,allow_other=True)
"""

