from flask import Flask,request,jsonify
import os 
from dotenv import load_dotenv
from utils.FileHelpers import CreateDir
from pathlib import Path
from flask_cors import CORS
#ImportBlueprints
from routes.fileupload.recive import uploadbp
from routes.filedownload.download import downloadbp
from routes.filestructure.structure import structurebp
#File operations
from routes.filedeletion.deletefile import deletefilebp
from routes.fileoperations.updatefile import updatefilebp
from routes.fileoperations.createdir import createbp
from routes.fileoperations.postionchnage import postionbp
from routes.filestats.spaceleft import spacebp
from routes.filesearch.searchfile import filesearch 
from routes.fileoperations.removetrash import trashbp
from routes.publicacces.accesspublic import publicbp
from routes.publicacces.setpublic import setpublicbp
from utils.auth import enableauth
import secrets
load_dotenv()
def Createapp():
    app = Flask(__name__)
    app.config["secret"] = os.getenv("secret")
    CORS(app=app)    
    enableauth(app)
    #Register Blueprints
    routes=[uploadbp,downloadbp,structurebp,deletefilebp,
            updatefilebp,createbp,postionbp,spacebp,filesearch,trashbp,
            setpublicbp,publicbp]
    for blueprint in routes:
        app.register_blueprint(blueprint)
    

    return app
app=Createapp()



if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)

