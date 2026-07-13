import subprocess as CMD
import os
import sys

try:
    from pckconfig import config, DEFAULT_HOST, DEFAULT_PORT, DEFAULT_THREADS
    from installdepen import PYTHON, NGROK
    from pipinstaller import PIP
except ImportError:
    from package.pckconfig import config, DEFAULT_HOST, DEFAULT_PORT, DEFAULT_THREADS
    from package.installdepen import PYTHON, NGROK
    from package.pipinstaller import PIP


def getvariables():
    try:
        pycommand, py = PYTHON()
    except TypeError as e:
        return str(e)
    try:
        ngrokcommand, ngrok = NGROK()
    except TypeError as e:
        return str(e)
    pippath = PIP()
    if pippath is None:
        return "Pip not found"
    return [py, ngrok, pippath]


def starttheserver():
    lst = getvariables()
    if isinstance(lst, str):
        raise TypeError(lst)
    pypath, ngrokpath, pippath = lst

    # Change to the workspace directory before starting
    workspace = config.get("dir")
    if workspace and os.path.isdir(workspace):
        os.chdir(workspace)

    host = config.get("host", DEFAULT_HOST)
    port = config.get("port", DEFAULT_PORT)
    threads = config.get("threads", DEFAULT_THREADS)

    result = CMD.Popen(
        [pippath, "-m", "waitress",
         f"--host={host}",
         f"--port={port}",
         f"--threads={threads}",
         "app:app"]
    )


if __name__ == "__main__":
    starttheserver()