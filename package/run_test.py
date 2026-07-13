"""
Sequential runner — delegates to the unified main.py launcher.

This script exists for backward compatibility. The preferred
entry point is now main.py, which runs both GUIs seamlessly
in a single process.
"""
import subprocess
import sys
import os


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(script_dir, "main.py")

    result = subprocess.run(
        [sys.executable, main_script],
        cwd=script_dir
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
