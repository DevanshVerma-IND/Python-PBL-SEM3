import os
import sys
import threading
import subject
import attendance
import assignments
import section

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
            self.protocol("WM_DELETE_WINDOW", lambda: self._on_close())
            self._create_widgets()
            self._show_login()

        def _create_widgets(self):
                self.header_var = tk.StringVar(value="welcome")
                header = ttk.Label(self, textvariable=self.header_var, font=("Segoe UI", 16, "bold"))
                header.pack(fill=tk.X, padx=12, pady=8)
                menubar = tk.Menu(self)
                file_menu = tk.Menu(menubar, tearoff=0)
                file_menu.add_command(label="Open Data Folder", command=self._open_data_folder)
                file_menu.add_separator()
                file_menu.add_command(label="Exit", command=self._on_close)
                menubar.add_cascade(label="File", menu=file_menu)
                help_menu = tk.Menu(menubar, tearoff=0)
                help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "EduTrack — simplified education tracker"))
                menubar.add_cascade(label="Help", menu=help_menu)
                try:
                    self.config(menu=menubar)
                except Exception:
                    pass
                self.body_frame = ttk.Frame(self)
                self.body_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
                self.left_panel = ttk.Frame(self.body_frame)
                self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
                self.right_panel = ttk.Frame(self.body_frame)
                self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
                self.status_var = tk.StringVar(value="ready")
                status = ttk.Label(self, textvariable=self.status_var, anchor="w")
                status.pack(fill=tk.X, side=tk.BOTTOM, padx=8, pady=6)
                self.output_box = tk.Text(self.right_panel, wrap="word", state="normal")
                self.output_box.pack(fill=tk.BOTH, expand=True)

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
            ttk.Button(frm, text="forget password?", command=self._show_forget_password).grid(row=3, column=0, columnspan=2, pady=6)

        def _show_forget_password(self):
            messagebox.showinfo("Forget Password", "Please contact the administrator to reset your password or check your registered email for reset instructions.")

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

            # Determine role (admin, teacher, student)
            role = getattr(self, 'role', None)
            if not role and hasattr(self, 'user'):
                # Guess role from username (fallback)
                if self.user.lower().startswith('a'):
                    role = 'admin'
                elif self.user.lower().startswith('t'):
                    role = 'teacher'
                else:
                    role = 'student'
                self.role = role

            # Button definitions for each role
            admin_buttons = [
                ("Add Subject", lambda: self._run_and_output(subject.add_subject)),
                ("List Subjects", lambda: self._run_and_output(subject.list_subjects)),
                ("Create Section", lambda: self._run_and_output(section.create_section)),
                ("List Sections", lambda: self._run_and_output(section.list_sections)),
                ("Assign Section to Student", lambda: self._run_and_output(section.assign_section_from_list)),
                ("Assign Sections to Teacher", lambda: self._run_and_output(section.assign_section_to_teacher)),
                ("Set/Update Exam Dates", lambda: self._run_and_output(lambda: __import__('exam_date').setExamDatesAdmin())),
                ("View All Exam Dates", lambda: self._run_and_output(lambda: __import__('exam_date').viewAllExamDates())),
                ("View Section Assignments", lambda: self._run_and_output(section.view_section_assignments)),
            ]
            teacher_buttons = [
                ("View My Sections", lambda: self._run_and_output(lambda: self._append_output(section.view_my_sections(self.user)))),
                ("Mark Attendance", lambda: self._run_and_output(self._mark_attendance_dialog)),
                ("Update Attendance", lambda: self._run_and_output(self._update_attendance_dialog)),
                ("View Attendance Chart", lambda: self._run_and_output(lambda: attendance.view_attendance(teachername=self.user))),
                ("Add Topic Covered", lambda: self._run_and_output(lambda: __import__('topics').add_topic(self.user))),
                ("View Topics Covered", lambda: self._run_and_output(lambda: self._append_output("See topics in topics.json"))),
                ("View Submitted Assignments", lambda: self._run_and_output(lambda: assignments.view_assignments(self.user))),
            ]
            student_buttons = [
                ("View Dashboard", lambda: self._run_and_output(lambda: self._append_output(f"Dashboard for {self.user}"))),
                ("View My Exam Schedule", lambda: self._run_and_output(lambda: __import__('exam_date').viewStudentExamSchedule(self.user))),
                ("View My Attendance", lambda: self._run_and_output(lambda: attendance.view_attendance(student_roll=self.user))),
                ("View Attendance Summary", lambda: self._run_and_output(lambda: attendance.get_student_attendance_summary(self.user))),
                ("View Topics Covered", lambda: self._run_and_output(lambda: __import__('topics').view_topics_for_student(self.user))),
                ("Submit Assignment PDF", lambda: self._run_and_output(self._submit_assignment_dialog)),
            ]


            # Add a View Dashboard button for all roles
            ttk.Button(left, text="View Dashboard", width=28, command=lambda: self._append_output(f"Dashboard for {self.user} ({role})")).pack(pady=4)

            # Add role-specific buttons
            if role == 'admin':
                for label, cmd in admin_buttons:
                    ttk.Button(left, text=label, width=28, command=cmd).pack(pady=4)
            elif role == 'teacher':
                for label, cmd in teacher_buttons:
                    ttk.Button(left, text=label, width=28, command=cmd).pack(pady=4)
            else:
                for label, cmd in student_buttons:
                    ttk.Button(left, text=label, width=28, command=cmd).pack(pady=4)

            # Common buttons
            ttk.Button(left, text="Open Data Folder", width=28, command=self._open_data_folder).pack(pady=4)
            ttk.Button(left, text="Logout", width=28, command=self._show_login).pack(pady=8)
            ttk.Button(left, text="Exit", width=28, command=self._on_close).pack()

            self.output_box = tk.Text(right, wrap="word")
            self.output_box.pack(fill=tk.BOTH, expand=True)

        def _run_and_output(self, func):
            """Run a function and append its output to the output box."""
            import io
            import contextlib
            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf):
                    func()
            except Exception as e:
                self._append_output(f"error: {e}")
            out = buf.getvalue()
            if out.strip():
                self._append_output(out.strip())

        def _mark_attendance_dialog(self):
            roll = simpledialog.askstring("Mark Attendance", "Enter student roll number:")
            subject_code = simpledialog.askstring("Mark Attendance", "Enter subject code:")
            if not roll or not subject_code:
                self._append_output("Roll number and subject code required.")
                return
            attendance.mark_attendance(self.user, roll, subject_code)

        def _update_attendance_dialog(self):
            roll = simpledialog.askstring("Update Attendance", "Enter student roll number:")
            subject_code = simpledialog.askstring("Update Attendance", "Enter subject code:")
            if not roll or not subject_code:
                self._append_output("Roll number and subject code required.")
                return
            attendance.update_attendance(self.user, roll, subject_code)

        def _submit_assignment_dialog(self):
            pdf_path = filedialog.askopenfilename(title="Select PDF to submit")
            if not pdf_path:
                self._append_output("No file selected.")
                return
            assignments.submit_assignment(self.user, pdf_path)

        def _append_output(self, text):
            try:
                import threading as _thr
                if _thr.current_thread().name != 'MainThread':
                    self.after(0, lambda: self._append_output(text))
                    return
            except Exception:
                pass
            try:
                self.output_box.insert("end", str(text) + "\n")
                self.output_box.see("end")
            except Exception:
                pass

        def _set_status(self, text):
            try:
                import threading as _thr
                if _thr.current_thread().name != 'MainThread':
                    self.after(0, lambda: self._set_status(text))
                    return
            except Exception:
                pass
            try:
                self.status_var.set(text)
            except Exception:
                pass

        def _on_subjects(self):
            self.status_var.set("loading subjects")
            def job():
                try:
                    subjects = subject.list_subjects()
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
            choice = simpledialog.askstring("attendance", "enter option: view by roll / update")
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
                teacher = simpledialog.askstring("attendance", "enter teacher username")
                if not teacher:
                    return
                roll = simpledialog.askstring("attendance", "enter student roll")
                if not roll:
                    return
                subject_code = simpledialog.askstring("attendance", "enter subject code or name")
                if not subject_code:
                    return
                def job2():
                    try:
                        attendance.update_attendance(teacher, roll, subject_code)
                        self._append_output(f"updated attendance for {roll} - {subject_code}")
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
                    secs = section.view_my_sections(self.user)
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
