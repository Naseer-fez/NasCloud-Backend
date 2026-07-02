from flask import Flask,jsonify,request,Blueprint
import os 
from dotenv import load_dotenv
from utils.FileHelpers import CreateDir
from pathlib import Path
from utils.acceptjson import getjson
from utils.updatespace import updatespace
load_dotenv()
uploadbp=Blueprint('FileUpload',__name__)


@uploadbp.route("/uploadfile/<int:Userid>",methods=["POST"]) 
def home(Userid):
    directory=request.form.get("directory")
    print(directory)
    Stream=request.environ["wsgi.input"]
    Filename=os.getenv("DestinationFolder")
    if 'filepath' not in request.files:
        return jsonify({"return": "No file provided"}), 400
    Recivedfile=str(request.files['filepath'].filename)
    uploadsize = request.content_length
    if  not updatespace(Userid,+uploadsize):
        return jsonify({"return":"No space left"}),400
    Tosave=CreateDir(Userid=Userid,Directory=directory,Filename=Recivedfile)
    filesize=0
    if  Tosave==0:
        print("HEHEHEHEH")
        return jsonify({"return":"Some Error in Creating the Directory"}),401
    uploaded_file = request.files["filepath"]
    with open (file=Path(Tosave),mode="ab") as File:

        while True:
            Chunk=uploaded_file.stream.read((1024*1024)*int(os.getenv("size"), 16)) #16MB
            if not Chunk :
                break
            File.write(Chunk)
            filesize += len(Chunk)
    updatespace(userid=Userid,operation=uploadsize)
    # with open() as File:
    return jsonify({"return":"File Saved in the server"}),200

