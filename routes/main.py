import subprocess
import os
import re
import requests as req
import time
from config import config

# We need to find cloudflared.exe. Let's check config, AppData, or PATH
def get_cloudflared_path():
    # 1. Config path
    cf_path = config.get("cloudflared")
    if cf_path and os.path.exists(cf_path):
        return cf_path
        
    # 2. AppData Local PersonalDrive bin check
    appdata_dir = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or os.path.expanduser("~")
    local_cf = os.path.normpath(os.path.join(appdata_dir, "PersonalDrive", "bin", "cloudflared.exe"))
    if os.path.exists(local_cf):
        return local_cf

    # 3. PATH lookup
    import shutil
    find_cf = shutil.which("cloudflared") or shutil.which("cloudflared.exe")
    if find_cf:
        return find_cf
        
    return None

def start_tunnel():
    """Start cloudflared tunnel and return public URL."""
    # Check if we already have a valid tunnel URL in environment or config
    url = os.getenv("TUNNEL_URL") or config.get("tunnel_url")
    if url:
        return url

    cf_path = get_cloudflared_path()
    if not cf_path:
        raise TypeError("cloudflared.exe is missing. Run server_launcher.py first.")

    port = config.get("port", 5000)
    try:
        # Spawn cloudflared tunnel
        process = subprocess.Popen(
            [cf_path, "tunnel", "--url", f"http://127.0.0.1:{port}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
    except Exception as e:
        raise TypeError(f"Failed to launch cloudflared tunnel: {e}")

    # Read output to capture the URL
    url_pattern = re.compile(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com')
    start_time = time.time()
    
    # Read output with a timeout of 15 seconds
    while time.time() - start_time < 15:
        line = process.stdout.readline()
        if not line:
            if process.poll() is not None:
                break
            time.sleep(0.1)
            continue
            
        match = url_pattern.search(line)
        if match:
            found_url = match.group(0)
            os.environ["TUNNEL_URL"] = found_url
            try:
                config.set("tunnel_url", found_url)
            except Exception:
                pass
            return found_url
            
    raise TypeError("Failed to extract Cloudflare tunnel URL from output.")

def resetlink():
    # Try to load CENTRAL_SERVER_URL from central server config constants or environment
    URL = config.get("CENTRAL_SERVER_URL") or os.getenv("CENTRAL_SERVER_URL") or "http://127.0.0.1:5000"
    if not URL:
        raise TypeError("The central server url is missing")
        
    LINK = start_tunnel()
    
    api = config.get("api_key")
    allow_users = 1 if config.get("allowusers", False) else 0
    
    data = {
        "api": api,
        "link": LINK,
        "users": allow_users
    }
    target_url = f"{URL.rstrip('/')}/register/api/"
    
    try:
        # Notify the central server via GET/POST matching existing protocol
        response = req.get(url=target_url, json=data, timeout=8)
        if response.status_code == 200:
            return LINK
    except Exception:
        try:
            response = req.post(url=target_url, json=data, timeout=8)
            if response.status_code == 200:
                config.set("link",LINK)
                return LINK
        except Exception:
            pass
            
    raise TypeError("No link created")

        













