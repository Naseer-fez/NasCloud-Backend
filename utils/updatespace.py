from .Storage import get_storage
from dotenv import load_dotenv
import os
load_dotenv()
Fileoperation=get_storage()

def getsize(node):
    # File
    if node["type"] != "Folder":
        return node["size"]

    # Folder
    total = 0
    for child in node["children"]:
        total += getsize(child)
    return total

def spacecalculator(userid,operation=0):

    DIR=Fileoperation.jsonread(userid=userid)
    total = 0

    for root in DIR:
        total += getsize(root)

    return total+operation


def totalspaceused(userid):
    PATH=Fileoperation.getfilepath(userid=userid)
    PATH=PATH.parent/"stats.json"
    try:
        DIR = Fileoperation.jsonread(userid=userid,path=PATH)
        return DIR
    except (FileNotFoundError,TypeError) as e:
        space=spacecalculator(userid=userid)
        data={"usedspace":int(space),"remaningspace":int(availabelforuser(userid)-space)}
        jsonoperation(userid=userid,data=data,path=PATH)
        return data
    

def jsonoperation(userid,data,path=None):
        if path is None:
            path=Fileoperation.getfilepath(userid=userid)
            path=path.parent/"stats.json"        
        Fileoperation.jsonwrite(userid=userid,data=data,filepath=path)



def updatespace(userid,operation):
    currentspace=totalspaceused(userid)
    currentspace["usedspace"]=currentspace["usedspace"]+operation
    currentspace["remaningspace"]=currentspace["remaningspace"]-operation
    if currentspace["remaningspace"]>=0:
        jsonoperation(userid=userid,data=currentspace)
        return currentspace
    else: 
        return [0]
    


    
    

def availabelforuser(userid):
    GB=1073741824
    if userid:
        return int(os.getenv("basic","15"))*GB
    

        
        