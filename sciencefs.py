from collections import defaultdict
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit
from time import time
import inspect
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
from etc.Info import Info as info





class ScienceFs(LoggingMixIn, Operations):
    """===========================
        ScienceFs(SF) prototype
       ==========================
       
       :sectionauthor : Stefanos Stefanou , University of Reading , stefannstefanou@gmail.com
       :platform      : Linux 14.x , FreeBSD 11.x
       
       """
    def __init__(self):
        """
            Initialization 

            *members section*

                self.paths          : list() -> Keeps all the paths 
                self.pathsToInfo    : dict() -> Translates paths to Info structure (meta-data about file (just like inode))
                self.fd             : int()  -> counter of file desciptors
        """
        self.paths=list()
        self.pathsToInfo={}
        self.fd=12


    def chmod(self, path, mode):
        print("chmod "+path)


    def chown(self, path, uid, gid):
        print("chown "+path)

    def create(self, path, mode, fi=None):
        """
            Create new File

                1) Adds the path on the self.paths registy
                2) Creates and assigns to self.pathToInfo translator a Info structure , with all the needed meta-information about a file
                

        """
        self.paths.append(path)
	self.pathsToInfo[path]=info.createReg(path,0o755)
        print(".create() request on "+path)
        print(self.pathsToInfo[path].toStandardDict())

        

    def destroy(self, path):
        print("destroy "+path)

    def flush(self, path, fh):
        print("flush "+path)

    def fsync(self, path, datasync, fh):
        print("fsync "+path)

    def fsyncdir(self, path, datasync, fh):
        print("fsyncdir "+path)

    def getattr(self, path, fh=None):
        """"
            returns a dictionary of properties of a file
                st_mode -> or value combined of file type (S_IFREG(Regular file) or S_IFDIR(directory file))
                st_atime -> last access itme
                st_mtime -> last modification time
                st_ctime ->
                n_link   ->
                st_size  -> the size of the file

            you can return ENOENT and declare that this file is not exist , in this case the.create method will
            called , and after a .getattr will be attemted again with the new file created by .create()


        """
        print("getattr request  "+path)
        
        """
            If the len <2 , then the request is about home directory(/) so a S_IFDIR|0o755 is returned 
        """
        if len(path)<2:
            return dict(st_mode=(S_IFDIR | 0o755), st_atime=int(time()), st_mtime=int(time()), st_ctime=int(time()), st_nlink=2)
        """
            Check if the path already exists , if yes just return the standard dict() described in the docstring
        """
        if(path in self.paths):
            return (self.pathsToInfo[path].toStandardDict())
        else:
            """
                Declare that the file is not exists , force the vfs to call the .create() method
            """
            print("getattr :ENOENT on file " + path)
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
        print("mkdir "+path)

    def mknod(self, path, mode, dev):
        print("mknod "+path)

    def open(self, path, flags):
	 """
        Open a file and return a file descriptor , you can find the file descriptor in .read() and .write() operations
        on fh parameter (fh.fd)

	"""
        fd=(self.fd+1)
        self.fd+=1
        print("open "+path+" with fd="+str(fd))
        return fd

    def opendir(self, path):
        """
            Returns an numberical file handle for a directory , simillar to open() for regular files(S_IFREG inodes)

        :param path: The path
        :return: a number , file descriptor , always positive and over 3(stdin=1,stdout=2,stderr=3)
        """
        print("opendir "+path)
        return 0

    def read(self, path, size, offset, fh):
        print("read "+path)
        return self.pathsToInfo[path].rawData

    def readdir(self, path, fh):
        """
            Returns a list([]) with all files and directories available + . and .. (current and previous dir)
        :param path: the path of the dir asking the files

        WARNING , I STUCK 102810281 HOURS -> ALWAYS RETURN THE NAME OF THE FILES , WITH NO /
        AS THE FIRST CHARACTER , THE DOCUMENTATION IN COMPLETELY FUCKED

        :param fh: the
        :return:
        """

        print("readdir "+path)
        return [".",".."] + [ x[1:].encode('ascii','ignore') for x in self.paths]

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
        self.pathsToInfo[path].rawData=data
        self.pathsToInfo[path].st_size=len(data)
        print("write "+path+"data : "+data)
        return len(data)

if __name__ == "__main__":
    fuse = FUSE(ScienceFs(), "/home/noreasonexception/Desktop/sciencefs/sciencefsPrototype/mnt", foreground=True,allow_other=True)




