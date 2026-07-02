from flask import Blueprint,jsonify
from utils.Storage import get_storage
from utils.updatespace import totalspaceused
spacebp=Blueprint("spacebp",__name__)

Fileoperation=get_storage()
@spacebp.route("/userstats/<int:userid>/",methods=["GET"])
def Home(userid):
    usedspace=getuserusage(userid)
    if usedspace==-1:
        return jsonify({"return":"The user do not exist"}),400
    return jsonify({"return":(usedspace)}),200
    


def getuserusage(userid):
    PATH=Fileoperation.getfilepath(userid=userid)
    PATH=(PATH.parent/"stats.json")
    if not Fileoperation.pathexist(PATH):
        return totalspaceused(userid)
    else:
        Data=Fileoperation.jsonread(userid=userid,path=PATH)
        return Data

        
    #check if the file exist or not 



    
    


# def getspace():