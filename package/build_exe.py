"""
NasCloud — Build Script (.exe)

Packages the entire Setup & Configuration wizard into a single
standalone .exe using PyInstaller.

Usage:
    python build_exe.py

Output:
    dist/NasCloudSetup.exe
"""
import subprocess
import sys
import os
import shutil


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENTRY_POINT = os.path.join(SCRIPT_DIR, "main.py")
EXE_NAME = "NasCloud"
DIST_DIR = os.path.join(SCRIPT_DIR, "dist")
BUILD_DIR = os.path.join(SCRIPT_DIR, "build")
SPEC_FILE = os.path.join(SCRIPT_DIR, f"{EXE_NAME}.spec")


def check_pyinstaller():
    """Check if PyInstaller is available, prompt to install if not."""
    try:
        import PyInstaller
        print(f"  PyInstaller {PyInstaller.__version__} found.")
        return True
    except ImportError:
        return False


def install_pyinstaller():
    """Install PyInstaller via pip."""
    print("  Installing PyInstaller...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "pyinstaller"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  ERROR: Failed to install PyInstaller:\n{result.stderr}")
        return False
    print("  PyInstaller installed successfully.")
    return True


def check_assets():
    """Verify assets directory and required bundled binaries/archives exist."""
    assets_dir = os.path.join(SCRIPT_DIR, "assets")
    if not os.path.exists(assets_dir):
        print(f"\n  ERROR: Assets directory not found at {assets_dir}")
        print("  Please create it and run 'python build_python_env.py' first.")
        return False

    required_assets = [
        ("python_env.zip", 1024 * 1024),          # At least 1MB
        ("cloudflared.exe", 1024 * 1024),         # At least 1MB
        ("backend_source.zip", 10 * 1024),        # At least 10KB
    ]

    missing = []
    for asset_name, min_size in required_assets:
        asset_path = os.path.join(assets_dir, asset_name)
        if not os.path.exists(asset_path):
            missing.append(f"Missing '{asset_name}' in {assets_dir}")
        elif os.path.getsize(asset_path) < min_size:
            missing.append(f"Invalid/incomplete '{asset_name}' in {assets_dir} (size: {os.path.getsize(asset_path)} bytes)")

    if missing:
        print("\n  ERROR: Asset verification failed:")
        for m in missing:
            print(f"    - {m}")
        print("\n  To build the required portable Python and backend archives, run:")
        print("    python build_python_env.py")
        print("  And ensure cloudflared.exe is placed in package/assets/.")
        return False

    print("  All required assets verified (python_env.zip, cloudflared.exe, backend_source.zip).")
    return True


def build():
    """Run the PyInstaller build."""
    print(f"\n{'='*50}")
    print(f"  Building {EXE_NAME}.exe")
    print(f"{'='*50}\n")

    # Step 1: Check PyInstaller
    print("[1/4] Checking for PyInstaller...")
    if not check_pyinstaller():
        print("  PyInstaller not found.")
        if not install_pyinstaller():
            sys.exit(1)

    # Step 2: Pre-flight check for assets
    print("[2/4] Verifying bundled assets...")
    if not check_assets():
        sys.exit(1)

    # Step 3: Clean previous build artifacts
    print("[3/4] Cleaning previous builds...")
    for path in (BUILD_DIR, DIST_DIR, SPEC_FILE):
        if os.path.exists(path):
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                print(f"  Removed: {path}")
            except Exception as e:
                print(f"  Warning: Could not remove {path}: {e}")

    # Step 4: Run PyInstaller
    print("[4/4] Running PyInstaller...")

    # Collect all the Python modules that main.py imports
    hidden_imports = [
        "pckconfig",
        "GUIsetup",
        "GUIconfig",
        "server_launcher",
        "installdepen",
        "packages",
        "pipinstaller",
        "controler",
        "urls",
        "url",
    ]

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                          # Single .exe output
        "--windowed",                         # No console window (GUI app)
        "--name", EXE_NAME,                   # Output name
        "--distpath", DIST_DIR,               # Output directory
        "--workpath", BUILD_DIR,              # Build temp directory
        "--specpath", SCRIPT_DIR,             # Spec file location
        "--icon", os.path.join(SCRIPT_DIR, "nascloud.ico"),
        "--add-data", f"{os.path.join(SCRIPT_DIR, 'nascloud.ico')};.",
        "--add-data", f"{os.path.join(SCRIPT_DIR, 'nascloud.png')};.",
        "--add-data", f"{os.path.join(SCRIPT_DIR, 'assets')};assets",
    ]

    # Add hidden imports
    for mod in hidden_imports:
        cmd.extend(["--hidden-import", mod])

    # Exclude heavy unnecessary modules and Pillow C-extensions (_avif alone is 7.5 MB)
    excluded_modules = [
        "numpy", "pandas", "scipy", "matplotlib", "IPython", "pytest", "docutils",
        "PIL._avif", "PIL._webp", "PIL._imagingcms", "PIL._imagingmath", "PIL._imagingmorph"
    ]
    for mod in excluded_modules:
        cmd.extend(["--exclude-module", mod])

    # Add the entry point
    cmd.append(ENTRY_POINT)

    print(f"  Command: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, cwd=SCRIPT_DIR)

    if result.returncode != 0:
        print(f"\n  BUILD FAILED (exit code {result.returncode})")
        sys.exit(result.returncode)

    # Verify output
    exe_path = os.path.join(DIST_DIR, f"{EXE_NAME}.exe")
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"\n{'='*50}")
        print(f"  BUILD SUCCESSFUL!")
        print(f"  Output: {exe_path}")
        print(f"  Size:   {size_mb:.1f} MB")
        print(f"{'='*50}")
        print(f"\n  The .exe will auto-create packageconfig.json")
        print(f"  next to itself on first launch.")
    else:
        print(f"\n  ERROR: Expected output not found at {exe_path}")
        sys.exit(1)


if __name__ == "__main__":
    build()
