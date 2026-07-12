from flask import request,jsonify
from functools import wraps
def getjson(fun):
    @wraps(fun)
    def decorator(*args,**kwargs):
        data=request.get_json(silent=True)
        if not data:
            data=request.args.to_dict()
        if not data:
            return jsonify({
                "return": "Missing or invalid JSON payload."
            }), 400
        kwargs['data'] = data
        return fun(*args,**kwargs)
    return decorator