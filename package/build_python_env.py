"""
Build Script for Pre-bundled Portable Python Environment (python_env.zip)
and Backend Source Bundle (backend_source.zip)

Downloads embeddable Python 3.12.4 (matching system architecture), enables import site, installs pip,
installs all required dependencies into Lib/site-packages, cleans up temporary build files,
and bundles the result into assets/python_env.zip and assets/backend_source.zip.
"""

import os
import sys
import shutil
import zipfile
import urllib.request
import subprocess
import platform
from pathlib import Path

# Paths configuration
SCRIPT_DIR = Path(__file__).parent.resolve()
ASSETS_DIR = SCRIPT_DIR / "assets"
OUTPUT_ZIP = ASSETS_DIR / "python_env.zip"
WORK_DIR = SCRIPT_DIR / "temp_py_build"

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


def get_python_zip_url():
    """Detect platform architecture and return matching Python embeddable zip URL."""
    machine = platform.machine().lower()
    if "arm64" in machine or "aarch64" in machine:
        return "https://www.python.org/ftp/python/3.12.4/python-3.12.4-embed-arm64.zip"
    elif "32" in machine or "x86" in machine or "i386" in machine or "i686" in machine:
        if "64" not in machine:
            return "https://www.python.org/ftp/python/3.12.4/python-3.12.4-embed-win32.zip"
    return "https://www.python.org/ftp/python/3.12.4/python-3.12.4-embed-amd64.zip"


def create_backend_source_zip():
    """Package backend source repository into assets/backend_source.zip."""
    backend_root = SCRIPT_DIR.parent
    backend_zip_path = ASSETS_DIR / "backend_source.zip"
    print(f"\n[Extra] Packaging backend source repository into {backend_zip_path.name}...")
    
    if backend_zip_path.exists():
        backend_zip_path.unlink()

    exclude_dirs = {
        ".git", ".github", ".vscode", "__pycache__", "temp_py_build",
        "build", "dist", "assets", "env", "venv", "Data", "test", "userdetails"
    }
    exclude_extensions = {".pyc", ".pyo", ".pyd", ".spec", ".zip", ".exe", ".log"}

    arc_prefix = "NasCloud-Backend-main"

    with zipfile.ZipFile(backend_zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(backend_root):
            # Prune excluded directories in-place
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            rel_root = Path(root).relative_to(backend_root)
            if any(part in exclude_dirs for part in rel_root.parts):
                continue
                
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in exclude_extensions:
                    continue
                if file_path.name.startswith(".") and file_path.name not in (".env", ".gitignore", "sample.env"):
                    continue
                
                rel_file = file_path.relative_to(backend_root)
                arc_name = f"{arc_prefix}/{rel_file.as_posix()}"
                zf.write(file_path, arc_name)

    size_mb = backend_zip_path.stat().st_size / (1024 * 1024)
    print(f" SUCCESS: Created backend_source.zip ({size_mb:.2f} MB)")


def main():
    print("=" * 60)
    print("Building Portable Python Environment with Pre-installed Dependencies")
    print("=" * 60)

    # 1. Clean previous work dir
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR, ignore_errors=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    py_zip_url = get_python_zip_url()
    py_zip_path = WORK_DIR / "python_embed.zip"
    get_pip_path = WORK_DIR / "get-pip.py"

    # 2. Download embeddable Python
    print(f"\n[1/6] Downloading Python embeddable package from {py_zip_url}...")
    urllib.request.urlretrieve(py_zip_url, py_zip_path)

    # 3. Extract embeddable Python
    print("[2/6] Extracting embeddable Python package...")
    with zipfile.ZipFile(py_zip_path, 'r') as zf:
        zf.extractall(WORK_DIR)
    py_zip_path.unlink()

    # 4. Patch ._pth file to enable site-packages with exact line matching
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
            new_lines.append("import site")
        elif stripped:
            new_lines.append(stripped)

    for req in ("Lib", "Lib/site-packages", "."):
        if req not in new_lines:
            new_lines.insert(0, req)

    if "import site" not in new_lines:
        new_lines.append("import site")

    with open(pth_file, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines) + "\n")

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

    # Verify site-packages has installed packages
    if not site_packages.exists() or not any(site_packages.iterdir()):
        raise RuntimeError("Lib/site-packages is missing or empty after pip install!")
    if not (site_packages / "flask").exists() and not list(site_packages.glob("flask*")):
        raise RuntimeError("Flask package was not found in Lib/site-packages after installation!")

    # Test installation
    print("Testing package imports in target environment...")
    verify_cmd = [str(py_exe), "-c", "import flask, waitress, sqlalchemy, requests, rapidfuzz; print('Verification Successful!')"]
    res = subprocess.run(verify_cmd, cwd=WORK_DIR, capture_output=True, text=True)
    print("Verification result:", res.stdout.strip() if res.returncode == 0 else res.stderr.strip())
    if res.returncode != 0:
        raise RuntimeError("Verification of installed packages failed!")

    # 6. Cleanup installer scripts and create python_env.zip
    print("[6/6] Creating python_env.zip...")
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

    # 7. Create backend source archive
    create_backend_source_zip()


if __name__ == "__main__":
    main()
