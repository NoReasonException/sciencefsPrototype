from Node import Node

x=Node.createDirectoryFile(None,None,"/",0o755)
z=Node.createDirectoryFile(None,None,"folderOfHello",0o755)
y=Node.createRegularFile(None,None,"hello",0o755)

#y.getName()
x.addChildren(z)
z.addChildren(y)
#y.getParent().getName()
#y.getName()
print(y.getFullPath())
print("end")
