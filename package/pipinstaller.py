import subprocess as CMD
import os
from pathlib import Path

try:
    from pckconfig import config
    from installdepen import PYTHON
    from packages import packages
except ImportError:
    from package.pckconfig import config
    from package.installdepen import PYTHON
    from package.packages import packages


DIR = config.get("workspace_path") or config.get("dir") or os.getcwd()
VENV_DIR = "env"


def _python_has_packages(py_path):
    if not py_path or not os.path.exists(py_path):
        return False
    try:
        res = CMD.run(
            [py_path, "-c", "import waitress, flask; print('ok')"],
            stdout=CMD.PIPE, stderr=CMD.PIPE, text=True, timeout=10,
            creationflags=CMD.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        return res.returncode == 0
    except Exception:
        return False


def pipcreation():
    try:
        _, path = PYTHON()
        if not path or not os.path.exists(path):
            return False, None

        # If Python already has required packages pre-installed, skip venv creation
        if _python_has_packages(path):
            config.set("venv_python", path)
            return True, path

        CMD.run(
            [path, "-m", "venv", VENV_DIR],
            check=True
        )

        venv_python = os.path.join(VENV_DIR, "Scripts", "python.exe")

        # Ensure pip is up to date in the venv
        CMD.run(
            [venv_python, "-m", "ensurepip", "--upgrade"],
            check=True
        )

        requirements_path = Path(os.getcwd()) / "requirements.txt"
        if requirements_path.exists():
            CMD.run(
                [venv_python, "-m", "pip", "install", "-r", str(requirements_path)],
                check=True
            )
        else:
            CMD.run(
                [venv_python, "-m", "pip", "install", *packages],
                check=True
            )

        config.set("venv_python", venv_python)
        return True, venv_python

    except CMD.CalledProcessError:
        return False, None


def PIP():
    venv_python = config.get("venv_python")

    if venv_python and Path(venv_python).exists() and _python_has_packages(venv_python):
        return venv_python

    _, py_path = PYTHON()
    if py_path and _python_has_packages(py_path):
        config.set("venv_python", py_path)
        return py_path

    success, venv_python = pipcreation()

    if success:
        return venv_python

    return None