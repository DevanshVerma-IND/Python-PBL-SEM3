import os
import sys
import subprocess

this_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(this_dir)

def main():
   
    python_executable = sys.executable or "python3"
    gui_path = os.path.join(this_dir, "gui.py")
   
    try:
        rc = subprocess.call([python_executable, "-c", "import tkinter"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError as e:
        print("Failed to check for tkinter availability:", e)
        return 1

    if rc != 0:
        # tkinter not importable — run CLI instead
        cli_path = os.path.join(this_dir, "main.py")
        print("Tkinter not available — launching CLI instead.")
        try:
            return subprocess.call([python_executable, cli_path])
        except OSError as e:
            print("Failed to launch CLI process:", e)
            return 1

    try:
        gui_rc = subprocess.call([python_executable, gui_path])
    except OSError as e:
        print("Failed to launch GUI process:", e)
        return 1

    if gui_rc == 0:
        return 0

    print("GUI exited unexpectedly (code {}). Launching CLI instead.".format(gui_rc))
    cli_path = os.path.join(this_dir, "main.py")
    try:
        return subprocess.call([python_executable, cli_path])
    except OSError as e:
        print("Failed to launch CLI process:", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
