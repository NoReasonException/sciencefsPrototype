import os
class ParserToFsMediator:
    def __init__(self,filesystem,readCallback):
        self.__fs=filesystem
        self.__readCallBack=readCallback
    def getFs(self):            return self.__fs
    def getReadCallBack(self):    return self.__readCallBack
    def mkdir(self,path):
        os.mkdir(path)

