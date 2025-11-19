import os
import sys
import subprocess

this_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(this_dir)

def main():
    """Launch the GUI in a separate Python process to isolate native Tk failures.

    This avoids a C-level abort in Tk from killing the launcher process.
    """
    python_executable = sys.executable or "python3"
    gui_path = os.path.join(this_dir, "gui.py")
    try:
        return subprocess.call([python_executable, gui_path])
    except OSError as e:
        print("Failed to launch GUI process:", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
