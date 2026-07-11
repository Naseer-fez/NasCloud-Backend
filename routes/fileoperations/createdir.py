from flask import Blueprint,jsonify
from utils.Storage import get_storage
from utils.acceptjson import getjson
from utils.FolderStructure import updatefilestructure
createbp=Blueprint("create",__name__)

Fileoperation=get_storage()
@createbp.route("/createfolder/<int:userid>/",methods=["PUT"])
@getjson
def Home(userid,data):
    filename=data.get("filename")
    tosend=createdir(userid=str(userid),foldername=filename)
    statuscode=200
    if tosend[0] ==0:
        statuscode=400
    updatefilestructure(userid)
    return jsonify({"return":tosend[1]}),statuscode
    



def createdir(userid,foldername):
    try:
        Fileoperation.Createfolder(userid=userid,filepath=foldername)
        return [1,"file renamed"]
    except PermissionError as e:
        return [0,"permissiondenied"]
    except Exception as e:
        return [0,str(e)]