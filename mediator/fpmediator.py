import os
class ParserToFsMediator:
    def __init__(self,filesystem,readCallback):
        self.__fs=filesystem
        self.__readCallBack=readCallback
    def mkdir(self,path):
        os.mkdir(path)

