from flask import Flask,jsonify,request,Blueprint
import os 
from dotenv import load_dotenv
from utils.FileHelpers import CreateDir
from pathlib import Path
from utils.acceptjson import getjson
load_dotenv()
uploadbp=Blueprint('FileUpload',__name__)


@uploadbp.route("/uploadfile/<int:Userid>",methods=["GET"]) 
@getjson
def home(Userid,data):
    directory=data.get("directory")
    Stream=request.environ["wsgi.input"]
    Filename=os.getenv("DestinationFolder")
    Recivedfile=str(request.files['filename'].filename)
    Tosave=CreateDir(Userid=Userid,Directory=directory,Filename=Recivedfile)
    if  Tosave==0:
        return jsonify({"return":"Some Error in Creating the Directory"}),401
    with open (file=Path(Tosave),mode="ab") as File:
        while True:
            Chunk=request.stream.read((1024*1024)*int(os.getenv("size"), 16)) #16MB
            if not Chunk :
                break
            File.write(Chunk)
    # with open() as File:
    return jsonify({"return":"File Saved in the server"}),200