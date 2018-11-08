class Dentry:


    @staticmethod
    def createRootDentry(name,children):
        return Dentry(None,name,children)
    @staticmethod
    def createDirectoryDentry(parent,name,children):
        return Dentry(parent,name,children)
    @staticmethod
    def createRegularDentry(parent,name):
        return Dentry(parent,name,None)
    def __init__(self,parent,name,children):
        self.__name=name
        self.__parent=parent
        self.__children=children
    
    def getParent   (self):return self.__parent
    def getName     (self):return self.__name
    def getChildren (self):return self.__children
    def isRoot      (self):return self.__parent==None
    def isRegular   (self):return self.getChildren()==None
    def isDirectory (self):return not self.isRegular()

