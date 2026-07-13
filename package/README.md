# PersonalDrive Setup & Server Launcher Package

This directory contains the installation, configuration, and monitoring wizard for PersonalDrive, as well as the build scripts to package them into standalone Windows executables.

---

## Package Structure

*   `main.py` - Seamlessly chains the Setup Wizard and Server Configuration into a single process.
*   `server_launcher.py` - GUI server manager that checks environments, starts Waitress with custom thread configurations, runs Ngrok, and displays logs.
*   `pckconfig.py` - Branding constants hub and JSON configuration loader/writer.
*   `installdepen.py` - Handles Python/Ngrok checks and download urls.
*   `build_exe.py` - PyInstaller builder for the Setup wizard (`PersonalDriveSetup.exe`).
*   `build_server_exe.py` - PyInstaller builder for the Server launcher (`PersonalDriveServer.exe`).
*   `controler.py` & `pipinstaller.py` - Server-side process launcher and virtual environment builder.

---

## 1. How to Run in Development Mode

If you have Python installed and want to run or test the scripts directly:

### Run the Integrated Setup flow:
```powershell
python package/main.py
```
*This will launch Step 1 (Workspace Selection), Step 2 (Ngrok Authtoken), Step 3 (GitHub Server Downloader), followed immediately by the Server Configuration screen.*

### Run the Server Launcher directly:
```powershell
python package/server_launcher.py
```
*This starts the GUI process manager to launch Waitress and Ngrok based on paths in `packageconfig.json`.*

---

## 2. How to Build Standalone Executables (.exe)

You can compile standalone binaries that run on Windows without needing Python installed on the target machine:

### Build the Setup Wizard (`PersonalDriveSetup.exe`):
```powershell
python package/build_exe.py
```
*Output: `package/dist/PersonalDriveSetup.exe`*

### Build the Server Launcher (`PersonalDriveServer.exe`):
```powershell
python package/build_server_exe.py
```
*Output: `package/dist/PersonalDriveServer.exe`*

*Both build scripts will automatically check for and install PyInstaller if it is missing.*

---

## 3. Configuration Management

*   `packageconfig.json` - Saves local paths for Python, Ngrok, and the Workspace. Auto-created next to the executable on its first run.
*   `config.json` - Saves the core backend configuration parameters (ports, storage quotas, rate limits, host, and admin credentials).
*   On setup completion, `GUIconfig.py` automatically links the server's `config.py` file to load settings directly from the absolute path of `config.json`.

---

## 4. Bloat Removal on Download

If a `remove.txt` file exists in the repository root when downloading the server code from GitHub:
- The setup wizard will read `remove.txt` line by line.
- It will delete any listed files or directories (e.g. `package/`) to avoid downloading unnecessary installer resources into the user's active workspace.
- Format: List one path relative to the repository root per line. Lines starting with `#` are ignored as comments.
