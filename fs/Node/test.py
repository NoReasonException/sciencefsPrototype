from Node import Node

x=Node.createDirectoryFile(None,None,"/",0o755)
z=Node.createDirectoryFile(None,None,"folderOfHello",0o755)
y=Node.createRegularFile(None,None,"hello",0o755)
n=Node.createRegularFile(None,None,"bla",0o755)

x.addChildren(z)
z.addChildren(y)
z.addChildren(n)
print(Node.pathToNodeTranslator(x,y.getFullPath()))
print(Node.pathToNodeTranslator(x,"/folderOfHello/bla").getFullPath()+"\tfound")
print(Node.pathToNodeTranslator(x,"/folderOfHello").getName())
print(x.toStandardDict())
