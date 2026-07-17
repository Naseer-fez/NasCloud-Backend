from flask import Blueprint,jsonify,request
from utils.acceptjson import getjson
from utils.trashfile import recovertrash as recover_trash_fn
from utils.FolderStructure import updatefilestructure
recovertrash=Blueprint("recovertrash",__name__)


@recovertrash.route("/recovertrash/<int:userid>/",methods=["PUT"])
@getjson
def Home(userid,data):
    trashpath=data.get("trashpath") ## The real 
    tosend=recover_trash_fn(userid=str(userid),trashpath=trashpath)
    if tosend == 0 or (isinstance(tosend, list) and tosend[0] == 0):
            return jsonify({"return":"Error recovering the files"}),400
    updatefilestructure(Userid=userid)
    return jsonify({"return":"File transferred"}),200



