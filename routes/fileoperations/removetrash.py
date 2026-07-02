from flask import Blueprint,jsonify
from utils.Storage import get_storage
from utils.acceptjson import getjson
from utils.updatespace import updatespace
trashbp=Blueprint("trash",__name__)

Fileoperation=get_storage()
@trashbp.route("/trash/<int:userid>/",methods=["DELETE"]) #Frontend shoudl send trash /filename
@getjson
def Home(userid,data):
    userid=str(userid)
    filename=str(data.get("filepath"))
    Fileoperation.deletefile(userid=userid,filepath=filename)
    return jsonify({"return":"removedsuccesully from trash"})
