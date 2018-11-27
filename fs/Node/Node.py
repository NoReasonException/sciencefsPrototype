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
    def create(fs,parent,name,links,mode,typeoffile):
        """create a plain Node object
        @param fs                   the object to filesystem
        @param paremt               the object to parent Node(None for root)
        @param name                 the name of the file(or directory)
        @param mode                 the permissions WITH NOT THE FILE TYPE (just the octal representing the permissions)
        @param typeoffile           the type of file (S_IFREG for file or S_IFDIR for directory)
        @return a brand-new Node Object
        """
        now=time()
        return Node(parent,name,now,now,now,links,fs,mode,typeoffile)
    @staticmethod
    def createRegularFile(fs,parent,name,mode):
        """
        a wrapper over .create() method providing the S_IFREG as @param typeoffile 
        @return a brand-new Node representing a file

        @Note
            When a Node object is created using .createRegularFile() , then the self.__data field is the actual data of that file

        """
        return Node.create(fs,parent,name,1,mode,S_IFREG)
    @staticmethod
    def createDirectoryFile(fs,parent,name,mode):
        """
        a wrapper over .create mehod providing the S_IFDIR as @param typeoffile 
        """
        return Node.create(fs,parent,name,2,mode,S_IFDIR)
    def __init__(self,parent,name,atime,mtime,ctime,nlink,fs,mode,typeoffile):
        """
            The constructor of Node Class

            @param parent       the parent of the current Node (always a file)
            @param name         the name of the Node (filename without '/'s or '\\'s, not the path! the filename!)
            @param atime        the atime (search for atime attribute somewhere dude)
            @param mtime        --//--//--//--//--//
            @param ctime        --//--//--//--//--//
            @param nlink        --//--//--//--//--//
            @param fs           the filesystem Object 
            @param mode         the permissions of the file WITHOUT the type (S_IFDIR/S_IFREG)
            @param typeoffile   the S_IFDIR/S_IFREG attribute

        """
        self.__parent=parent
        self.__name=name
        self.__size=0
        self.__atime=atime
        self.__mtime=mtime
        self.__ctime=ctime
        self.__nlink=nlink
        self.__fs=fs
        self.__mode=(0o755|typeoffile)
        self.__data=""
        """
            @Note!
                When this file is regular file , the self.data will be contain the data of that file
                When this file is directory file,the self.data will be contain the children of that directory
        """
        if(typeoffile==S_IFDIR):
            self.__data=list()
    @staticmethod
    def pathToNodeTranslator(rootNode,path):
        """
            .pathToNodeTranslator gets a rootNode and a path and tries to return the Node Object representing
            that particular file
            

            @param rootNode the node of the root
            @param path     the string providing a given path
            @returns a Node object if the path exists , or None otherwise

            @Note
            Why this is not recursive?
                because after ~65535 folder will crash , also thing the call overhead. a plain for (for the prototype only of course)
                will be fine~
        """
        
        if(rootNode.getName()==path):
            """
            If we ask the rootNode , just avoid everything and return the root
            """
            return rootNode

        nodeNames=path.split('/')                                               #We split the Path in '/'
        tmp=rootNode                                                            #temponary variable to interate
        for i in range(1,len(nodeNames)):                                       #iterate every element of path
            #childrenOfCurrentNode=map(lambda x:x.getName(),tmp.getData())       #we take every childs name in a list
            childrenOfCurrentNode=[x.getName() for x in tmp.getData()]
            print(type(childrenOfCurrentNode))
            if tmp.isDirectory() and nodeNames[i] in childrenOfCurrentNode:     #if our current path name exists in children list of the current folder
                print(nodeNames[i])
                tmp=tmp.getData()[childrenOfCurrentNode.index(nodeNames[i])]    #we point there and we continue from there
            elif tmp.isFile() and tmp.getName()==nodeNames[-1]:                 #if we have reached our target , just break
                break
            else:
                return None                                                     #Invalid url , we are in a dead-end
        return tmp                                                              #return the found node
        

                
            
    
    def getFullPath (self):
        """
            .getFullPath
            
            this method returns the full path representing the actual Node 
            
            @Todo -> make a utillity method to convert into standard path.

        """
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


    """
        This is a bunch of setters/getters

    """
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
    def setSize     (self,size):self.__size=size
    def getChildren (self):
        if self.isFile():
            raise Exception('Regular files cant have children')
        return tuple(self.getData()) #return as turple in order to be non-volatible
    def addChildren(self,child):
        if self.isFile():
            raise Exception('Regular files cant have children')
        self.__data.append(child)
        child.__parent=self
        return child



    def toStandardDict(self):
        """
            Converts the attributes of this node into a standard dict() , whitch we can return it 
            from a direct call on .getattr() in fusepy level

        """

        retval=     dict(st_mode=self.__mode,
                    st_atime=self.__atime,
                    st_mtime=self.__mtime,
                    st_ctime=self.__ctime,
                    st_size=self.__size,
                    st_nlink=self.__nlink)
        """if(self.isDirectory()):
            del retval['st_size']"""
        return retval
