import os
import sys
import json
import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

try:
    from pckconfig import (
        config, CONFIG_TITLE,
        LBL_DIRECTORIES, LBL_LIMITS, LBL_SECURITY, LBL_RATE_LIMITER, LBL_NETWORK,
        DEFAULT_BANDWIDTH, DEFAULT_USER_SPACE, DEFAULT_JWT_MINUTES,
        DEFAULT_FREQUENCY, DEFAULT_RESET_SEC, DEFAULT_COOLDOWN_SEC,
        DEFAULT_FRONTEND_URL, DEFAULT_CORS_ORIGIN, DEFAULT_LOGIN, DEFAULT_RATE_LIMITER,
        DEFAULT_HOST, DEFAULT_PORT, DEFAULT_THREADS,
        SERVER_CONFIG_FILE, CODE_CONFIG_SCRIPT
    )
except ImportError:
    from package.pckconfig import (
        config, CONFIG_TITLE,
        LBL_DIRECTORIES, LBL_LIMITS, LBL_SECURITY, LBL_RATE_LIMITER, LBL_NETWORK,
        DEFAULT_BANDWIDTH, DEFAULT_USER_SPACE, DEFAULT_JWT_MINUTES,
        DEFAULT_FREQUENCY, DEFAULT_RESET_SEC, DEFAULT_COOLDOWN_SEC,
        DEFAULT_FRONTEND_URL, DEFAULT_CORS_ORIGIN, DEFAULT_LOGIN, DEFAULT_RATE_LIMITER,
        DEFAULT_HOST, DEFAULT_PORT, DEFAULT_THREADS,
        SERVER_CONFIG_FILE, CODE_CONFIG_SCRIPT
    )

class ServerConfigApp:
    def __init__(self, root, on_complete=None, on_cancel=None):
        self.root = root
        self.on_complete = on_complete
        self.on_cancel = on_cancel
        self.root.title(CONFIG_TITLE)
        self.root.geometry("620x720")
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.style = ttk.Style()
        self.style.theme_use('vista' if 'vista' in self.style.theme_names() else 'clam')
        
        self.workspace_dir = os.path.normpath(config.get("dir") or os.getcwd())
        
        self.create_widgets()
        self.load_saved_data()
        self.center_window()

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_help_link(self, parent, title, text):
        lbl = ttk.Label(
            parent, 
            text="[?]", 
            foreground="#0066cc", 
            cursor="hand2",
            font=("Segoe UI", 9, "bold")
        )
        lbl.bind("<Button-1>", lambda e: messagebox.showinfo(title, text, parent=self.root))
        return lbl

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Directories Config
        dir_frame = ttk.LabelFrame(main_frame, text=LBL_DIRECTORIES, padding="10")
        dir_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(dir_frame, text="Destination Folder:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.dest_var = tk.StringVar()
        self.dest_entry = ttk.Entry(dir_frame, textvariable=self.dest_var, width=45)
        self.dest_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(dir_frame, text="Browse", command=self.browse_dest).grid(row=0, column=2, pady=2)

        ttk.Label(dir_frame, text="User Details Folder:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.user_var = tk.StringVar()
        self.user_entry = ttk.Entry(dir_frame, textvariable=self.user_var, width=45)
        self.user_entry.grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(dir_frame, text="Browse", command=self.browse_user).grid(row=1, column=2, pady=2)

        self.create_help_link(
            dir_frame,
            "Storage Directories Help",
            "Destination Folder:\nWhere uploaded files are stored.\n\nUser Details Folder:\nStores local user databases and profiles."
        ).grid(row=0, column=3, rowspan=2, padx=10, sticky=tk.N)

        # 2. Limits Config
        limits_frame = ttk.LabelFrame(main_frame, text=LBL_LIMITS, padding="10")
        limits_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(limits_frame, text="Bandwidth Limit (size):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.size_var = tk.IntVar()
        self.size_spin = ttk.Spinbox(limits_frame, from_=1, to=10000, textvariable=self.size_var, width=8)
        self.size_spin.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(limits_frame, text="Space per User (basic):").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.basic_var = tk.IntVar()
        self.basic_spin = ttk.Spinbox(limits_frame, from_=1, to=1000, textvariable=self.basic_var, width=8)
        self.basic_spin.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)

        self.create_help_link(
            limits_frame,
            "Limits Help",
            "Bandwidth Limit (size):\nSets standard network transfer quota limits.\n\nSpace per User (basic):\nMax disk storage space (in GB) allocated per basic user account."
        ).grid(row=0, column=4, padx=10, sticky=tk.W)

        # 3. Security (Login)
        self.sec_frame = ttk.LabelFrame(main_frame, text=LBL_SECURITY, padding="10")
        self.sec_frame.pack(fill=tk.X, pady=(0, 10))

        sec_header_row = ttk.Frame(self.sec_frame)
        sec_header_row.pack(fill=tk.X)

        self.login_var = tk.BooleanVar(value=DEFAULT_LOGIN)
        self.login_check = ttk.Checkbutton(
            sec_header_row, 
            text="Allow Login", 
            variable=self.login_var,
            command=self.toggle_login_state
        )
        self.login_check.pack(side=tk.LEFT)

        self.create_help_link(
            sec_header_row,
            "Security & Login Help",
            "Allow Login:\nEnables user authentication. If unchecked, the server restricts login access and registration.\n\nJWT Duration:\nThe period (in minutes) a logged-in user session remains valid before expiring, requiring them to sign in again."
        ).pack(side=tk.LEFT, padx=10)

        self.jwt_frame = ttk.Frame(self.sec_frame)
        ttk.Label(self.jwt_frame, text="JWT Expiration (minutes):").pack(side=tk.LEFT, pady=2)
        self.jwt_var = tk.IntVar()
        self.jwt_spin = ttk.Spinbox(self.jwt_frame, from_=1, to=1440, textvariable=self.jwt_var, width=10)
        self.jwt_spin.pack(side=tk.LEFT, padx=5, pady=2)

        # 4. Rate Limiter Config
        self.rl_frame = ttk.LabelFrame(main_frame, text=LBL_RATE_LIMITER, padding="10")
        self.rl_frame.pack(fill=tk.X, pady=(0, 10))

        rl_header_row = ttk.Frame(self.rl_frame)
        rl_header_row.pack(fill=tk.X)

        self.rl_enable_var = tk.BooleanVar(value=DEFAULT_RATE_LIMITER)
        self.rl_check = ttk.Checkbutton(
            rl_header_row, 
            text="Enable Rate Limiter", 
            variable=self.rl_enable_var,
            command=self.toggle_rl_states
        )
        self.rl_check.pack(side=tk.LEFT)

        self.create_help_link(
            rl_header_row,
            "Rate Limiting Help",
            "Enable Rate Limiter:\nToggles request limit tracking to prevent server overload.\n\nDatabase Path:\nStores the limiter tracking logs database.\n\nRequest Frequency:\nMax request threshold permitted within the Reset Duration.\n\nReset / Cooldown Time:\nTiming thresholds (in seconds) defining the reset window and the temporary block duration."
        ).pack(side=tk.LEFT, padx=10)

        self.rl_options_frame = ttk.Frame(self.rl_frame)
        
        path_row = ttk.Frame(self.rl_options_frame)
        path_row.pack(fill=tk.X, pady=2)
        ttk.Label(path_row, text="Limiter Database Path:").pack(side=tk.LEFT)
        self.rl_path_var = tk.StringVar()
        self.rl_path_entry = ttk.Entry(path_row, textvariable=self.rl_path_var, width=40)
        self.rl_path_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.rl_path_btn = ttk.Button(path_row, text="Browse", command=self.browse_rl_path)
        self.rl_path_btn.pack(side=tk.RIGHT)

        grid_row = ttk.Frame(self.rl_options_frame)
        grid_row.pack(fill=tk.X, pady=2)
        
        ttk.Label(grid_row, text="Frequency:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.freq_var = tk.IntVar()
        self.freq_spin = ttk.Spinbox(grid_row, from_=1, to=1000, textvariable=self.freq_var, width=8)
        self.freq_spin.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(grid_row, text="Reset (sec):").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.reset_var = tk.IntVar()
        self.reset_spin = ttk.Spinbox(grid_row, from_=1, to=86400, textvariable=self.reset_var, width=8)
        self.reset_spin.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)

        ttk.Label(grid_row, text="Cooldown (sec):").grid(row=0, column=4, sticky=tk.W, pady=2)
        self.cooldown_var = tk.IntVar()
        self.cooldown_spin = ttk.Spinbox(grid_row, from_=1, to=86400, textvariable=self.cooldown_var, width=8)
        self.cooldown_spin.grid(row=0, column=5, sticky=tk.W, padx=5, pady=2)

        # 5. Network Links & Server Settings
        net_frame = ttk.LabelFrame(main_frame, text=LBL_NETWORK, padding="10")
        net_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(net_frame, text="Frontend website URL (URL):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(net_frame, textvariable=self.url_var, width=45)
        self.url_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(net_frame, text="CORS Origin Header (FrontendURL):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.cors_var = tk.StringVar()
        self.cors_entry = ttk.Entry(net_frame, textvariable=self.cors_var, width=45)
        self.cors_entry.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(net_frame, text="Server Host:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.host_var = tk.StringVar()
        self.host_entry = ttk.Entry(net_frame, textvariable=self.host_var, width=45)
        self.host_entry.grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(net_frame, text="Server Port:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.port_var = tk.IntVar()
        self.port_spin = ttk.Spinbox(net_frame, from_=1, to=65535, textvariable=self.port_var, width=8)
        self.port_spin.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(net_frame, text="Worker Threads:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.threads_var = tk.IntVar()
        self.threads_spin = ttk.Spinbox(net_frame, from_=1, to=64, textvariable=self.threads_var, width=8)
        self.threads_spin.grid(row=4, column=1, sticky=tk.W, padx=5, pady=2)

        self.create_help_link(
            net_frame,
            "Connections & URLs Help",
            "Frontend website URL (URL):\nThe link to your client web interface application (e.g. http://localhost:5174).\n\nCORS Header (FrontendURL):\nControls client request access permissions. Set to '*' to allow all client websites to contact the server API.\n\nServer Host:\nThe network interface the server binds to (e.g. 0.0.0.0 for all interfaces, 127.0.0.1 for local only).\n\nServer Port:\nThe port number the server listens on (e.g. 5000).\n\nWorker Threads:\nNumber of concurrent request handler threads for the Waitress server. More threads = more simultaneous users. Default is 4."
        ).grid(row=0, column=2, rowspan=5, padx=10, sticky=tk.N)

        # Actions Panel
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.cancel_btn = ttk.Button(action_frame, text="Cancel", command=self.on_close)
        self.cancel_btn.pack(side=tk.LEFT)

        self.finish_btn = ttk.Button(action_frame, text="Finish Configuration", command=self.handle_finish)
        self.finish_btn.pack(side=tk.RIGHT)

    def toggle_login_state(self):
        if self.login_var.get():
            self.jwt_frame.pack(fill=tk.X, pady=(5, 0), anchor=tk.W)
        else:
            self.jwt_frame.pack_forget()
        self.auto_adjust_height()

    def toggle_rl_states(self):
        if self.rl_enable_var.get():
            self.rl_options_frame.pack(fill=tk.X, pady=(5, 0))
        else:
            self.rl_options_frame.pack_forget()
        self.auto_adjust_height()

    def auto_adjust_height(self):
        self.root.update_idletasks()
        self.root.geometry("")
        self.center_window()

    def load_saved_data(self):
        config_path = config.get("config_path", "")
        
        server_data = {}
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    server_data = json.load(f)
            except Exception:
                pass
                
        self.dest_var.set(os.path.normpath(
            server_data.get("DestinationFolder") or 
            config.get("DestinationFolder") or 
            os.path.join(self.workspace_dir, "test")
        ))
        self.user_var.set(os.path.normpath(
            server_data.get("Userfolder") or 
            config.get("Userfolder") or 
            os.path.join(self.workspace_dir, "userdetails")
        ))
        
        self.size_var.set(server_data.get("size") or config.get("size", DEFAULT_BANDWIDTH))
        self.basic_var.set(server_data.get("basic") or config.get("basic", DEFAULT_USER_SPACE))
        
        self.login_var.set(server_data.get("Allowlogin") if "Allowlogin" in server_data else config.get("Allowlogin", DEFAULT_LOGIN))
        self.jwt_var.set(server_data.get("jwtduration") or config.get("jwtduration", DEFAULT_JWT_MINUTES))
        self.toggle_login_state()
        
        self.rl_enable_var.set(server_data.get("Ratelimiter") if "Ratelimiter" in server_data else config.get("Ratelimiter", DEFAULT_RATE_LIMITER))
        self.rl_path_var.set(os.path.normpath(
            server_data.get("ratelimiter") or 
            config.get("ratelimiter") or 
            os.path.join(self.workspace_dir, "data")
        ))
        self.freq_var.set(server_data.get("Allowfreq") or config.get("Allowfreq", DEFAULT_FREQUENCY))
        self.reset_var.set(server_data.get("Resettime") or config.get("Resettime", DEFAULT_RESET_SEC))
        self.cooldown_var.set(server_data.get("cooldowntime") or config.get("cooldowntime", DEFAULT_COOLDOWN_SEC))
        self.toggle_rl_states()
        
        self.url_var.set(server_data.get("URL") or config.get("URL", DEFAULT_FRONTEND_URL))
        self.cors_var.set(server_data.get("FrontendURL") or config.get("FrontendURL", DEFAULT_CORS_ORIGIN))
        self.host_var.set(server_data.get("host") or config.get("host", DEFAULT_HOST))
        self.port_var.set(server_data.get("port") or config.get("port", DEFAULT_PORT))
        self.threads_var.set(server_data.get("threads") or config.get("threads", DEFAULT_THREADS))
        
        self.auto_adjust_height()

    def browse_dest(self):
        folder = filedialog.askdirectory(initialdir=self.workspace_dir, title="Select Destination Folder")
        if folder:
            self.dest_var.set(os.path.normpath(folder))
            parent_dir = os.path.dirname(folder)
            self.user_var.set(os.path.normpath(os.path.join(parent_dir, "userdetails")))

    def browse_user(self):
        folder = filedialog.askdirectory(initialdir=self.workspace_dir, title="Select User Details Folder")
        if folder:
            self.user_var.set(os.path.normpath(folder))

    def browse_rl_path(self):
        folder = filedialog.askdirectory(initialdir=self.workspace_dir, title="Select Rate Limiter Database Folder")
        if folder:
            self.rl_path_var.set(os.path.normpath(folder))

    def update_config_py_path(self, config_py_path, target_config_json_path):
        if not os.path.exists(config_py_path):
            return False
            
        try:
            with open(config_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            pattern = r'^PATH\s*=\s*[\'"].*?[\'"]'
            normalized_path = target_config_json_path.replace("\\", "/")
            replacement = f'PATH="{normalized_path}"'
            
            new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)
            
            if count > 0:
                with open(config_py_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return True
        except Exception as e:
            print(f"Error updating config.py path: {e}", file=sys.stderr)
            
        return False

    # ── Credential & Security Dialogs ──────────────────────
    def show_credential_dialog(self):
        """Show a dialog asking the user to create an initial account.
        Returns (username, email, password) or None if skipped."""
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Account")
        dialog.geometry("480x340")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.transient(self.root)
        
        # Center on parent
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (240)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (170)
        dialog.geometry(f"480x340+{x}+{y}")
        
        main = ttk.Frame(dialog, padding="20")
        main.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            main,
            text="Create Your Account",
            font=("Segoe UI", 13, "bold")
        ).pack(anchor=tk.W, pady=(0, 5))
        
        ttk.Label(
            main,
            text="Set up credentials for accessing your Personal Drive.\n"
                 "This account will be created when the server starts.",
            font=("Segoe UI", 9),
            foreground="gray",
            wraplength=420,
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=(0, 15))
        
        fields = ttk.Frame(main)
        fields.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(fields, text="Username:", font=("Segoe UI", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        username_var = tk.StringVar()
        username_entry = ttk.Entry(fields, textvariable=username_var, width=35)
        username_entry.grid(row=0, column=1, padx=(10, 0), pady=5, sticky=tk.EW)
        
        ttk.Label(fields, text="Email:", font=("Segoe UI", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        email_var = tk.StringVar()
        email_entry = ttk.Entry(fields, textvariable=email_var, width=35)
        email_entry.grid(row=1, column=1, padx=(10, 0), pady=5, sticky=tk.EW)
        
        ttk.Label(fields, text="Password:", font=("Segoe UI", 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        password_var = tk.StringVar()
        password_entry = ttk.Entry(fields, textvariable=password_var, width=35, show="●")
        password_entry.grid(row=2, column=1, padx=(10, 0), pady=5, sticky=tk.EW)
        
        # Show/hide password toggle
        show_pw_var = tk.BooleanVar(value=False)
        def toggle_pw():
            password_entry.config(show="" if show_pw_var.get() else "●")
        ttk.Checkbutton(fields, text="Show", variable=show_pw_var, command=toggle_pw).grid(
            row=2, column=2, padx=(5, 0), pady=5
        )
        
        fields.columnconfigure(1, weight=1)
        
        result = [None]
        
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        def on_skip():
            result[0] = "SKIP"
            dialog.destroy()
        
        def on_create():
            u = username_var.get().strip()
            e = email_var.get().strip()
            p = password_var.get().strip()
            if not u or not p:
                messagebox.showwarning(
                    "Missing Fields", 
                    "Username and Password are required.",
                    parent=dialog
                )
                return
            result[0] = (u, e, p)
            dialog.destroy()
        
        ttk.Button(btn_frame, text="Skip", command=on_skip).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Create Account", command=on_create).pack(side=tk.RIGHT)
        
        username_entry.focus_set()
        self.root.wait_window(dialog)
        return result[0]

    def show_security_warning(self):
        """Show a security warning when the user skips account creation.
        Returns True if user wants to continue anyway, False to go back."""
        
        dialog = tk.Toplevel(self.root)
        dialog.title("⚠ Security Warning")
        dialog.geometry("500x350")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.transient(self.root)
        
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (250)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (175)
        dialog.geometry(f"500x350+{x}+{y}")
        
        main = ttk.Frame(dialog, padding="20")
        main.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            main,
            text="⚠  Your Server Security Is at Risk",
            font=("Segoe UI", 13, "bold"),
            foreground="#cc6600"
        ).pack(anchor=tk.W, pady=(0, 12))
        
        warning_frame = ttk.Frame(main)
        warning_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        warning_text = tk.Text(
            warning_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            background=dialog.cget("background"),
            borderwidth=0,
            highlightthickness=0,
            height=10,
            cursor="arrow",
            padx=5, pady=5
        )
        warning_text.pack(fill=tk.BOTH, expand=True)
        
        reasons = (
            "Without user authentication, your server is vulnerable:\n\n"
            "🔓  Open Access — Anyone who discovers your server URL can "
            "upload, download, and delete files without restriction.\n\n"
            "👤  No Identity Tracking — There is no way to know who "
            "accessed, modified, or deleted your files.\n\n"
            "📂  Full Data Exposure — All files stored on the server "
            "are accessible to anyone on the network, including "
            "sensitive personal documents.\n\n"
            "🚫  No Revocation — Without accounts, you cannot block "
            "or revoke access for any specific user.\n\n"
            "It is strongly recommended to create at least one "
            "account to protect your data."
        )
        
        warning_text.insert("1.0", reasons)
        warning_text.config(state="disabled")
        
        result = [False]
        
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        def go_back():
            result[0] = False
            dialog.destroy()
            
        def continue_anyway():
            result[0] = True
            dialog.destroy()
        
        ttk.Button(btn_frame, text="Go Back (Recommended)", command=go_back).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Continue Anyway", command=continue_anyway).pack(side=tk.RIGHT)
        
        self.root.wait_window(dialog)
        return result[0]

    # ── Finish Handler ─────────────────────────────────────
    def handle_finish(self):
        dest = self.dest_var.get().strip()
        user_dir = self.user_var.get().strip()
        rl_path = self.rl_path_var.get().strip()
        
        if not dest or not user_dir:
            messagebox.showerror("Error", "Please fill in all storage folder paths.")
            return
            
        if self.rl_enable_var.get() and not rl_path:
            messagebox.showerror("Error", "Please enter a rate-limiter database folder path.")
            return

        expanded_dest = os.path.expandvars(os.path.expanduser(dest))
        expanded_user = os.path.expandvars(os.path.expanduser(user_dir))
        
        for folder in (expanded_dest, expanded_user):
            if not os.path.exists(folder):
                try:
                    os.makedirs(folder, exist_ok=True)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to create directory:\n{folder}\nError: {e}")
                    return

        if self.rl_enable_var.get():
            expanded_rl = os.path.expandvars(os.path.expanduser(rl_path))
            if not os.path.exists(expanded_rl):
                try:
                    os.makedirs(expanded_rl, exist_ok=True)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to create rate limiter directory:\n{expanded_rl}\nError: {e}")
                    return
        else:
            expanded_rl = rl_path

        # ── Account Creation Flow (when login is disabled) ──
        initial_username = ""
        initial_email = ""
        initial_password = ""

        if not self.login_var.get():
            cred_result = self.show_credential_dialog()
            
            if cred_result == "SKIP":
                # User skipped — show security warning
                should_continue = self.show_security_warning()
                if not should_continue:
                    return  # Go back to config page
            elif cred_result is None:
                # Dialog was closed (X button) — stay on config page
                return
            else:
                # User created credentials
                initial_username, initial_email, initial_password = cred_result

        # 1. Prepare server/project configuration properties
        server_data = {
            "DestinationFolder": expanded_dest,
            "Userfolder": expanded_user,
            "size": self.size_var.get(),
            "basic": self.basic_var.get(),
            "backend": "",
            "Allowlogin": self.login_var.get(),
            "jwtduration": self.jwt_var.get(),
            "ratelimiter": expanded_rl,
            "FrontendURL": self.cors_var.get().strip(),
            "URL": self.url_var.get().strip(),
            "Ratelimiter": self.rl_enable_var.get(),
            "Allowfreq": self.freq_var.get(),
            "Resettime": self.reset_var.get(),
            "cooldowntime": self.cooldown_var.get(),
            "host": self.host_var.get().strip(),
            "port": self.port_var.get(),
            "threads": self.threads_var.get(),
            "initial_username": initial_username,
            "initial_email": initial_email,
            "initial_password": initial_password
        }

        # 2. Retrieve setup/installer config properties from packageconfig.json
        package_data = {}
        try:
            package_data = {
                "dir": config.get("dir", ""),
                "python": config.get("python", ""),
                "ngrok": config.get("ngrok", ""),
                "ngrok_token": config.get("ngrok_token", "")
            }
        except Exception:
            pass

        # 3. Create combined dictionary holding ALL settings together
        config_json_path = os.path.normpath(os.path.join(self.workspace_dir, SERVER_CONFIG_FILE))
        combined_config = {}
        combined_config.update(server_data)
        combined_config.update(package_data)
        combined_config["config_path"] = config_json_path

        # 4. Save combined settings directly to workspace config.json
        try:
            with open(config_json_path, 'w', encoding='utf-8') as f:
                json.dump(combined_config, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save combined config file:\n{config_json_path}\nError: {e}")
            return

        # 5. Save combined settings directly to packageconfig.json
        try:
            config.set("config_path", config_json_path)
            for k, v in combined_config.items():
                config.set(k, v)
        except Exception as e:
            messagebox.showerror("Warning", f"Failed to save package config: {e}")

        # 6. Update PATH variable in pointed repository's config.py file
        config_py_path = os.path.join(self.workspace_dir, CODE_CONFIG_SCRIPT)
        if os.path.exists(config_py_path):
            updated = self.update_config_py_path(config_py_path, config_json_path)
            if not updated:
                print(f"Warning: Could not update config.py variable in {config_py_path}", file=sys.stderr)
        else:
            print(f"Warning: {CODE_CONFIG_SCRIPT} not found in {self.workspace_dir}", file=sys.stderr)

        print(json.dumps(combined_config))
        sys.stdout.flush()
        
        self.root.destroy()
        if self.on_complete:
            self.on_complete(combined_config)
        else:
            sys.exit(0)

    def on_close(self):
        self.root.destroy()
        if self.on_cancel:
            self.on_cancel()
        else:
            sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerConfigApp(root)
    root.mainloop()
