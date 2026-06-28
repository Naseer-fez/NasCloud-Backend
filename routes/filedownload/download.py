from flask  import Blueprint,jsonify,Response
# from flask import Flask,jsonify,Response
# # from .sendfile import Filedownload
# from sendfile import Filedowload
import os 
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
downloadbp=Blueprint('Downloadbp',__name__)
# downloadbp=Flask(__name__)


# @downloadbp.route("/downloadfile/<int:userid>/",defaults={"folderpath":None,"filepath":None,},methods=["GET"])
@downloadbp.route("/downloadfile/<int:userid>/<string:filepath>",methods=["GET"]) 
def Home(userid,filepath):
    filepath,filesize,filetype=filedetails(str(userid),filepath)
    if filepath is None:
        return jsonify({"retutn":"WrongFile Inputed Tryahain"}),429
    headerdata={"filesize":filesize,"filetype":filetype}
    value=Filedownload(filepath)
    return Response(value,mimetype=filetype,headers=headerdata)
    
    
    

def filedetails(userid,filepath):
    Source=os.getenv("DestinationFolder") or r"D:/CODE/PYTHON/CODE/Projects/Personaldrive/test"
    filepath=Path(os.path.join(Source,userid,filepath))
    if not os.path.exists(filepath):
        return [None]
    Filesize=os.path.getsize(filepath)
    Fileextenstion=os.path.splitext(filepath)[1]
    return [filepath,Filesize,Fileextenstion]


def Filedownload(filepath):
        SIZE=int(os.getenv("size")) or 5
        with open (file=filepath,mode="rb") as output:
            while True:
              chunk=output.read(1024*1024*SIZE)
              if not chunk:
                  break
              yield chunk  


    
    

if __name__=="__main__":
    downloadbp.run(debug=True)
