from apirlpy import ratelimiter as RL
from flask import request,jsonify
from dotenv import load_dotenv
import os
load_dotenv()
path=os.getenv("ratelimiter")
def enableratelimiter(app):
    
    @app.before_request
    def enforcing():
        ip = request.remote_addr
        waittime=RL(IP_Adrs=ip,FolderPath=path)
        if waittime!=1:
            return jsonify({"return":f"too many requests!!, wait for {waittime}sec","waittime":int(waittime)}),429
        return
    return
        