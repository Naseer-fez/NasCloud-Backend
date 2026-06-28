from flask import Flask,request,jsonify
import os 
from dotenv import load_dotenv
from utils.FileHelpers import CreateDir
from pathlib import Path

#ImportBlueprints
from routes.fileupload.recive import uploadbp


load_dotenv()
def Createapp():
    app = Flask(__name__)

    #Register Blueprints
    app.register_blueprint(uploadbp)
    return app


app=Createapp()




if __name__ == "__main__":
    app.run(debug=True)
