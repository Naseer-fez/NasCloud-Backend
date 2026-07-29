import sys
import subprocess
import os
import time
import shutil

# Ensure pywinauto is installed
try:
    from pywinauto import Application, keyboard
except ImportError:
    print("Installing pywinauto...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pywinauto"])
    from pywinauto import Application, keyboard

TEST_WORKSPACE = r"D:\TestWorkspace"
EXE_PATH = r"d:\CODE\PYTHON\CODE\Projects\Personaldrive\package\dist\NasCloud.exe"
LOCAL_APP_DATA = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or os.path.expanduser("~")
BIN_DIR = os.path.join(LOCAL_APP_DATA, "NasCloud", "bin")

def main():
    print("Killing any existing NasCloud processes...")
    os.system("taskkill /f /im NasCloud.exe >nul 2>&1")
    time.sleep(2)
    
    if not os.path.exists(EXE_PATH):
        print(f"Error: {EXE_PATH} not found.")
        sys.exit(1)

    print("Cleaning up previous test workspace...")
    if os.path.exists(TEST_WORKSPACE):
        shutil.rmtree(TEST_WORKSPACE, ignore_errors=True)
    os.makedirs(TEST_WORKSPACE, exist_ok=True)

    print("Cleaning up previous bin directory...")
    if os.path.exists(BIN_DIR):
        try:
            shutil.rmtree(BIN_DIR, ignore_errors=True)
        except Exception as e:
            print(f"Could not remove BIN_DIR: {e}")

    print("Launching NasCloud...")
    # PyInstaller one-file executables spawn a child process.
    # It's better to launch it via subprocess and then connect to the window.
    subprocess.Popen([EXE_PATH])
    
    app = Application(backend="uia")
    try:
        # Wait up to 45 seconds for the setup window to appear and connect to its process
        app.connect(title_re=".*NasCloud Setup.*", timeout=45)
        dlg = app.window(title_re=".*NasCloud Setup.*")
        dlg.wait("ready", timeout=30)
        print("Setup window detected.")
    
        # Find the entry to set the workspace
        # We will type the path into the window, usually the entry is the first Edit control
        edit = dlg.child_window(control_type="Edit", found_index=0)
        edit.set_text(TEST_WORKSPACE)
        
        # Check "Extract Bundled Python" and "Extract Bundled Cloudflare"
        checkboxes = dlg.children(control_type="CheckBox")
        for cb in checkboxes:
            if "Extract Bundled" in cb.window_text():
                if cb.get_toggle_state() == 0:
                    cb.toggle()
        
        # Click Next
        next_btn = dlg.child_window(title="Next", control_type="Button")
        next_btn.click()
        
        print("Waiting for extraction...")
        # Since extraction can take time, we wait for the next screen
        time.sleep(15) 
        
        # In case there's another "Next" or "Finish" or "Continue"
        try:
            # We skip Ngrok auth by clicking Next or Finish
            finish_btn = dlg.child_window(title_re=".*Finish.*|.*Next.*", control_type="Button", found_index=0)
            if finish_btn.exists():
                finish_btn.click()
                time.sleep(5)
        except Exception:
            pass

        print("Checking if binaries were extracted...")
        python_exe = os.path.join(BIN_DIR, "python.exe")
        cf_exe = os.path.join(BIN_DIR, "cloudflared.exe")
        
        if not os.path.exists(python_exe):
            print(f"Error: Python was not extracted to {python_exe}")
            sys.exit(1)
            
        if not os.path.exists(cf_exe):
            print(f"Error: Cloudflare was not extracted to {cf_exe}")
            sys.exit(1)
            
        print("Binaries verified.")
        
        # Wait for transition to Server Window
        server_win = app.window(title_re=".*Server.*")
        server_win.wait("ready", timeout=30)
        print("Server Launcher window detected.")
        
        # Click Start Server
        start_btn = server_win.child_window(title_re=".*Start Server.*", control_type="Button")
        start_btn.click()
        
        print("Server starting... waiting for Cloudflare tunnel (up to 40 seconds)")
        
        # We need to wait and check if the public URL entry updates.
        # It's an Edit control
        start_time = time.time()
        url_found = False
        while time.time() - start_time < 40:
            edits = server_win.children(control_type="Edit")
            for e in edits:
                text = e.window_text()
                if "trycloudflare.com" in text:
                    print(f"Tunnel URL obtained: {text}")
                    url_found = True
                    break
            if url_found:
                break
            time.sleep(2)
            
        if not url_found:
            print("Error: Cloudflare tunnel URL was not obtained within 40 seconds.")
            sys.exit(1)
            
        # Check logs for module not found
        # Usually text is in a Document control in Tkinter UI Automation
        docs = server_win.children(control_type="Document")
        log_text = ""
        for d in docs:
            log_text += d.window_text() + "\n"
            
        if "ModuleNotFoundError: No module named 'waitress'" in log_text:
            print("Error: Waitress module not found in server log.")
            sys.exit(1)
            
        print("No module errors detected in log.")
        
        # Stop Server
        stop_btn = server_win.child_window(title_re=".*Stop Server.*", control_type="Button")
        stop_btn.click()
        time.sleep(3)
        
        # Clean shutdown check
        print("Test passed successfully.")
        
    except Exception as e:
        print(f"Test failed with exception: {e}")
        try:
            print("Control identifiers for debugging:")
            app.window().print_control_identifiers()
        except:
            pass
        sys.exit(1)
    finally:
        try:
            app.kill()
        except:
            # Fallback if kill fails
            os.system('taskkill /f /im NasCloud.exe')
        
        if os.path.exists(TEST_WORKSPACE):
            try:
                shutil.rmtree(TEST_WORKSPACE, ignore_errors=True)
            except:
                pass

if __name__ == "__main__":
    main()
