from flask import Flask,request,jsonify
import os 
from dotenv import load_dotenv
from utils.FileHelpers import CreateDir

load_dotenv()
app = Flask(__name__)

@app.route("/<int:Userid>",defaults={"directory":None},methods=["GET","POST"]) 
@app.route("/<int:Userid>/<string:directory>",methods=["GET","POST"]) 
def home(Userid,directory):
    Stream=request.environ["wsgi.input"]
    Filename=os.getenv("DestinationFolder")
    Recivedfile=request.files['filename'].filename
    PATH=CreateDir(Userid,directory,Filename)
    if  PATH==0:
        return jsonify({"return":"Some Error in Creating the Directory"}),401
    with open (PATH,"ab") as File:
        while True:
            Chunk=request.stream.read((1024)*16) #16MB
            if not Chunk :
                break
            File.write(Chunk)
    # with open() as File:
    return jsonify({"return":"File Saved in the server"}),200
if __name__ == "__main__":
    app.run(debug=True)
