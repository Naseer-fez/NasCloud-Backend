"""
PersonalDrive — Unified Setup & Configuration Launcher

Seamlessly chains the Setup Wizard (Steps 1-3) into the
Server Configuration GUI in a single process. This is the
entry point for both development runs and the .exe build.
"""
import sys
import tkinter as tk

try:
    from pckconfig import config, APP_DISPLAY_NAME
    from GUIsetup import ProgramSetupApp
    from GUIconfig import ServerConfigApp
except ImportError:
    from package.pckconfig import config, APP_DISPLAY_NAME
    from package.GUIsetup import ProgramSetupApp
    from package.GUIconfig import ServerConfigApp


def main():
    setup_completed = False

    # ── Phase 1: Setup Wizard ──────────────────────────────
    def on_setup_complete(result):
        nonlocal setup_completed
        setup_completed = True
        # Reload config so GUIconfig sees the freshly saved values
        config.reload()

    def on_setup_cancel():
        pass  # Just let mainloop exit naturally

    setup_root = tk.Tk()
    ProgramSetupApp(setup_root, on_complete=on_setup_complete, on_cancel=on_setup_cancel)
    setup_root.mainloop()

    if not setup_completed:
        print("Setup was cancelled by the user.")
        sys.exit(1)

    # ── Phase 2: Server Configuration ──────────────────────
    config_completed = False

    def on_config_complete(combined_config):
        nonlocal config_completed
        config_completed = True

    def on_config_cancel():
        pass

    config_root = tk.Tk()
    ServerConfigApp(config_root, on_complete=on_config_complete, on_cancel=on_config_cancel)
    config_root.mainloop()

    if config_completed:
        print(f"\n{APP_DISPLAY_NAME} setup and configuration complete!")
    else:
        print("Configuration was cancelled by the user.")
        sys.exit(1)


if __name__ == "__main__":
    main()
