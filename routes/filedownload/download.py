from flask  import Blueprint,jsonify,Response
# from flask import Flask,jsonify,Response
# # from .sendfile import Filedownload
# from sendfile import Filedowload
import os 
from dotenv import load_dotenv
from pathlib import Path
from utils.Storage import get_storage
from utils.acceptjson import getjson

downloadbp=Blueprint('Downloadbp',__name__)
# downloadbp=Flask(__name__)
Fileoperation=get_storage()

# @downloadbp.route("/downloadfile/<int:userid>/",defaults={"folderpath":None,"filepath":None,},methods=["GET"])
@downloadbp.route("/downloadfile/<int:userid>/",methods=["GET"]) 
@getjson
def Home(userid,data):
    userid=str(userid)
    filepath=data.get("filename")
    filepath,filesize,filetype=filedetails((userid),filepath)
    if filepath is None:
        return jsonify({"retutn":"WrongFile Inputed Tryagain"}),400
    headerdata={"filesize":filesize,"filetype":filetype}
    SIZE=os.getenv("size") or 5
    return Response(Fileoperation.readdata(filename=filepath,Sizeofdata=SIZE),
                    mimetype=filetype,headers=headerdata)
    
    
    

def filedetails(userid,filepath):
    Source=Fileoperation.source 
    orginalfile=filepath
    filepath=Fileoperation.joinpath(Source,[str(userid),filepath])
    if Fileoperation.isdirectory(filepath):
        return [None]*3
    try:
        Filesize=Fileoperation.Filesize(userid=userid,filepath=orginalfile)
    except FileNotFoundError as e:
        return [None]*3
    Fileextenstion=Fileoperation.getextenstion(filepath=filepath)
    return [filepath,Filesize,Fileextenstion]




    
    

if __name__=="__main__":
    downloadbp.run(debug=True)
