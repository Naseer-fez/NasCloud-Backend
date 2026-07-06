#Uploads cant be modulase by using the file class
from flask import jsonify,request,Blueprint
import os 
from dotenv import load_dotenv
from utils.FileHelpers import CreateDir
from pathlib import Path
from utils.updatespace import updatespace
from utils.FolderStructure import updatefilestructure
load_dotenv()
folderuploadbp=Blueprint('folderupload',__name__)


@folderuploadbp.route("/uploadfolder/<int:Userid>/",methods=["POST"]) 
def home(Userid):
    fileslist=request.files.getlist("files")
    if fileslist is None:
        return jsonify({"return":"No folder uploaded"}),400
    directory=request.form.get("directory")
    if directory is None:
        return  jsonify({"return":"No folder path mentioned"}),400
    Destiantion=os.getenv("DestinationFolder")
    directory=Path(os.path.join(Destiantion,str(Userid),directory))
    #first create the directory
    directory.mkdir(parents=True,exist_ok=True) #directory is created 
    #now stream the file
    CHUNK_SIZE=1024*1024*int(os.getenv("size",16))
    #now iterante over the files
    output="Folder upload done"
    statuscode=200
    try:

        for file in fileslist:
            fileanme=Path(file.filename).name
            filepath=directory/fileanme
            newpath=filecheck(filepath)
            if newpath !=0:
                filepath=newpath #meaning replcae the file
            with open(file=filepath,mode="wb") as f:
                while True:
                    chunk=file.stream.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    f.write(chunk)
    except Exception as e:
        output=e   
        statuscode=401
        
    return jsonify({"return":str(output)}),statuscode



def filecheck(tosavepath):
        prefix=1
        attempt=10000
        original_stem=tosavepath.stem
        suffix=tosavepath.suffix
        while attempt:
                if not tosavepath.exists():
                    return tosavepath
                tosavepath=tosavepath.with_name(f"{original_stem}[{prefix}]{suffix}")
                prefix+=1
                attempt-=1
        return 0  