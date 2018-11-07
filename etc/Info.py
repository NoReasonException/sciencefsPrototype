from time import time
from stat import S_IFDIR,S_IFREG

class Info:

    @staticmethod
    def create(path,filetype, accessOctal):
        now = int(time())
        return Info(path,  # path to file
                    S_IFREG | accessOctal,  # Mode(example 0o755)
                    now,  # atime now()
                    now,  # mtime now()
                    now,  # ctime now()
                    1)  # links 1
    @staticmethod
    def createDir(path,accessOctal):
        return Info.create(path,S_IFDIR,accessOctal)
    @staticmethod
    def createReg(path,accessOctal):
        return Info.create(path,S_IFREG,accessOctal)
    


    def __init__(self, path, mode, atime, mtime, ctime, links):
        self.rawData=0
        self.mode = mode
        self.atime = atime
        self.mtime = mtime
        self.ctime = ctime
        self.links = links
        self.path = path
        self.st_size=0

    def toStandardDict(self):
        return dict(st_mode=self.mode,
                    st_atime=self.atime,
                    st_mtime=self.mtime,
                    st_ctime=self.ctime,
                    st_size=self.st_size,
                    st_nlink=2)
