import ngrok
from config import config
import requests as req
import os



def setapi():
    
    API = os.getenv("ngrokauth") 
    if not API:
        try:
            import winreg
            key_handle = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ)
            API, _ = winreg.QueryValueEx(key_handle, "ngrokauth")
            winreg.CloseKey(key_handle)
        except Exception:
            API = None

    if not API:
        API=config.get("ngrokauth")
        
    if not API:
        raise TypeError("Ngrok api key missing")
    ngrok.set_auth_token(API)

def startngrok():
    setapi()
    listener=ngrok.forward(
        config.get("port",5000),)
    return listener.url()





# URL= "http://127.0.0.1:5000"

def resetlink():
    URL=config.get("backend")
    if not URL:
        raise TypeError("The backend url is missing")
    LINK=startngrok()
    api=config.get("api_key")
    allow_users = "1" if config.get("allowusers", False) else "0"
    
    import urllib.parse
    params = {
        "api": api,
        "link": LINK,
        "users": allow_users
    }
    query_string = urllib.parse.urlencode(params)
    target_url = f"{URL.rstrip('/')}/register/api/?{query_string}"
    
    try: #notify the center server
        response=req.get(url=target_url)
        strc=response.status_code
        if strc==200:
            return LINK
    except Exception as e:
        raise TypeError("No link created")
        













