import os
import sys
import threading
import subject
import attendance
import assignments
import section

# tkinter may not be available or may crash on some macOS/Python builds.
# Try importing it and fall back to a clear error at runtime if unavailable.
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, simpledialog, filedialog
    _TK_AVAILABLE = True
except Exception as _tk_err:
    tk = None
    ttk = None
    messagebox = None
    simpledialog = None
    filedialog = None
    _TK_AVAILABLE = False
    _TK_IMPORT_ERROR = _tk_err

this_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(this_dir)

if _TK_AVAILABLE:
    class app(tk.Tk):
        def __init__(self):
            super().__init__()
            self.title("edutrack")
            self.geometry("800x520")
            self.protocol("WM_DELETE_WINDOW", self._on_close)
            self._create_widgets()
            self._show_login()

    def _create_widgets(self):
        self.header_var = tk.StringVar(value="welcome")
        header = ttk.Label(self, textvariable=self.header_var, font=("Segoe UI", 16))
        header.pack(fill=tk.X, padx=12, pady=8)
        self.body_frame = ttk.Frame(self)
        self.body_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
        self.status_var = tk.StringVar(value="ready")
        status = ttk.Label(self, textvariable=self.status_var, anchor="w")
        status.pack(fill=tk.X, side=tk.BOTTOM, padx=8, pady=6)

    def _clear_body(self):
        for w in list(self.body_frame.winfo_children()):
            w.destroy()

    def _show_login(self):
        self.header_var.set("login")
        self.status_var.set("login screen")
        self._clear_body()
        frm = ttk.Frame(self.body_frame)
        frm.pack(pady=20)
        ttk.Label(frm, text="username").grid(row=0, column=0, sticky="w", pady=6)
        ttk.Label(frm, text="password").grid(row=1, column=0, sticky="w", pady=6)
        user_var = tk.StringVar()
        pwd_var = tk.StringVar()
        user_entry = ttk.Entry(frm, textvariable=user_var)
        pwd_entry = ttk.Entry(frm, textvariable=pwd_var, show="*")
        user_entry.grid(row=0, column=1, padx=8)
        pwd_entry.grid(row=1, column=1, padx=8)
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=12)
        ttk.Button(btn_frame, text="login", command=lambda: self._on_login(user_var.get().strip(), pwd_var.get().strip())).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text="exit", command=self._on_close).pack(side=tk.LEFT, padx=6)

    def _on_login(self, username, password):
        self.user = username or "guest"
        self.header_var.set(f"user: {self.user}")
        self._show_main_menu()

    def _show_main_menu(self):
        self.header_var.set(f"dashboard - {self.user}")
        self.status_var.set("dashboard")
        self._clear_body()
        frm = ttk.Frame(self.body_frame)
        frm.pack(fill=tk.BOTH, expand=True)
        left = ttk.Frame(frm)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=8)
        right = ttk.Frame(frm)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=8, pady=8)
        ttk.Button(left, text="subjects", width=20, command=self._on_subjects).pack(pady=6)
        ttk.Button(left, text="attendance", width=20, command=self._on_attendance).pack(pady=6)
        ttk.Button(left, text="assignments", width=20, command=self._on_assignments).pack(pady=6)
        ttk.Button(left, text="sections", width=20, command=self._on_sections).pack(pady=6)
        ttk.Button(left, text="open data folder", width=20, command=self._open_data_folder).pack(pady=6)
        ttk.Button(left, text="logout", width=20, command=self._show_login).pack(pady=16)
        ttk.Button(left, text="exit", width=20, command=self._on_close).pack()
        self.output_box = tk.Text(right, wrap="word")
        self.output_box.pack(fill=tk.BOTH, expand=True)

    def _append_output(self, text):
        self.output_box.insert("end", str(text) + "\n")
        self.output_box.see("end")

    def _on_subjects(self):
        self.status_var.set("loading subjects")
        def job():
            try:
                subjects = subject.listSubjects()
                if not subjects:
                    self._append_output("no subjects found")
                    return
                self._append_output("subjects:")
                for s in subjects:
                    name = s.get("name") if isinstance(s, dict) else str(s)
                    code = s.get("code","") if isinstance(s, dict) else ""
                    self._append_output(f"- {name} ({code})")
            except Exception as e:
                self._append_output(f"error: {e}")
        threading.Thread(target=job, daemon=True).start()

    def _on_attendance(self):
        choices = ["view by roll", "update by file"]
        choice = simpledialog.askstring("attendance", "enter option: view by roll / update by file")
        if not choice:
            return
        if choice.lower().startswith("view"):
            roll = simpledialog.askstring("attendance", "enter student roll")
            if not roll:
                return
            def job():
                try:
                    attendance.view_attendance(student_roll=roll)
                    self._append_output(f"viewed attendance for {roll}")
                except Exception as e:
                    self._append_output(f"error: {e}")
            threading.Thread(target=job, daemon=True).start()
        else:
            path = filedialog.askopenfilename(title="select attendance json or csv")
            if not path:
                return
            def job2():
                try:
                    attendance.update_attendance(path)
                    self._append_output(f"updated attendance from {path}")
                except Exception as e:
                    self._append_output(f"error: {e}")
            threading.Thread(target=job2, daemon=True).start()

    def _on_assignments(self):
        choice = simpledialog.askstring("assignments", "enter option: submit / view")
        if not choice:
            return
        if choice.lower().startswith("submit"):
            sid = simpledialog.askstring("submit", "enter student id")
            if not sid:
                return
            path = filedialog.askopenfilename(title="select pdf")
            if not path:
                return
            def job():
                try:
                    assignments.submit_assignment(sid, path)
                    self._append_output(f"submitted assignment for {sid}")
                except Exception as e:
                    self._append_output(f"error: {e}")
            threading.Thread(target=job, daemon=True).start()
        else:
            tname = simpledialog.askstring("view", "enter teacher name")
            if not tname:
                return
            def job2():
                try:
                    assignments.view_assignments(tname)
                    self._append_output(f"viewed assignments for {tname}")
                except Exception as e:
                    self._append_output(f"error: {e}")
            threading.Thread(target=job2, daemon=True).start()

    def _on_sections(self):
        def job():
            try:
                secs = section.viewMySections(self.user)
                self._append_output(f"sections for {self.user}: {secs}")
            except Exception as e:
                self._append_output(f"error: {e}")
        threading.Thread(target=job, daemon=True).start()

    def _open_data_folder(self):
        folder = this_dir
        if sys.platform.startswith("win"):
            os.startfile(folder)
        elif sys.platform == "darwin":
            os.system(f"open \"{folder}\"")
        else:
            os.system(f"xdg-open \"{folder}\"")

    def _on_close(self):
        try:
            self.destroy()
        except:
            pass

else:
    class app:
        def __init__(self):
            raise RuntimeError(
                "Tkinter is not available or failed to initialize on this system. "
                "Original error: {}\n\nOn macOS, install Python from python.org or ensure Tcl/Tk is installed and compatible. "
                "If you don't need the GUI, run command-line scripts directly.".format(repr(_TK_IMPORT_ERROR))
            )

if __name__ == "__main__":
    a = app()
    a.mainloop()
