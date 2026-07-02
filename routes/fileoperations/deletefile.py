from flask import Blueprint,jsonify
from utils.Storage import get_storage
from utils.acceptjson import getjson
from utils.updatespace import updatespace
deletefilebp=Blueprint("delete",__name__)

Fileoperation=get_storage()
@deletefilebp.route("/deletefile/<int:userid>/",methods=["DELETE"])
@getjson
def Home(userid,data):
    userid=str(userid)
    filename=data.get("filename")   
    tosend=deletefile(userid=(userid),filename=filename)
    filesize=tosend[2]
    if tosend[0] ==0:
        return jsonify({"return":tosend[1]}),400
    updatespace(userid=userid,operation=-filesize)
    #The frontend should update the         
    return jsonify({"return":tosend[1]}),200
    
    
    
def deletefile(userid,filename):
    try:
        filesize=Fileoperation.Filesize(userid=userid,filepath=filename)
        Fileoperation.deletefile(userid=userid,filepath=filename)
        return [1,"file deleted",filesize]
    except FileNotFoundError as e:
        return [0,"Filenotfound",None]
    except FileExistsError as e:
        return [0,"filedonotexist",None]
    except PermissionError as e:
        return [0, "Something is wrong please try again ",None]

    except Exception as e:

        return [0, str(e),None]