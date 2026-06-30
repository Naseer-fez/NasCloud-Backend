from flask import Blueprint,jsonify
from utils.Storage import get_storage
from utils.acceptjson import getjson
from utils.updatespace import updatespace
deletefilebp=Blueprint("delete",__name__)

Fileoperation=get_storage()
@deletefilebp.route("/deletefile/<int:userid>/",methods=["DELETE"])
@getjson
def Home(userid,data):
    filename=data.get("filename")
    filesize=Fileoperation.Filesize(userid=userid,filepath=filename)
    tosend=deletefile(userid=str(userid),filename=filename)
    statuscode=200
    if tosend[0] ==0:
        statuscode=400
    updatespace(userid=userid,operation=-filesize)
    #The frontend should update the         
    return jsonify({"return":tosend[1]}),statuscode
    
    
    
def deletefile(userid,filename):
    try:
        
        Fileoperation.deletefile(userid=userid,filepath=filename)
        return [1,"file deleted"]
    except FileNotFoundError as e:
        return [0,"Filenotfound"]
    except FileExistsError as e:
        return [0,"filedonotexist"]
    # except Exception as e:

    #     return [0, str(e)]