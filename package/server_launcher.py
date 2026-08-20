"""
NasCloud - Server Launcher

Reads all paths from packageconfig.json, sets up the virtual environment
if needed, starts the Flask/Waitress server, configures and launches
ngrok for public tunneling, and displays everything in a clean GUI.
"""
import os
import sys
import json
import time
import threading
import subprocess
import urllib.request
import shutil
import zipfile
import queue
import signal
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

try:
    from pckconfig import (
        config, APP_DISPLAY_NAME, APP_NAME,
        DEFAULT_HOST, DEFAULT_PORT, DEFAULT_THREADS, CENTRAL_SERVER_URL,
        apply_google_light_theme, get_resource_path,
        GITHUB_OWNER, GITHUB_REPO, GITHUB_BRANCH, GITHUB_ZIP_URL
    )
    from packages import packages
    from GUIconfig import ServerConfigApp
except ImportError:
    from package.pckconfig import (
        config, APP_DISPLAY_NAME, APP_NAME,
        DEFAULT_HOST, DEFAULT_PORT, DEFAULT_THREADS, CENTRAL_SERVER_URL,
        apply_google_light_theme, get_resource_path,
        GITHUB_OWNER, GITHUB_REPO, GITHUB_BRANCH, GITHUB_ZIP_URL
    )
    from package.packages import packages
    from package.GUIconfig import ServerConfigApp


class ServerLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_DISPLAY_NAME} - Server")
        self.root.geometry("640x580")
        self.root.resizable(False, False)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.style = ttk.Style()
        apply_google_light_theme(self.style, self.root)

        # Process handles
        self.server_process = None
        self.tunnel_process = None
        self.is_running = False
        self.log_thread_active = threading.Event()
        self.stop_event = threading.Event()
        self.log_queue = queue.Queue()
        self.public_url = "Not connected"
        self.state_lock = threading.Lock()
        self.stopping = False
        self.close_after_stop = False

        # Load config
        try:
            config.sync_to_server_config()
        except Exception:
            pass
        self.workspace = config.get("dir", "")
        
        # Portable Binaries setup
        appdata_dir = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or os.path.expanduser("~")
        self.bin_dir = os.path.join(appdata_dir, "NasCloud", "bin")
        local_py = os.path.join(self.bin_dir, "python.exe")
        self.python_path = config.get("python", "") or (local_py if os.path.exists(local_py) else "")
        self.cloudflared_path = config.get("cloudflared", "") or os.path.join(self.bin_dir, "cloudflared.exe")
        
        self.host = config.get("host", DEFAULT_HOST)
        self.port = config.get("port", DEFAULT_PORT)
        self.threads = config.get("threads", DEFAULT_THREADS)

        self.create_widgets()
        self.center_window()
        self._drain_log_queue()
        
        # Start automatic background check for GitHub updates
        threading.Thread(target=self._verify_and_check_updates, args=(False,), daemon=True).start()

    def center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f'{w}x{h}+{x}+{y}')

    # GUI Layout
    def create_widgets(self):
        main = ttk.Frame(self.root, padding="15")
        main.pack(fill=tk.BOTH, expand=True)

        # Header
        header = ttk.Frame(main)
        header.pack(fill=tk.X, pady=(0, 12))

        try:
            logo_path = get_resource_path("nascloud.png")
            if os.path.exists(logo_path):
                original_img = tk.PhotoImage(file=logo_path)
                w, h = original_img.width(), original_img.height()
                self.logo_photo = original_img.subsample(max(1, w // 32), max(1, h // 32))
                self.logo_lbl = ttk.Label(header, image=self.logo_photo)
                self.logo_lbl.pack(side=tk.LEFT, padx=(0, 10))
        except Exception as e:
            print(f"Warning: Could not load logo image: {e}", file=sys.stderr)

        ttk.Label(
            header,
            text=f"{APP_DISPLAY_NAME} Server",
            font=("Segoe UI", 16, "bold"),
            foreground="#202124"
        ).pack(side=tk.LEFT)

        # Status Section
        status_frame = ttk.LabelFrame(main, text=" Server Status ", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))

        row1 = ttk.Frame(status_frame)
        row1.pack(fill=tk.X, pady=2)
        ttk.Label(row1, text="Status:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
        self.status_var = tk.StringVar(value="Stopped")
        self.status_lbl = ttk.Label(
            row1, textvariable=self.status_var,
            font=("Segoe UI", 10), foreground="gray"
        )
        self.status_lbl.pack(side=tk.LEFT, padx=(8, 0))

        row2 = ttk.Frame(status_frame)
        row2.pack(fill=tk.X, pady=2)
        ttk.Label(row2, text="Local:", font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.local_var = tk.StringVar(value="-")
        ttk.Label(row2, textvariable=self.local_var,
                  font=("Segoe UI", 9), foreground="#555").pack(side=tk.LEFT, padx=(8, 0))

        row3 = ttk.Frame(status_frame)
        row3.pack(fill=tk.X, pady=2)
        ttk.Label(row3, text="Workspace:", font=("Segoe UI", 9)).pack(side=tk.LEFT)
        ws_display = self.workspace if self.workspace else "Not configured"
        ttk.Label(row3, text=ws_display,
                  font=("Segoe UI", 9), foreground="#555").pack(side=tk.LEFT, padx=(8, 0))

        # Public Access Section
        url_frame = ttk.LabelFrame(main, text=" Public Access (Cloudflare Quick Tunnel) ", padding="10")
        url_frame.pack(fill=tk.X, pady=(0, 10))

        url_row = ttk.Frame(url_frame)
        url_row.pack(fill=tk.X)

        self.url_var = tk.StringVar(value="Not connected")
        self.url_entry = ttk.Entry(
            url_row, textvariable=self.url_var,
            state="readonly", width=50,
            font=("Consolas", 10)
        )
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        self.copy_btn = ttk.Button(url_row, text="Copy URL", command=self.copy_url, state="disabled")
        self.copy_btn.pack(side=tk.RIGHT)

        # Log Section
        log_frame = ttk.LabelFrame(main, text=" Server Log ", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        self.log_text = tk.Text(
            log_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            height=10,
            state="disabled",
            background="#f5f5f5",
            foreground="#202124",
            insertbackground="#202124",
            selectbackground="#e8f0fe",
            borderwidth=0,
            highlightthickness=0,
            padx=8, pady=6
        )
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(yscrollcommand=scrollbar.set)

        # Tag configs for colored log output
        self.log_text.tag_config("info", foreground="#202124")
        self.log_text.tag_config("success", foreground="#1e8e3e")
        self.log_text.tag_config("warning", foreground="#b06000")
        self.log_text.tag_config("error", foreground="#d93025")
        self.log_text.tag_config("url", foreground="#1a73e8", underline=True)

        # Button Bar
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X)

        self.start_btn = ttk.Button(
            btn_frame, text="Start Server",
            command=self.start_all,
            style="Accent.TButton"
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 6))

        self.stop_btn = ttk.Button(
            btn_frame, text="Stop Server",
            command=self.stop_all, state="disabled"
        )
        self.stop_btn.pack(side=tk.LEFT)

        self.config_btn = ttk.Button(
            btn_frame, text="Configure",
            command=self.open_config_gui
        )
        self.config_btn.pack(side=tk.LEFT, padx=(6, 0))

        self.reextract_btn = ttk.Button(
            btn_frame, text="Re-extract Python",
            command=self.reextract_python
        )
        self.reextract_btn.pack(side=tk.LEFT, padx=(6, 0))

        self.check_update_btn = ttk.Button(
            btn_frame, text="Check Updates",
            command=lambda: threading.Thread(target=self._verify_and_check_updates, args=(True,), daemon=True).start()
        )
        self.check_update_btn.pack(side=tk.LEFT, padx=(6, 0))

        ttk.Button(
            btn_frame, text="Exit",
            command=self.on_close
        ).pack(side=tk.RIGHT)

    # Logging
    def log(self, message, tag="info"):
        """Thread-safe log to the GUI text widget."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_queue.put((f"[{timestamp}] {message}\n", tag))

    def _drain_log_queue(self):
        """Batch queued log records on the Tk thread to avoid flooding root.after()."""
        if not self.root.winfo_exists():
            return

        drained = 0
        try:
            self.log_text.config(state="normal")
            while drained < 200:
                line, tag = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, line, tag)
                drained += 1
            if drained:
                self.log_text.see(tk.END)
            self.log_text.config(state="disabled")
        except queue.Empty:
            self.log_text.config(state="disabled")
        except tk.TclError:
            return

        self.root.after(100, self._drain_log_queue)

    # Status Updates
    def set_status(self, text, color):
        def _update():
            self.status_var.set(text)
            self.status_lbl.config(foreground=color)
        self.root.after(0, _update)

    def set_url(self, url):
        with self.state_lock:
            self.public_url = url
        def _update():
            self.url_var.set(url)
            self.copy_btn.config(state="normal")
        self.root.after(0, _update)

    def get_public_url(self):
        with self.state_lock:
            return self.public_url

    def copy_url(self):
        url = self.url_var.get()
        if url and url != "Not connected":
            self.root.clipboard_clear()
            self.root.clipboard_append(url)
            self.log("URL copied to clipboard!", "success")

    # Portable Python / Virtual Environment Setup
    def _ensure_venv(self):
        """Validate Python environment and return executable path."""
        # 1. Check configured python or AppData bin portable python
        if self.python_path and os.path.exists(self.python_path):
            self.log(f"Using Python environment: {self.python_path}", "success")
            return self.python_path

        local_py = os.path.join(self.bin_dir, "python.exe")
        if os.path.exists(local_py):
            self.python_path = local_py
            try:
                config.set("python", local_py)
            except Exception:
                pass
            self.log(f"Using portable Python environment: {local_py}", "success")
            return local_py

        # Extract python environment if missing (e.g. if config exists but binaries don't)
        self.log("Portable Python environment not found. Extracting bundled environment...", "info")
        self.set_status("Extracting Python...", "#b06000")
        try:
            try:
                from installdepen import extractpython
            except ImportError:
                from package.installdepen import extractpython
            extracted_py = extractpython()
            self.python_path = extracted_py
            try:
                config.set("python", extracted_py)
            except Exception:
                pass
            self.log(f"Extracted portable Python environment: {extracted_py}", "success")
            return extracted_py
        except Exception as ex:
            self.log(f"Failed to extract Python environment: {ex}", "warning")

        # 2. Legacy workspace virtual environment check
        venv_python = os.path.join(self.workspace, "env", "Scripts", "python.exe")
        if os.path.exists(venv_python):
            self.log("Virtual environment found.", "success")
            return venv_python

        self.log("ERROR: Python environment not found. Run Setup or click 'Re-extract Python'.", "error")
        return None

    def reextract_python(self):
        """Manually re-extract bundled portable Python environment into %LOCALAPPDATA%/NasCloud/bin/."""
        if self.is_running:
            messagebox.showwarning("Server Running", "Please stop the server before re-extracting Python.", parent=self.root)
            return

        confirm = messagebox.askyesno(
            "Re-extract Python",
            "This will re-extract the bundled portable Python environment into your local AppData directory to fix any missing packages or broken configuration.\n\nContinue?",
            parent=self.root
        )
        if not confirm:
            return

        def task():
            self.log("Re-extracting bundled portable Python environment...", "warning")
            self.set_status("Re-extracting Python...", "#b06000")
            try:
                try:
                    from installdepen import extractpython
                except ImportError:
                    from package.installdepen import extractpython
                extracted_py = extractpython()
                self.python_path = extracted_py
                try:
                    config.set("python", extracted_py)
                except Exception:
                    pass
                self.log(f"Successfully re-extracted portable Python: {extracted_py}", "success")
                self.set_status("Python Ready", "#1e8e3e")
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success",
                    f"Portable Python environment was successfully re-extracted to:\n{extracted_py}",
                    parent=self.root
                ))
            except Exception as ex:
                self.log(f"Failed to re-extract Python: {ex}", "error")
                self.set_status("Extraction Failed", "#d93025")
                self.root.after(0, lambda: messagebox.showerror(
                    "Extraction Failed",
                    f"Failed to re-extract Python environment:\n{ex}",
                    parent=self.root
                ))

        threading.Thread(target=task, daemon=True).start()

    def _validate_python_environment(self, python_exe, env_vars):
        """Catch missing bundled packages before starting Waitress and log exact tracebacks."""
        check_script = (
            "import sys, traceback\n"
            "try:\n"
            "    import waitress, flask, flask_cors, flask_jwt_extended, flask_sqlalchemy, sqlalchemy, dotenv, rapidfuzz, apirlpy\n"
            "    print('SUCCESS: python environment ok')\n"
            "except Exception as exc:\n"
            "    traceback.print_exc()\n"
            "    sys.exit(1)\n"
        )
        try:
            result = subprocess.run(
                [python_exe, "-c", check_script],
                cwd=self.workspace,
                env=env_vars,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
        except Exception as exc:
            self.log(f"ERROR: Python environment validation failed to execute: {exc}", "error")
            return False

        if result.returncode != 0:
            output = (result.stdout or "").strip()
            self.log("ERROR: Python environment is missing required server modules.", "error")
            if output:
                for line in output.splitlines():
                    self.log(f"[python-check] {line}", "error")
            self.log("Tip: Click 'Re-extract Python' to reinstall the bundled portable Python environment.", "warning")
            return False
        return True

    # Cloudflared URL Discovery
    def _get_cloudflared_url(self):
        """Deprecated placeholder for backward compatibility"""
        return self.url_var.get()

    # Start Sequence
    def start_all(self):
        """Launch the full start sequence in a background thread."""
        if self.is_running or self.server_process or self.tunnel_process:
            return
        self.stop_event.clear()
        with self.state_lock:
            self.public_url = "Not connected"
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        threading.Thread(target=self._start_sequence, daemon=True).start()

    def _start_sequence(self):
        self.log(f"Starting {APP_DISPLAY_NAME} server...", "info")

        # Validate Config
        if not self.workspace or not os.path.isdir(self.workspace):
            self.log("ERROR: Workspace directory not found.", "error")
            self.log(f"  Path: {self.workspace}", "error")
            self.log("Run NasCloud.exe first to configure.", "error")
            self.set_status("Configuration Error", "#d93025")
            self.root.after(0, lambda: self.start_btn.config(state="normal"))
            self.root.after(0, lambda: self.stop_btn.config(state="disabled"))
            return

        app_py = os.path.join(self.workspace, "app.py")
        if not os.path.exists(app_py):
            self.log(f"ERROR: app.py not found in workspace.", "error")
            self.log(f"  Expected: {app_py}", "error")
            self.set_status("Configuration Error", "#d93025")
            self.root.after(0, lambda: self.start_btn.config(state="normal"))
            self.root.after(0, lambda: self.stop_btn.config(state="disabled"))
            return

        # Step 1: Setup Virtual Environment
        self.set_status("Setting up environment...", "#b06000")
        venv_python = self._ensure_venv()
        if not venv_python:
            self.set_status("Setup Failed", "#d93025")
            self.root.after(0, lambda: self.start_btn.config(state="normal"))
            self.root.after(0, lambda: self.stop_btn.config(state="disabled"))
            return

        # Step 2: Start Waitress Server
        self.set_status("Starting server...", "#b06000")
        bind_host = config.get("bind_host")
        local_host = config.get("local_host")
        register_host = local_host if self.host == bind_host else self.host
        local_url = f"http://{register_host}:{self.port}"
        self.root.after(0, lambda: self.local_var.set(local_url))
        self.log(f"Starting Waitress on {self.host}:{self.port}...", "info")

        # Copy current environment and explicitly inject configured api_key as 'accesstooken'
        env_vars = os.environ.copy()
        env_vars["PYTHONUNBUFFERED"] = "1"
        env_vars["PYTHONNOUSERSITE"] = "1"
        api_key = config.get("api_key", "")
        if api_key:
            env_vars["accesstooken"] = api_key

        if not self._validate_python_environment(venv_python, env_vars):
            self.set_status("Setup Failed", "#d93025")
            self.root.after(0, lambda: self.start_btn.config(state="normal"))
            self.root.after(0, lambda: self.stop_btn.config(state="disabled"))
            return

        try:
            flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            if os.name == 'nt':
                flags |= subprocess.CREATE_NEW_PROCESS_GROUP
            self.server_process = subprocess.Popen(
                [venv_python, "-m", "waitress",
                 f"--host={self.host}",
                 f"--port={self.port}",
                 f"--threads={self.threads}",
                 "app:app"],
                cwd=self.workspace,
                env=env_vars,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=flags,
                start_new_session=(os.name != 'nt')
            )
        except FileNotFoundError:
            self.log("ERROR: Could not start server - venv python not found.", "error")
            self.set_status("Start Failed", "#d93025")
            self.root.after(0, lambda: self.start_btn.config(state="normal"))
            self.root.after(0, lambda: self.stop_btn.config(state="disabled"))
            return

        # Start log streaming thread immediately to keep pipe empty
        self.log_thread_active.set()
        threading.Thread(target=self._stream_server_logs, daemon=True).start()

        # Give the server a moment to start (or fail)
        for _ in range(30):
            if self.stop_event.is_set():
                return
            if self.server_process.poll() is not None:
                break
            time.sleep(0.1)
        if self.server_process.poll() is not None:
            self.log(f"ERROR: Server exited immediately.", "error")
            self.set_status("Server Crashed", "#d93025")
            self.server_process = None
            self.root.after(0, lambda: self.start_btn.config(state="normal"))
            self.root.after(0, lambda: self.stop_btn.config(state="disabled"))
            return

        self.log("Server started successfully!", "success")
        self.is_running = True

        # Step 3: Ensure Cloudflared Binary exists
        self.set_status("Checking cloudflared...", "#b06000")
        if not os.path.exists(self.cloudflared_path) or os.path.getsize(self.cloudflared_path) < 1000000:
            try:
                try:
                    from installdepen import extractcloudflared
                except ImportError:
                    from package.installdepen import extractcloudflared
                self.cloudflared_path = extractcloudflared()
                self.log(f"Extracted valid cloudflared binary: {self.cloudflared_path}", "success")
            except Exception as ex:
                import shutil
                find_cf = shutil.which("cloudflared") or shutil.which("cloudflared.exe")
                if find_cf and os.path.exists(find_cf) and os.path.getsize(find_cf) > 1000000:
                    self.cloudflared_path = find_cf
                    self.log(f"Found cloudflared fallback in system PATH: {self.cloudflared_path}", "success")
                else:
                    self.log(f"ERROR: cloudflared.exe not found or invalid: {ex}", "error")
                    self.set_status("Running (Local Only)", "#1e8e3e")
                    self.log("-" * 45, "info")
                    self.log(f"{APP_DISPLAY_NAME} is ready (Local Only)!", "success")
                    self.log(f"  Local:  {local_url}", "info")
                    self.log("-" * 45, "info")
                    self.notify_central_server(local_url)
                    return

        # Step 4: Start Cloudflared Tunnel
        self.set_status("Connecting cloudflared...", "#b06000")
        self.log(f"Starting cloudflared tunnel to port {self.port}...", "info")
        try:
            self.tunnel_process = subprocess.Popen(
                [self.cloudflared_path, "tunnel", "--url", f"http://127.0.0.1:{self.port}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=flags,
                start_new_session=(os.name != 'nt')
            )
            # Start background thread to stream tunnel logs and extract the URL
            self.log_thread_active.set()
            threading.Thread(target=self._stream_tunnel_logs, daemon=True).start()
        except Exception as e:
            self.log(f"ERROR: Failed to start cloudflared tunnel: {e}", "error")
            self.tunnel_process = None

        # Wait up to 15 seconds for the cloudflared URL to be captured
        self.log("Waiting for cloudflared tunnel to establish...", "info")
        for _ in range(15):
            if self.stop_event.is_set():
                return
            if self.get_public_url() != "Not connected":
                break
            time.sleep(1)

        # Done
        self.set_status("Running", "#1e8e3e")
        self.log("-" * 45, "info")
        self.log(f"{APP_DISPLAY_NAME} is ready!", "success")
        self.log(f"  Local:  {local_url}", "info")
        if self.get_public_url() != "Not connected":
            self.log(f"  Public: {self.get_public_url()}", "info")
        self.log("-" * 45, "info")

        # Notify Central Server
        final_url = self.get_public_url()
        if final_url == "Not connected":
            final_url = local_url
        self.notify_central_server(final_url)

    # Log Streaming
    def _stream_server_logs(self):
        """Read server stdout line-by-line and display in log."""
        try:
            while self.log_thread_active.is_set() and self.server_process:
                line = self.server_process.stdout.readline()
                if not line:
                    if self.server_process.poll() is not None:
                        break
                    continue
                stripped = line.strip()
                if stripped:
                    self.log(f"[server] {stripped}", "info")
        except Exception:
            pass

    def _stream_tunnel_logs(self):
        """Read cloudflared stdout line-by-line, display in log, and extract URL."""
        import re
        url_pattern = re.compile(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com')
        try:
            while self.log_thread_active.is_set() and self.tunnel_process:
                line = self.tunnel_process.stdout.readline()
                if not line:
                    if self.tunnel_process.poll() is not None:
                        break
                    continue
                stripped = line.strip()
                if stripped:
                    self.log(f"[cloudflared] {stripped}", "info")
                    match = url_pattern.search(stripped)
                    if match:
                        url = match.group(0)
                        if self.get_public_url() == "Not connected":
                            self.set_url(url)
                            self.log(f"Public Tunnel URL discovered: {url}", "success")
                            os.environ["TUNNEL_URL"] = url
                            try:
                                config.set("tunnel_url", url)
                            except Exception:
                                pass
        except Exception as e:
            self.log(f"Error reading cloudflared logs: {e}", "warning")

    # Stop Sequence
    def stop_all(self):
        """Stop server and cloudflared processes."""
        if self.stopping:
            return
        self.stopping = True
        self.stop_btn.config(state="disabled")
        self.log("Stopping server...", "warning")
        threading.Thread(target=self._stop_all_worker, daemon=True).start()
        return

    def _terminate_process_tree(self, proc, name):
        if not proc or proc.poll() is not None:
            return
        try:
            if os.name == 'nt':
                subprocess.run(
                    ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=8,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                except ProcessLookupError:
                    return
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            proc.wait(timeout=3)
            self.log(f"{name} stopped.", "info")
        except Exception as exc:
            try:
                proc.kill()
            except Exception:
                pass
            self.log(f"{name} forced to stop: {exc}", "warning")

    def _stop_all_worker(self):
        self.stop_event.set()
        self.log_thread_active.clear()
        self.is_running = False

        if self.tunnel_process:
            self._terminate_process_tree(self.tunnel_process, "Cloudflared tunnel")
            self.tunnel_process = None

        if self.server_process:
            self._terminate_process_tree(self.server_process, "Server")
            self.server_process = None

        with self.state_lock:
            self.public_url = "Not connected"

        def finish_stop():
            self.set_status("Stopped", "#5f6368")
            self.url_var.set("Not connected")
            self.local_var.set("-")
            self.copy_btn.config(state="disabled")
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            self.stopping = False
            if self.close_after_stop:
                self.root.destroy()

        self.root.after(0, finish_stop)
        self.log("All processes terminated.", "success")

    def notify_central_server(self, server_url):
        """Send an HTTP GET request to the Central Server with our URL and API Key."""
        api_key = config.get("api_key", "")
        access_code = config.get("access_code", "")
        opt_password = config.get("opt_password", "")
        
        # Use dynamically fetched URL if available, otherwise fallback to hardcoded
        central_url = config.get("central_server_url") or CENTRAL_SERVER_URL
        
        # If CENTRAL_SERVER_URL is not set or placeholder, skip
        if not central_url or "example.com" in central_url:
            self.log("Skipping Central Server notification: CENTRAL_SERVER_URL is a placeholder.", "info")
            return

        def task():
            import urllib.parse
            self.log(f"Notifying Central Server ({central_url})...", "info")
            base_url = central_url.rstrip('/')
            payload = json.dumps({
                "api": api_key,
                "link": server_url,
                "users": config.get("allowusers", False)
            }).encode('utf-8')
            try:
                req = urllib.request.Request(
                    f"{base_url}/register/api/",
                    data=payload,
                    headers={
                        'Content-Type': 'application/json',
                        'User-Agent': 'NasCloud-Server/1.0'
                    },
                    method='POST'
                )
                with urllib.request.urlopen(req, timeout=8) as resp:
                    status = resp.status
                    body = resp.read().decode('utf-8')
                    self.log(f"Central Server notified successfully (Status {status}).", "success")
            except Exception as e:
                self.log(f"Failed to notify Central Server: {e}", "warning")

            if access_code:
                self.log("Registering Frontend Access Code...", "info")
                try:
                    payload = json.dumps({
                        "api": api_key,
                        "code": access_code,
                        "userpassword": opt_password if opt_password else None
                    }).encode('utf-8')
                    
                    req_user = urllib.request.Request(
                        f"{base_url}/register/user/",
                        data=payload,
                        headers={
                            'Content-Type': 'application/json',
                            'User-Agent': 'NasCloud-Server/1.0'
                        },
                        method='POST'
                    )
                    with urllib.request.urlopen(req_user, timeout=8) as resp:
                        self.log("Frontend access code registered successfully.", "success")
                except Exception as e:
                    self.log(f"Failed to register access code: {e}", "warning")

        # Run in a background thread so we don't freeze the GUI
        threading.Thread(target=task, daemon=True).start()

    def open_config_gui(self):
        """Open the Server Configuration GUI in a new window."""
        config_win = tk.Toplevel(self.root)
        config_win.configure(bg="#ffffff")
        
        def on_complete(combined_config):
            config_win.destroy()
            config.reload()
            self.workspace = config.get("dir", "")
            self.python_path = config.get("python", "")
            self.cloudflared_path = config.get("cloudflared", "") or os.path.join(self.bin_dir, "cloudflared.exe")
            self.host = config.get("host", DEFAULT_HOST)
            self.port = config.get("port", DEFAULT_PORT)
            self.threads = config.get("threads", DEFAULT_THREADS)
            self.log("Server settings reloaded.", "success")
            
        ServerConfigApp(config_win, on_complete=on_complete, on_cancel=config_win.destroy)

    # GitHub Version Verification & Update
    def _verify_and_check_updates(self, manual=False):
        """Check current program hash against latest GitHub commit SHA."""
        if manual:
            self.log("Checking GitHub for backend code updates...", "info")
        
        current_hash = (config.get("program_hash") or "").strip()
        api_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/commits/{GITHUB_BRANCH}"
        
        try:
            req = urllib.request.Request(
                api_url,
                headers={
                    'User-Agent': 'NasCloud-Server/1.0',
                    'Accept': 'application/vnd.github.v3+json'
                }
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                latest_sha = (data.get("sha") or "").strip()
        except Exception as e:
            if manual:
                self.log(f"Failed to check updates from GitHub: {e}", "warning")
                self.root.after(0, lambda: messagebox.showwarning(
                    "Update Check Failed",
                    f"Could not connect to GitHub to verify updates:\n{e}",
                    parent=self.root
                ))
            return

        if not latest_sha:
            return

        # Case 1: No current hash saved yet (First verification)
        if not current_hash:
            config.set("program_hash", latest_sha)
            self.log(f"Initial program hash verified and saved: {latest_sha[:8]}...", "success")
            if manual:
                self.root.after(0, lambda: messagebox.showinfo(
                    "Check Updates",
                    f"Current program hash initialized and verified:\nCommit {latest_sha[:8]}",
                    parent=self.root
                ))
            return

        # Case 2: New version found
        if latest_sha != current_hash:
            self.log(f"New version found on GitHub! Commit: {latest_sha[:8]} (Current: {current_hash[:8]})", "warning")
            self.root.after(0, lambda: self._prompt_update(latest_sha))
            return

        # Case 3: Up to date
        if manual:
            self.log("Backend code is up to date with GitHub main branch.", "success")
            self.root.after(0, lambda: messagebox.showinfo(
                "Check Updates",
                "You are already running the latest version of the backend code!",
                parent=self.root
            ))

    def _prompt_update(self, latest_sha):
        """Prompt user on the GUI if they want to update to the new version."""
        confirm = messagebox.askyesno(
            "New Version Found",
            f"A new version of the backend code was found on GitHub (commit {latest_sha[:7]}).\n\n"
            "Do you want to update it right now?\n\n"
            "Note: Protected folders (like storage, userdetails, data, env) and database/config files will NOT be replaced.",
            parent=self.root
        )
        if confirm:
            threading.Thread(target=self._perform_update, args=(latest_sha,), daemon=True).start()

    def _perform_update(self, latest_sha):
        """Download latest zip from GitHub and replace workspace code while preserving protected folders."""
        self.log(f"Starting update to commit {latest_sha[:8]}...", "warning")
        if not self.workspace or not os.path.exists(self.workspace):
            self.log("ERROR: Workspace directory is not valid. Cannot update.", "error")
            return

        appdata_dir = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or os.path.expanduser("~")
        tmp_update_dir = os.path.join(appdata_dir, "NasCloud", "update_tmp")
        os.makedirs(tmp_update_dir, exist_ok=True)
        zip_path = os.path.join(tmp_update_dir, "update.zip")

        try:
            self.log(f"Downloading source repository from {GITHUB_ZIP_URL}...", "info")
            urllib.request.urlretrieve(GITHUB_ZIP_URL, zip_path)
            
            self.log("Extracting updated files...", "info")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmp_update_dir)
            
            # Find extracted root (usually NasCloud-Backend-main)
            extracted_subdirs = [
                os.path.join(tmp_update_dir, d) for d in os.listdir(tmp_update_dir)
                if os.path.isdir(os.path.join(tmp_update_dir, d)) and d != "__pycache__"
            ]
            if not extracted_subdirs:
                raise Exception("Extracted archive did not contain a project directory.")
            extracted_dir = extracted_subdirs[0]

            # Define protected items that must NOT be wiped or overwritten
            protected_folders = {
                "storage", "userdetails", "test", "data", "env", "package", ".git", "__pycache__"
            }
            # Add configured directory names if they exist
            for k in ["DestinationFolder", "Userfolder", "ratelimiter"]:
                val = config.get(k)
                if val and isinstance(val, str):
                    protected_folders.add(os.path.basename(os.path.normpath(val)).lower())

            protected_files = {
                "config.json", "packageconfig.json", "config.py", ".env", "sample.env"
            }

            self.log("Replacing old workspace files while preserving protected data and configs...", "info")
            
            # 1. Wipe existing unprotected items in self.workspace
            for item in os.listdir(self.workspace):
                item_path = os.path.join(self.workspace, item)
                item_lower = item.lower()
                if os.path.isdir(item_path):
                    if item_lower in protected_folders:
                        continue
                    try:
                        shutil.rmtree(item_path, ignore_errors=True)
                    except Exception as e:
                        self.log(f"Warning: Could not remove old directory {item}: {e}", "warning")
                elif os.path.isfile(item_path):
                    if item_lower in protected_files or item_lower.endswith(".db") or item_lower.endswith(".sqlite") or item_lower.endswith(".sqlite3"):
                        continue
                    try:
                        os.remove(item_path)
                    except Exception as e:
                        self.log(f"Warning: Could not remove old file {item}: {e}", "warning")

            # 2. Copy new items from extracted_dir to self.workspace
            for item in os.listdir(extracted_dir):
                if item == "remove.txt":
                    continue
                src_path = os.path.join(extracted_dir, item)
                dst_path = os.path.join(self.workspace, item)
                item_lower = item.lower()

                if os.path.isdir(src_path):
                    if item_lower in protected_folders and os.path.exists(dst_path):
                        # Protected directory already exists in workspace - keep existing
                        continue
                    if os.path.exists(dst_path):
                        shutil.rmtree(dst_path, ignore_errors=True)
                    shutil.copytree(src_path, dst_path)
                elif os.path.isfile(src_path):
                    if item_lower in protected_files or item_lower.endswith(".db") or item_lower.endswith(".sqlite") or item_lower.endswith(".sqlite3"):
                        if os.path.exists(dst_path):
                            # Protected local file already exists - do not overwrite
                            continue
                    shutil.copy2(src_path, dst_path)

            # Cleanup temp zip and extracted dir
            shutil.rmtree(tmp_update_dir, ignore_errors=True)

            # Update saved hash
            config.set("program_hash", latest_sha)
            self.log(f"Update complete! Code updated to commit {latest_sha[:8]}.", "success")
            self.root.after(0, lambda: messagebox.showinfo(
                "Update Complete",
                f"Backend code has been successfully updated to version {latest_sha[:7]}!\n\n"
                "All protected folders, databases, and configuration files were preserved.",
                parent=self.root
            ))

        except Exception as e:
            self.log(f"ERROR: Failed to perform code update: {e}", "error")
            self.root.after(0, lambda: messagebox.showerror(
                "Update Error",
                f"An error occurred during the update process:\n{e}",
                parent=self.root
            ))
            try:
                shutil.rmtree(tmp_update_dir, ignore_errors=True)
            except Exception:
                pass

    # Window Close
    def on_close(self):
        if self.is_running:
            confirm = messagebox.askyesno(
                "Stop Server?",
                f"The {APP_DISPLAY_NAME} server is still running.\n\n"
                "Stop the server and exit?",
                parent=self.root
            )
            if not confirm:
                return
            self.close_after_stop = True
            self.stop_all()
            return
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ServerLauncher(root)
    root.mainloop()
