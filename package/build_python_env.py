"""
Build Script for Pre-bundled Portable Python Environment (python_env.zip)

Downloads embeddable Python 3.12.4, enables import site, installs pip,
installs all required dependencies into Lib/site-packages, cleans up temporary build files,
and bundles the result into assets/python_env.zip.
"""

import os
import sys
import shutil
import zipfile
import urllib.request
import subprocess
from pathlib import Path

# Paths configuration
SCRIPT_DIR = Path(__file__).parent.resolve()
ASSETS_DIR = SCRIPT_DIR / "assets"
OUTPUT_ZIP = ASSETS_DIR / "python_env.zip"
WORK_DIR = SCRIPT_DIR / "temp_py_build"

PYTHON_ZIP_URL = "https://www.python.org/ftp/python/3.12.4/python-3.12.4-embed-amd64.zip"
GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"

PACKAGES = [
    "flask",
    "flask-cors",
    "flask-jwt-extended",
    "flask_sqlalchemy",
    "sqlalchemy",
    "python-dotenv",
    "gunicorn",
    "waitress",
    "requests",
    "pymysql",
    "apirlpy",
    "rapidfuzz",
    "stream-zip",
]

def main():
    print("=" * 60)
    print("Building Portable Python Environment with Pre-installed Dependencies")
    print("=" * 60)

    # 1. Clean previous work dir
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR, ignore_errors=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    py_zip_path = WORK_DIR / "python_embed.zip"
    get_pip_path = WORK_DIR / "get-pip.py"

    # 2. Download embeddable Python
    print(f"\n[1/6] Downloading Python embeddable package from {PYTHON_ZIP_URL}...")
    urllib.request.urlretrieve(PYTHON_ZIP_URL, py_zip_path)

    # 3. Extract embeddable Python
    print("[2/6] Extracting embeddable Python package...")
    with zipfile.ZipFile(py_zip_path, 'r') as zf:
        zf.extractall(WORK_DIR)
    py_zip_path.unlink()

    # 4. Patch ._pth file to enable site-packages
    print("[3/6] Configuring import site & site-packages in ._pth file...")
    pth_files = list(WORK_DIR.glob("*._pth"))
    if not pth_files:
        raise RuntimeError("Could not find ._pth file in extracted embeddable Python!")
    pth_file = pth_files[0]

    with open(pth_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped in ("#import site", "# import site"):
            new_lines.append("import site\n")
        else:
            new_lines.append(line if line.endswith("\n") else line + "\n")

    for req in ("Lib", "Lib/site-packages", "."):
        if not any(req in l for l in new_lines):
            new_lines.insert(0, req + "\n")

    if not any("import site" in l for l in new_lines):
        new_lines.append("import site\n")

    with open(pth_file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    # Ensure Lib/site-packages directory exists
    site_packages = WORK_DIR / "Lib" / "site-packages"
    site_packages.mkdir(parents=True, exist_ok=True)

    # 5. Bootstrap pip and install packages
    print(f"[4/6] Downloading get-pip.py from {GET_PIP_URL}...")
    urllib.request.urlretrieve(GET_PIP_URL, get_pip_path)

    py_exe = WORK_DIR / "python.exe"
    print("[5/6] Installing pip into embeddable Python...")
    res = subprocess.run([str(py_exe), str(get_pip_path), "--no-warn-script-location"], cwd=WORK_DIR)
    if res.returncode != 0:
        raise RuntimeError("Failed to run get-pip.py")
    get_pip_path.unlink()

    print(f"Installing target packages into embeddable environment: {', '.join(PACKAGES)}")
    install_cmd = [str(py_exe), "-m", "pip", "install", "--no-cache-dir", "--no-warn-script-location"] + PACKAGES
    res = subprocess.run(install_cmd, cwd=WORK_DIR)
    if res.returncode != 0:
        raise RuntimeError("Failed to install packages into embeddable environment!")

    # Test installation
    print("Testing package imports in target environment...")
    verify_cmd = [str(py_exe), "-c", "import flask, waitress, sqlalchemy, requests, rapidfuzz; print('Verification Successful!')"]
    res = subprocess.run(verify_cmd, cwd=WORK_DIR, capture_output=True, text=True)
    print("Verification result:", res.stdout.strip() if res.returncode == 0 else res.stderr.strip())
    if res.returncode != 0:
        raise RuntimeError("Verification of installed packages failed!")

    # 6. Cleanup pip and build cache before packaging to save space
    print("[6/6] Cleaning up installer scripts and creating python_env.zip...")
    # Optional: Uninstall pip/setuptools to save size, or leave pip in case it's needed
    # Packaging into assets/python_env.zip
    if OUTPUT_ZIP.exists():
        OUTPUT_ZIP.unlink()

    with zipfile.ZipFile(OUTPUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(WORK_DIR):
            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(WORK_DIR)
                zf.write(file_path, rel_path)

    zip_size_mb = OUTPUT_ZIP.stat().st_size / (1024 * 1024)
    print(f"\n============================================================")
    print(f" SUCCESS: Created pre-bundled python_env.zip ({zip_size_mb:.2f} MB)")
    print(f" Output Location: {OUTPUT_ZIP}")
    print(f"============================================================")

    # Cleanup temp directory
    shutil.rmtree(WORK_DIR, ignore_errors=True)

if __name__ == "__main__":
    main()
