from flask import Blueprint,jsonify
from utils.Storage import get_storage
from utils.acceptjson import getjson
from utils.FolderStructure import updatefilestructure
updatefilebp=Blueprint("update",__name__)

Fileoperation=get_storage()
@updatefilebp.route("/updatefile/<int:userid>/",methods=["PUT"])
@getjson
def Home(userid,data):

    filename=data.get("filename")
    newname=data.get("newname")
    tosend=updatefile(userid=str(userid),filename=filename,newname=newname)
    statuscode=200
    if tosend[0] ==0:
        statuscode=400
    updatefilestructure(userid,update=[filename,newname],operation="update")    
    return jsonify({"return":tosend[1]}),statuscode


def updatefile(userid,filename,newname):
    try:
        Fileoperation.rename(userid=userid,filepath=filename,tochange=newname)
        return [1,"file renamed"]
    except FileNotFoundError as e:
        return [0,"Filenotfound"]
    except FileExistsError as e:
        return [0,"filedonotexist"]
    except PermissionError as e:
        return [0,"permissiondenied"]
    except Exception as e:
        return [0,str(e)]
    
    