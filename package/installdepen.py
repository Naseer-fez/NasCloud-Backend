import urllib.request as DOWNLOAD
import os
import sys
import zipfile
from pathlib import Path
try:
    from pckconfig import config, PYTHON_EXE, NGROK_EXE, GITHUB_REPO
except ImportError:
    from package.pckconfig import config, PYTHON_EXE, NGROK_EXE, GITHUB_REPO

PYTHON_VERSION = "3.12.4"
DIR = config.get("dir") or os.path.join(os.getcwd(), GITHUB_REPO)

def find_executable(name):
    """Fast check for executable in system PATH without spawning subprocesses."""
    path_env = os.environ.get("PATH", "")
    for path in path_env.split(os.pathsep):
        candidate = os.path.join(path, name)
        if os.name == "nt" and not candidate.lower().endswith(".exe"):
            candidate += ".exe"
        if os.path.exists(candidate) and os.path.isfile(candidate):
            return os.path.normpath(candidate)
    return None

def checkpython():
    # 1. Instant check: use the currently running Python interpreter path
    #    Skip this when running as a PyInstaller .exe (sys.executable is the bundle)
    if not getattr(sys, 'frozen', False):
        if sys.executable and os.path.exists(sys.executable):
            return True, "python", os.path.normpath(sys.executable)
        
    # 2. PATH lookup
    for command in ("python", "py"):
        exe = find_executable(command)
        if exe:
            return True, command, exe

    return False, None, None

def checkngrok():
    # 1. Local path check
    local_ngrok = os.path.join(DIR, NGROK_EXE)
    if os.path.exists(local_ngrok):
        return True, "local_ngrok", os.path.normpath(local_ngrok)
        
    # 2. PATH lookup
    exe = find_executable("ngrok")
    if exe:
        return True, "ngrok", exe
        
    return False, None, None

def getarch():
    arch = os.environ.get("PROCESSOR_ARCHITEW6432")
    if arch:
        return arch.upper()
    return os.environ.get("PROCESSOR_ARCHITECTURE", "AMD64").upper()

def progress(block_num, block_size, total_size):
    if total_size <= 0:
        return
    downloaded = block_num * block_size
    percent = min(downloaded * 100 / total_size, 100)
    print(f"\rDownloading... {percent:.1f}%", end="")

def downloadpython():
    """Download Python installer. Returns the installer path for the user to run."""
    arch = getarch()
    if arch == "AMD64":
        URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-amd64.exe"
    elif arch == "x86":
        URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}.exe"
    elif arch == "ARM64":
        URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-arm64.exe"
    else:
        raise TypeError(
            f"""The user is recommended to install python manually.
            LINKS:
            64BIT->"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-amd64.exe"
            32BIT->"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}.exe"
            ARM64->"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-arm64.exe"
            """)
       
    Filename = os.path.join(DIR, "python-installer.exe")
    DOWNLOAD.urlretrieve(URL, Filename, reporthook=progress)
    return Filename

def downloadngrok():
    """Download and extract ngrok into the workspace directory."""
    arch = getarch()
    if arch == "AMD64":
        URL = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
    elif arch == "x86":
        URL = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-386.zip"
    elif arch == "ARM64":
        URL = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-arm64.zip"
    else:
        raise TypeError(
            """The user is recommended to install ngrok manually.
            LINKS:
            64BIT->"https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
            32BIT->"https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-386.zip"
            ARM64->"https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-arm64.zip"
            """
        )
    Filename = os.path.join(DIR, "ngrok-download.zip")
    os.makedirs(DIR, exist_ok=True)
    DOWNLOAD.urlretrieve(URL, Filename, reporthook=progress)
    with zipfile.ZipFile(Filename, 'r') as zip_ref:
        zip_ref.extractall(DIR)
    os.remove(Filename)

def PYTHON():
    """Returns [command, path] on success, [0, 0] on failure."""
    output, command, path = checkpython()
    if output:
        try:
            config.set("python", path)
        except Exception:
            pass
        return [command, path]
    else:
        return [0, 0]
    
def NGROK():
    """Returns [command, path] on success, [0, 0] on failure."""
    output, command, path = checkngrok()
    if output:
        try:
            config.set("ngrok", path)
        except Exception:
            pass
        return [command, path]
    else:
        return [0, 0]
