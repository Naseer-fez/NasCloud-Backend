from utils.Storage import get_storage
from utils.FolderStructure import Createfilestructure
from utils.updatespace import jsonoperation,checkchanges
Fileoperation=get_storage()

def searchfile(userid,tofind):
    #check if the cache exist 
    filepath=Fileoperation.getfilesjson(userid) #create a substitute of this
    checkchanges(userid=userid) #Because i need accurate files so , the createfolder will do that for me 
    try:
        filedata=Fileoperation.jsonread(userid=userid,path=filepath) #meaning reading the cache file path
    except FileNotFoundError as e:
        filedata=createfilescache(userid,filepath)
        if filedata==-1:
            return [-1,"User not found"]
        jsonoperation(userid=userid,data=filedata,path=filepath)
    except Exception as e:
        return [-1,str(e)]
    filedata=filelookup(filename=tofind,source=filedata)
    return filedata[0],filedata[1]
    
def createfilescache(userid,path):


    #First verify that the user is available
    result,filepath=(Fileoperation.userexist(str(userid)))
    if not  result:
        return -1
    Createfilestructure(userid=userid)
    return Fileoperation.jsonread(userid=userid,path=path)
    #Now start searching for the user

def filelookup(filename,source):
    #time to search
    if filename  in source:
        return [1,source[filename]]
    else:
        return [-1,"No file found"]
    



if __name__=="__main__":
    print()
    
    
    
    

    