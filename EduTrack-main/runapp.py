import os
import sys

this_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(this_dir)

def main():
    from gui import app as app_class
    application = app_class()
    application.mainloop()

if __name__ == "__main__":
    main()
