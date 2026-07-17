from flask import Blueprint,jsonify
from utils.FolderStructure import Createfilestructure
from utils.FileHelpers import checkchangesinstats
from utils.Storage import get_storage
structurebp=Blueprint("structure",__name__)

File=get_storage()

@structurebp.route("/structure/<int:userid>/",defaults={"folder":-1},methods=["GET"])
@structurebp.route("/structure/<int:userid>/<int:folder>",methods=["GET"])
def Home(userid,folder):
    userid=str(userid)
    structure=paging(userid,folderno=folder)
    if structure[0]==0:
        return jsonify({"return":"No folders left ","instruction":"create a file before getting the structure"}),400  
    if  structure[0]==-1:
        return jsonify({"return":"file opening error","instruction":"try again"}),400
    return jsonify(structure[1]),200
    

@structurebp.route("/folders/<int:userid>/",methods=["GET"])
def totalfolders(userid):
    userid=str(userid)
    lenoffolders=paging(userid,ask=1)
    if lenoffolders[0]==0:
        return jsonify({"return":"No folders left ","instruction":"create a file before getting the structure"}),400  
    if  lenoffolders[0]==-1:
        return jsonify({"return":"file opening error","instruction":"try again"}),400
    return jsonify({"return":lenoffolders[1]}),200
    



def paging(userid,folderno=None,ask=0):
    data=checkchangesinstats(userid)
    if  data==0:
        Createfilestructure(userid)
    try:
        filedata=File.jsonread(userid=(userid))
    except Exception as e:
        return [-1]
    if ask:
        toreturn=len(filedata)
        if toreturn==0:
            return [0]  
        return [1,toreturn-1]  
    
    if folderno==-1:
        return [1,filedata]
    lenofpages=len(filedata)
    if lenofpages <= folderno: ##means no more folders left
        return [0]
    return [1,filedata[folderno]]