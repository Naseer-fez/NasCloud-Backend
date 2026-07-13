# PersonalDrive Installer & Configuration GUI — Complete Specification Prompt

---

## 1. Role & Objective

**Role:** You are a professional UI/UX designer and Python developer.

**Objective:** Build a multi-step Tkinter GUI wizard that configures a
self-hosted personal cloud storage server called **PersonalDrive**. The
wizard handles dependency checks, project downloading, and generates
two JSON configuration files that the server reads at runtime.

**You must not guess, assume, or invent any names, labels, paths,
behaviors, or values.** Everything is explicitly defined in this
document. If something is not defined here, ask before proceeding.

---

## 2. Branding & Naming Constants

All display names, window titles, labels, and identifiers across the
entire application MUST be derived from this single block. No hardcoded
strings elsewhere.

```python
# ──────────────────────────────────────────────
# BRANDING CONSTANTS — Single Source of Truth
# ──────────────────────────────────────────────
APP_NAME            = "PersonalDrive"
APP_DISPLAY_NAME    = "Personal Drive"
APP_DESCRIPTION     = "Self-hosted personal cloud storage server"

# Window Titles (used in root.title())
SETUP_TITLE         = f"{APP_DISPLAY_NAME} Setup"
SETUP_STEP1_TITLE   = f"{SETUP_TITLE} — Step 1: Workspace"
SETUP_STEP2_TITLE   = f"{SETUP_TITLE} — Step 2: Ngrok Auth"
SETUP_STEP3_TITLE   = f"{SETUP_TITLE} — Step 3: Code Server"
CONFIG_TITLE        = f"{APP_DISPLAY_NAME} — Server Configuration"
HELP_TITLE          = "Ngrok Authtoken Help"
CONFIG_HELP_TITLE   = "Configuration Guide"

# Section Labels (used inside LabelFrames)
LBL_WORKSPACE       = " Select Workspace "
LBL_INSTALL_OPTIONS  = " Installation Options "
LBL_NGROK_AUTH       = " Configure Ngrok Authentication "
LBL_CODE_SERVER      = " Code Server Setup "
LBL_DIRECTORIES      = " Storage Directories "
LBL_LIMITS           = " Storage & Bandwidth Limits "
LBL_SECURITY         = " Security & Authentication "
LBL_RATE_LIMITER     = " Rate Limiting Settings "
LBL_NETWORK          = " Connections & Network URLs "

# GitHub Source (used for code download)
GITHUB_OWNER        = "Naseer-fez"
GITHUB_REPO         = "PersonalDrive"
GITHUB_BRANCH       = "main"
GITHUB_ZIP_URL      = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/archive/refs/heads/{GITHUB_BRANCH}.zip"
GITHUB_EXTRACTED_DIR = f"{GITHUB_REPO}-{GITHUB_BRANCH}"

# Ngrok Links (used in Help dialogs)
NGROK_SIGNUP_URL     = "https://ngrok.com"
NGROK_DASHBOARD_URL  = "https://dashboard.ngrok.com"

# File Names
PACKAGE_CONFIG_FILE  = "packageconfig.json"
SERVER_CONFIG_FILE   = "config.json"
CODE_CONFIG_SCRIPT   = "config.py"

# Dependency Names
PYTHON_EXE           = "python.exe"
NGROK_EXE            = "ngrok.exe"

# Default Values (used when no prior config exists)
DEFAULT_BANDWIDTH    = 100
DEFAULT_USER_SPACE   = 10
DEFAULT_JWT_MINUTES  = 30
DEFAULT_FREQUENCY    = 50
DEFAULT_RESET_SEC    = 60
DEFAULT_COOLDOWN_SEC = 30
DEFAULT_FRONTEND_URL = "http://localhost:5174"
DEFAULT_CORS_ORIGIN  = "*"
DEFAULT_LOGIN        = False
DEFAULT_RATE_LIMITER = False
```

---

## 3. What is PersonalDrive? (Architectural Context)

PersonalDrive is a **self-hosted, RESTful backend API** for managing
personal cloud storage, built with Python/Flask. It provides:

- **Chunked file upload/download** (prevents OOM on large files)
- **Nested directory management** (create, move, rename folders)
- **Trash system** (soft-delete before permanent removal)
- **Public file sharing** (generate shareable links)
- **User storage quotas** (configurable GB limits per user)
- **JWT authentication** (login, registration, password recovery)
- **IP-based rate limiting** (prevents abuse/brute-force)

### Project Structure (Server Code)

```
PersonalDrive/                  ← The server repository
├── app.py                      ← Flask application entry point
├── config.py                   ← Runtime config loader (reads config.json)
├── config.json                 ← Server runtime configuration
├── models/                     ← SQLAlchemy database models
├── routes/                     ← Flask blueprints (upload, download, etc.)
├── utils/                      ← Business logic (Storage, RateLimiter, Auth)
├── test/                       ← Upload destination (DestinationFolder)
└── userdetails/                ← User profile JSON storage (Userfolder)
```

### Installer Package Structure

```
package/                        ← The installer/configuration package
├── V1/                         ← Backup of previous version code
├── pckconfig.py                ← Config helper class (reads/writes packageconfig.json)
├── packageconfig.json          ← Package-level configuration storage
├── installdepen.py             ← Fast dependency checker & downloader
├── GUIsetup.py                 ← Multi-page setup wizard (Steps 1–3)
├── GUIconfig.py                ← Server configuration GUI (Step 4)
├── run_test.py                 ← Sequential runner (GUIsetup → GUIconfig)
├── controler.py                ← Server launcher (starts Flask via waitress)
├── pipinstaller.py             ← Virtual environment & pip dependency installer
├── packages.py                 ← List of required pip packages
├── requirements.txt            ← pip requirements file
└── devreq.txt                  ← Development requirements
```

### How the Server Loads Configuration at Runtime

The server's `config.py` file contains:
```python
PATH = "config.json"   # ← This line is what the installer modifies
class Config:
    def __init__(self):
        self.reload()
    def reload(self):
        with open(PATH) as file:
            self.data = json.load(file)
    def get(self, key, default=None):
        return self.data.get(key, default)
config = Config()
```

The installer GUI replaces the `PATH` variable with the absolute path
to the generated `config.json`, so the server knows exactly where to
load its configuration from at runtime.

---

## 4. Configuration Data Schema

### 4.1 Complete Combined Schema

Both `packageconfig.json` and `config.json` store the **exact same
combined dataset** (redundant mirroring). This is intentional so users
can edit either file.

```json
{
    "dir": "D:/path/to/workspace",
    "python": "D:/path/to/python.exe",
    "ngrok": "C:/path/to/ngrok.exe",
    "ngrok_token": "2abcDEFghIJKlmNOpQRstuVWxyz",
    "config_path": "D:/path/to/workspace/config.json",

    "DestinationFolder": "D:/path/to/workspace/test",
    "Userfolder": "D:/path/to/workspace/userdetails",
    "size": 100,
    "basic": 10,
    "backend": "",
    "Allowlogin": true,
    "jwtduration": 30,
    "ratelimiter": "D:/path/to/workspace/data",
    "FrontendURL": "*",
    "URL": "http://localhost:5174",
    "Ratelimiter": true,
    "Allowfreq": 50,
    "Resettime": 60,
    "cooldowntime": 30
}
```

### 4.2 Key Definitions

| Key | Type | Source | Description |
|---|---|---|---|
| `dir` | string | Setup GUI Step 3 | Absolute path to the code server repository directory |
| `python` | string | installdepen.py | Absolute path to python.exe |
| `ngrok` | string | installdepen.py | Absolute path to ngrok.exe |
| `ngrok_token` | string | Setup GUI Step 2 | Ngrok authentication token |
| `config_path` | string | Config GUI | Absolute path to generated config.json |
| `DestinationFolder` | string | Config GUI | Where user-uploaded files are physically stored |
| `Userfolder` | string | Config GUI | Where user profile JSONs and DB records are stored |
| `size` | int | Config GUI | Total bandwidth/transfer quota limit |
| `basic` | int | Config GUI | Max disk storage (GB) allocated per user |
| `backend` | string | Config GUI | Reserved for future backend URL (currently empty) |
| `Allowlogin` | bool | Config GUI | Whether user registration/login is enabled. If false, Single User Mode is active (all requests map to a default user 'default_user' without authentication). |
| `jwtduration` | int | Config GUI | JWT session token expiry period in minutes |
| `ratelimiter` | string | Config GUI | Folder path for rate limiter tracking database |
| `FrontendURL` | string | Config GUI | CORS allowed origin header (`*` = allow all) |
| `URL` | string | Config GUI | Frontend web application URL |
| `Ratelimiter` | bool | Config GUI | Whether rate limiting is active |
| `Allowfreq` | int | Config GUI | Max requests allowed within reset window |
| `Resettime` | int | Config GUI | Rate limit counter reset interval (seconds) |
| `cooldowntime` | int | Config GUI | Temporary block duration after exceeding limit (seconds) |

---

## 5. Dependency Checking (installdepen.py)

### Design Rules
- **NEVER spawn subprocesses** for dependency lookups. No `subprocess.run`,
  no `where python`, no `ngrok version` commands. These are slow (1-2s
  on Windows).
- Use `sys.executable` for instant Python path detection.
- Use a `find_executable(name)` helper that scans `os.environ["PATH"]`
  directories and checks `os.path.exists()` for the target executable.

### Public API
```python
def PYTHON() -> list:
    """Returns [command, path] on success, [0, 0] on failure."""

def NGROK() -> list:
    """Returns [command, path] on success, [0, 0] on failure."""
```

### Download Functions
- `downloadpython()`: Architecture-aware download from python.org.
  Supports AMD64, x86, ARM64. Uses `urllib.request.urlretrieve`.
- `downloadngrok()`: Architecture-aware download from equinox.io.
  Downloads ZIP, extracts using `zipfile` into workspace.

---

## 6. Setup Wizard — GUIsetup.py (3 Pages)

Class: `ProgramSetupApp`
Window size: `550x380`
Style theme: `vista` (fallback to `clam`)

### Page 1: Workspace & Dependency Options

**Title:** Uses `SETUP_STEP1_TITLE`

**Layout:**
```
┌─ LBL_WORKSPACE ────────────────────────────┐
│ "Select where you want to save the program" │
│ [path entry field        ] [Browse...]       │
│              [Next]                          │
└──────────────────────────────────────────────┘
┌─ LBL_INSTALL_OPTIONS ──────────────────────┐
│ [Install Python]    [Install Ngrok]         │
│ [Python Already]    [Ngrok Already]         │
└─────────────────────────────────────────────┘
```

**Behavior:**
- The 4 option buttons are `ttk.Checkbutton` with `style="Toolbutton"`.
- "Install Python" and "Python Already Installed" are mutually exclusive
  (selecting one disables the other).
- Same for Ngrok pair.
- If nothing is selected and user clicks Next → defaults to
  `"already_installed"` for both.
- Next button validates:
  1. Path is not empty.
  2. Directory exists or offers to create it.
  3. Directory is writable.
  4. Saves `dir` to packageconfig.json.
  5. Runs `performbackend()` which calls `PYTHON()` and `NGROK()`.
  6. If a dependency is not found → shows error message → opens
     `ask_manual_path()` dialog for manual path selection.
  7. On success → transitions to Page 2.

**Manual Path Dialog (`ask_manual_path`):**
- Modal `Toplevel` window, `450x180`.
- Shows: text label, entry + Browse button, Cancel + Confirm buttons.
- Confirm validates that the executable exists at the given path.

### Page 2: Ngrok Authtoken

**Title:** Uses `SETUP_STEP2_TITLE`

**Layout:**
```
┌─ LBL_NGROK_AUTH ──────────────────────────┐
│ "Please enter your Ngrok Authtoken below"  │
│ (gray) "You can obtain this token from..." │
│ [token entry field                       ] │
└────────────────────────────────────────────┘
[Back]  [Help]                        [Next]
```

**Help Dialog:**
- Modal `Toplevel`, `480x250`.
- Contains a 2-step paginated guide:
  - **Step 1:** "Create an account" — clickable hyperlink to
    `NGROK_SIGNUP_URL`. Opens browser via `webbrowser.open_new()`.
  - **Step 2:** "Get the Authtoken" — clickable hyperlink to
    `NGROK_DASHBOARD_URL`. Shows step-by-step instructions and
    sample token format.
- `tk.Text` widget (read-only) with `ttk.Scrollbar`.
- Hyperlinks use tag `"link"` with blue foreground, underline, and
  hand cursor on hover.
- Previous/Next buttons disable at boundaries.
- Close button destroys dialog.

**Next Action:** Saves `ngrok_token` to packageconfig.json → Page 3.

### Page 3: Code Server Setup

**Title:** Uses `SETUP_STEP3_TITLE`

**Layout:**
```
┌─ LBL_CODE_SERVER ─────────────────────────┐
│ "Install the Code server?"                 │
│                                            │
│ [Already Installed]  [Not Installed]       │
│                                            │
│ Selected Code Server Path:                 │
│ (blue italic) "Not Configured"             │
└────────────────────────────────────────────┘
[Back]                                [Finish]
```

**"Already Installed" Button:**
- Opens `filedialog.askdirectory`.
- Sets the selected path in the status label.

**"Not Installed (Download)" Button:**
1. Opens `filedialog.askdirectory` → user picks parent folder.
2. Launches `threading.Thread(daemon=True)` → downloads ZIP from
   `GITHUB_ZIP_URL` via `urllib.request.urlretrieve`.
3. Shows a modal progress dialog (`400x130`):
   - Status label ("Downloading..." → "Extracting...")
   - `ttk.Progressbar` (determinate during download → indeterminate
     during extraction)
   - Percentage label
   - GUI updates via `self.root.after(0, callback)` (thread-safe).
4. Extracts ZIP using `zipfile.ZipFile` into parent folder.
5. Deletes temporary ZIP file.
6. Extracted folder name: `GITHUB_EXTRACTED_DIR` (i.e. `PersonalDrive-main`).
7. Shows success messagebox.

**Finish Action:**
- Validates code server path is not "Not Configured".
- Saves `dir` to packageconfig.json.
- Prints result JSON to stdout with `#FEZ` comment marker.
- Destroys window, `sys.exit(0)`.

---

## 7. Server Configuration GUI — GUIconfig.py (1 Page, Dynamic)

Class: `ServerConfigApp`
Initial window size: `620x680` (auto-resizes dynamically)
Style theme: `vista` (fallback to `clam`)

**Title:** Uses `CONFIG_TITLE`

### Design Rules
1. **Minimal initial layout.** Advanced options (JWT, Rate Limiter
   fields) are hidden by default.
2. **Dynamic expansion.** Checking a toggle checkbox packs its
   sub-frame via `.pack()`. Unchecking hides it via `.pack_forget()`.
3. **Auto window resize.** After toggle, call `self.root.geometry("")`
   then `center_window()` to auto-fit visible content.
4. **No global Help button.** Instead, blue `[?]` labels are placed
   inline next to section headers.

### Layout Sections

**Section 1: Storage Directories** (`LBL_DIRECTORIES`)
```
┌─ LBL_DIRECTORIES ─────────────── [?] ────┐
│ Destination Folder: [entry     ] [Browse] │
│ User Details Folder: [entry    ] [Browse] │
└───────────────────────────────────────────┘
```
- Browsing Destination auto-sets User Details to sibling
  `<parent>/userdetails`.

**Section 2: Storage & Bandwidth Limits** (`LBL_LIMITS`)
```
┌─ LBL_LIMITS ──────────────────── [?] ────┐
│ Bandwidth (size): [spinbox]               │
│ Space/User (basic): [spinbox]             │
└───────────────────────────────────────────┘
```

**Section 3: Security & Authentication** (`LBL_SECURITY`) — DYNAMIC
```
┌─ LBL_SECURITY ───────────────── [?] ─────┐
│ ☐ Allow Login                              │
│  ┌── (shown only when checked) ──────┐    │
│  │ JWT Expiration (min): [spinbox]   │    │
│  └───────────────────────────────────┘    │
└───────────────────────────────────────────┘
```
- `DEFAULT_LOGIN = False` → checkbox unchecked, JWT frame hidden.

**Section 4: Rate Limiting Settings** (`LBL_RATE_LIMITER`) — DYNAMIC
```
┌─ LBL_RATE_LIMITER ──────────── [?] ──────┐
│ ☐ Enable Rate Limiter                      │
│  ┌── (shown only when checked) ──────┐    │
│  │ DB Path: [entry        ] [Browse] │    │
│  │ Freq: [spin] Reset: [spin]        │    │
│  │ Cooldown: [spin]                  │    │
│  └───────────────────────────────────┘    │
└───────────────────────────────────────────┘
```
- `DEFAULT_RATE_LIMITER = False` → unchecked, sub-frame hidden.

**Section 5: Connections & Network URLs** (`LBL_NETWORK`)
```
┌─ LBL_NETWORK ────────────────── [?] ─────┐
│ Frontend URL (URL): [entry              ] │
│ CORS Header (FrontendURL): [entry       ] │
└───────────────────────────────────────────┘
```

**Action Bar:**
```
[Cancel]                  [Finish Configuration]
```

### `[?]` Help Link Behavior
- Created by helper: `create_help_link(parent, title, text)`.
- Returns a `ttk.Label` with text `"[?]"`, foreground `#0066cc`,
  cursor `hand2`, font `("Segoe UI", 9, "bold")`.
- On click → `messagebox.showinfo(title, text)`.
- Each `[?]` shows ONLY the information relevant to its section.

### Help Text Content (Exact)

**Directories:**
```
Destination Folder:
Where uploaded files are stored.

User Details Folder:
Stores local user databases and profiles.
```

**Limits:**
```
Bandwidth Limit (size):
Sets standard network transfer quota limits.

Space per User (basic):
Max disk storage space (in GB) allocated per basic user account.
```

**Security:**
```
Allow Login:
Enables user authentication. If unchecked, the server restricts
login access and registration.

JWT Duration:
The period (in minutes) a logged-in user session remains valid
before expiring, requiring them to sign in again.
```

**Rate Limiter:**
```
Enable Rate Limiter:
Toggles request limit tracking to prevent server overload.

Database Path:
Stores the limiter tracking logs database.

Request Frequency:
Max request threshold permitted within the Reset Duration.

Reset / Cooldown Time:
Timing thresholds (in seconds) defining the reset window and
the temporary block duration.
```

**Network:**
```
Frontend website URL (URL):
The link to your client web interface application
(e.g. http://localhost:5174).

CORS Header (FrontendURL):
Controls client request access permissions. Set to '*' to allow
all client websites to contact the server API.
```

### Data Loading Priority
1. Read `config_path` from `packageconfig.json`.
2. If `config_path` file exists → load JSON from it.
3. Fall back to values in `packageconfig.json`.
4. Fall back to default constants.

### Finish Configuration Action (Exact Sequence)
1. Validate required fields (storage paths, rate limiter path if
   enabled).
2. Create missing directories (`DestinationFolder`, `Userfolder`,
   rate limiter path) via `os.makedirs(exist_ok=True)`.
3. Build `server_data` dictionary from all form inputs.
4. Fetch `package_data` from packageconfig (`dir`, `python`, `ngrok`,
   `ngrok_token`).
5. Merge into `combined_config` dictionary.
6. Add `config_path` key pointing to `<workspace_dir>/config.json`.
7. **Write `combined_config` to `<workspace_dir>/config.json`.**
8. **Write `combined_config` to `packageconfig.json`** (every key
   via `config.set(key, value)`).
9. **Update `config.py` PATH variable:**
   - Locate `<workspace_dir>/config.py`.
   - Regex: `^PATH\s*=\s*['"].*?['"]`
   - Replace with: `PATH="<absolute_path_to_config.json>"`
   - Use forward slashes in path.
10. Print combined JSON to stdout.
11. Destroy window, `sys.exit(0)`.

---

## 8. Sequential Runner — run_test.py

Launches both GUIs as sequential subprocesses:
1. Run `GUIsetup.py` → capture stdout.
2. If exit code 0 → run `GUIconfig.py` → capture stdout.
3. Print outputs from both steps.

---

## 9. Package Config Helper — pckconfig.py

```python
class Config:
    def __init__(self):
        self.reload()
    def reload(self):
        with open(PACKAGE_CONFIG_FILE) as file:
            self.data = json.load(file)
    def get(self, key, default=None):
        return self.data.get(key, default)
    def set(self, key, value):
        self.data[key] = value
        with open(PACKAGE_CONFIG_FILE, "w") as file:
            json.dump(self.data, file, indent=4)

config = Config()
```

---

## 10. V1 Backup Directory

The `package/V1/` directory contains the complete backup of all
previous version code before any new modifications. Files:
- `GUIsetup.py`, `GUIconfig.py`, `installdepen.py`
- `pckconfig.py`, `packageconfig.json`, `run_test.py`
- `controler.py`, `pipinstaller.py`, `packages.py`

---

## 11. Technology & Environment Constraints

- **Language:** Python 3.12+
- **GUI Framework:** Tkinter (standard library only)
- **Style Theme:** `vista` on Windows, `clam` fallback
- **No external GUI dependencies.** No PyQt, no Kivy, no web frameworks.
- **No git dependency.** Repository download uses ZIP via urllib.
- **No hardcoded paths.** All paths come from config files or user input.
- **Thread-safe GUI updates** using `root.after(0, callback)` for any
  background thread work.
- **OS:** Windows (primary target)
