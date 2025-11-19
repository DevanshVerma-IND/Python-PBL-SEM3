import os
import sys
import threading
import contextlib
import io
import subject
import section
import attendance
import assignments
import topics
import login
import exam_date

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, simpledialog, filedialog
    tk_available = True
except Exception as tk_err:
    tk = ttk = messagebox = simpledialog = filedialog = None
    tk_available = False
    tk_import_error = tk_err

def projectroot():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def path(name: str) -> str:
    return os.path.join(projectroot(), name)

def runbg(fn, ondone=None, onerr=None):
    def wrapper():
        try:
            fn()
            if ondone:
                ondone()
        except Exception as e:
            if onerr:
                onerr(e)
    t = threading.Thread(target=wrapper, daemon=True)
    t.start()
    return t

if tk_available:

    class edutrackapp(tk.Tk):
        def __init__(self):
            super().__init__()
            self.title("EduTrack")
            self.geometry("980x600")
            self.users = None
            self.createchrome()
            self.showlogin()

        def createchrome(self):
            self.headervar = tk.StringVar(value="Welcome")
            header = ttk.Label(self, textvariable=self.headervar, font=("Segoe UI", 16, "bold"))
            header.pack(fill=tk.X, padx=12, pady=8)
            menubar = tk.Menu(self)
            filemenu = tk.Menu(menubar, tearoff=0)
            filemenu.add_command(label="Open Data Folder", command=self.opendatafolder)
            filemenu.add_separator()
            filemenu.add_command(label="Exit", command=self.onclose)
            menubar.add_cascade(label="File", menu=filemenu)
            helpmenu = tk.Menu(menubar, tearoff=0)
            helpmenu.add_command(label="About", command=lambda: messagebox.showinfo("About", "EduTrack — simplified education tracker"))
            menubar.add_cascade(label="Help", menu=helpmenu)
            try:
                self.config(menu=menubar)
            except Exception:
                pass
            self.body = ttk.Frame(self)
            self.body.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
            self.statusvar = tk.StringVar(value="Ready")
            status = ttk.Label(self, textvariable=self.statusvar, anchor="w")
            status.pack(fill=tk.X, side=tk.BOTTOM, padx=8, pady=6)

        def clearbody(self):
            for w in list(self.body.winfo_children()):
                w.destroy()

        def showlogin(self):
            self.headervar.set("Login")
            self.statusvar.set("Login screen")
            self.clearbody()
            frm = ttk.Frame(self.body)
            frm.pack(pady=20)
            ttk.Label(frm, text="Username").grid(row=0, column=0, sticky="w", pady=6)
            ttk.Label(frm, text="Password").grid(row=1, column=0, sticky="w", pady=6)
            self.usernamevar = tk.StringVar()
            self.passwordvar = tk.StringVar()
            userentry = ttk.Entry(frm, textvariable=self.usernamevar)
            pwentry = ttk.Entry(frm, textvariable=self.passwordvar, show="*")
            userentry.grid(row=0, column=1, padx=8)
            pwentry.grid(row=1, column=1, padx=8)
            btnrow = ttk.Frame(frm)
            btnrow.grid(row=2, column=0, columnspan=2, pady=12)
            ttk.Button(btnrow, text="Login", command=self.onlogin).pack(side=tk.LEFT, padx=6)
            ttk.Button(btnrow, text="Exit", command=self.onclose).pack(side=tk.LEFT, padx=6)
            ttk.Button(frm, text="Forgot password?", command=lambda: messagebox.showinfo("Forgot Password", "Use CLI 'Forgot password' in main.py or contact admin.")).grid(row=3, column=0, columnspan=2, pady=6)
            try:
                self.users = login.load_users()
            except Exception:
                self.users = None

        def onlogin(self):
            uname = (self.usernamevar.get() or "").strip()
            pwd = (self.passwordvar.get() or "").strip()
            if not uname or not pwd:
                messagebox.showerror("Login failed", "Username and password are required.")
                return
            users = self.users or login.load_users()
            uobj = users.find(uname) if users else None
            if not uobj:
                messagebox.showerror("Login failed", "User not found.")
                return
            try:
                ok = login.hmac.compare_digest(login.make_hash(pwd, uobj.salt), uobj.pwd_hash)
            except Exception:
                ok = False
            if not ok:
                messagebox.showerror("Login failed", "Wrong password.")
                return
            self.user = uname
            self.role = uobj.role
            self.roll = subject.lookupRollNumber(uname, self.role)
            self.headervar.set(f"User: {self.user} ({self.role})")
            self.showmainmenu()

        def showmainmenu(self):
            self.headervar.set(f"Dashboard — {getattr(self, 'user', 'guest')}")
            self.statusvar.set("Dashboard")
            self.clearbody()
            container = ttk.Frame(self.body)
            container.pack(fill=tk.BOTH, expand=True)
            leftspace = ttk.Frame(container)
            leftspace.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            centercol = ttk.Frame(container)
            centercol.pack(side=tk.LEFT)
            rightpanel = ttk.Frame(container)
            rightpanel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=8, pady=8)
            panel = ttk.Frame(centercol)
            panel.pack(padx=8, pady=8)
            ttk.Button(panel, text="View Dashboard", width=28, command=self.viewdashboard).pack(pady=4)
            ttk.Button(panel, text="Attendance Graph", width=28, command=self.showattendancegraph).pack(pady=4)
            if self.role == "admin":
                self.addadmin(panel)
            elif self.role == "teacher":
                self.addteacher(panel)
            else:
                self.addstudent(panel)
            ttk.Button(panel, text="Open Data Folder", width=28, command=self.opendatafolder).pack(pady=4)
            ttk.Button(panel, text="Logout", width=28, command=self.showlogin).pack(pady=8)
            ttk.Button(panel, text="Exit", width=28, command=self.onclose).pack()
            self.outputbox = tk.Text(rightpanel, wrap="word")
            self.outputbox.pack(fill=tk.BOTH, expand=True)

        def viewdashboard(self):
            roll = self.ensureroll()
            sec = section.getSectionForRoll(roll) if roll else "Not assigned"
            self.appendoutput(f"Dashboard\nUser: {self.user} ({self.role})\nRoll: {roll or 'N/A'}\nSection: {sec}")

        def ensureroll(self):
            if getattr(self, "roll", None):
                return self.roll
            created = subject.getRollNumber(self.user, self.role, create_if_missing=True)
            self.roll = created
            return created

        def addadmin(self, parent):
            btns = [
                ("Add Subject", lambda: self.runandcapture(subject.addSubject)),
                ("List Subjects", lambda: self.runandcapture(subject.listSubjects)),
                ("Create Section", lambda: self.runandcapture(section.createSection)),
                ("List Sections", lambda: self.runandcapture(section.listSections)),
                ("Assign Section to Student", lambda: self.runandcapture(section.assignSectionFromList)),
                ("Assign Sections to Teacher", lambda: self.runandcapture(section.assignSectionToTeacher)),
                ("Set/Update Exam Dates", lambda: self.runandcapture(exam_date.setExamDatesAdmin)),
                ("View All Exam Dates", lambda: self.runandcapture(exam_date.viewAllExamDates)),
                ("View Section Assignments", lambda: self.runandcapture(section.viewSectionAssignments)),
            ]
            for label, cmd in btns:
                ttk.Button(parent, text=label, width=28, command=cmd).pack(pady=4)

        def addteacher(self, parent):
            ttk.Button(parent, text="View My Sections", width=28, command=lambda: self.runandcapture(lambda: section.viewMySections(self.user))).pack(pady=4)
            ttk.Button(parent, text="Mark Attendance", width=28, command=self.markattendancedialog).pack(pady=4)
            ttk.Button(parent, text="Update Attendance", width=28, command=self.updateattendancedialog).pack(pady=4)
            ttk.Button(parent, text="View Attendance Chart", width=28, command=lambda: self.runandcapture(lambda: attendance.view_attendance(teachername=self.user))).pack(pady=4)
            ttk.Button(parent, text="Add Topic Covered", width=28, command=lambda: self.runandcapture(lambda: topics.add_topic(self.user))).pack(pady=4)
            ttk.Button(parent, text="View Topics Covered", width=28, command=self.viewmytopics).pack(pady=4)
            ttk.Button(parent, text="View Submitted Assignments", width=28, command=lambda: self.runandcapture(lambda: assignments.view_assignments(self.user))).pack(pady=4)

        def addstudent(self, parent):
            ttk.Button(parent, text="View My Exam Schedule", width=28, command=self.viewmyexamschedule).pack(pady=4)
            ttk.Button(parent, text="View My Attendance", width=28, command=self.viewmyattendance).pack(pady=4)
            ttk.Button(parent, text="View Attendance Summary", width=28, command=self.viewmyattendancesummary).pack(pady=4)
            ttk.Button(parent, text="View Topics Covered", width=28, command=self.viewmytopicsasstudent).pack(pady=4)
            ttk.Button(parent, text="Submit Assignment PDF", width=28, command=self.submitassignmentdialog).pack(pady=4)

        def runandcapture(self, func):
            buf = io.StringIO()
            def job():
                try:
                    with contextlib.redirect_stdout(buf):
                        func()
                except Exception as e:
                    self.appendoutput(f"Error: {e}")
            def done():
                out = buf.getvalue()
                if out.strip():
                    self.appendoutput(out.strip())
            runbg(job, ondone=done)

        def appendoutput(self, text):
            try:
                self.outputbox.insert("end", str(text) + "\n")
                self.outputbox.see("end")
            except Exception:
                pass

        def setstatus(self, text):
            try:
                self.statusvar.set(text)
            except Exception:
                pass

        def markattendancedialog(self):
            roll = simpledialog.askstring("Mark Attendance", "Enter student roll number:")
            code = simpledialog.askstring("Mark Attendance", "Enter subject code:")
            if not roll or not code:
                self.appendoutput("Roll number and subject code required.")
                return
            self.runandcapture(lambda: attendance.mark_attendance(self.user, roll, code))

        def updateattendancedialog(self):
            roll = simpledialog.askstring("Update Attendance", "Enter student roll number:")
            code = simpledialog.askstring("Update Attendance", "Enter subject code:")
            if not roll or not code:
                self.appendoutput("Roll number and subject code required.")
                return
            self.runandcapture(lambda: attendance.update_attendance(self.user, roll, code))

        def submitassignmentdialog(self):
            roll = self.ensureroll()
            if not roll:
                self.appendoutput("No roll number found. Ask admin to create your account.")
                return
            pdfpath = filedialog.askopenfilename(title="Select PDF to submit")
            if not pdfpath:
                self.appendoutput("No file selected.")
                return
            self.runandcapture(lambda: assignments.submit_assignment(roll, pdfpath))

        def viewmyexamschedule(self):
            roll = self.ensureroll()
            sec = section.getSectionForRoll(roll) if roll else "Not assigned"
            if sec == "Not assigned":
                self.appendoutput("Section not assigned.")
                return
            self.runandcapture(lambda: exam_date.viewSectionExamDates(sec))

        def viewmyattendance(self):
            roll = self.ensureroll()
            if not roll:
                self.appendoutput("No roll number found.")
                return
            self.runandcapture(lambda: attendance.view_attendance(student_roll=roll))

        def viewmyattendancesummary(self):
            roll = self.ensureroll()
            if not roll:
                self.appendoutput("No roll number found.")
                return
            self.runandcapture(lambda: attendance.get_student_attendance_summary(roll))

        def viewmytopicsasstudent(self):
            roll = self.ensureroll()
            if not roll:
                self.appendoutput("No roll number found.")
                return
            self.runandcapture(lambda: topics.view_topics_for_student(roll))

        def viewmytopics(self):
            temap = topics.load_teacher_sections()
            secs = temap.get(self.user, [])
            if not secs:
                self.appendoutput("No sections assigned to you.")
                return
            data = topics.load_json(topics.TOPICS_FILE)
            anyprint = False
            for sec in secs:
                entries = data.get(sec) or []
                if entries:
                    self.appendoutput(f"\nTopics for section {sec}:")
                    for i, t in enumerate(entries, 1):
                        self.appendoutput(f" {i}. {t.get('topic')} (by {t.get('teacher')} on {t.get('date')})")
                    anyprint = True
            if not anyprint:
                self.appendoutput("No topics recorded yet for your sections.")

        def showattendancegraph(self):
            try:
                import json
                from collections import defaultdict
                p = path("attendance_master.json")
                with open(p, "r", encoding="utf-8") as fh:
                    am = json.load(fh)
                records = am.get("attendance_records", {})
                agg = defaultdict(list)
                for info in records.values():
                    subs = info.get("subjects", {})
                    for s in subs.values():
                        name = s.get("subject_name") or ""
                        try:
                            perc = float(s.get("attendance_percentage", 0.0) or 0.0)
                        except Exception:
                            perc = 0.0
                        if name:
                            agg[name].append(perc)
                if not agg:
                    self.appendoutput("No attendance data to plot.")
                    return
                labels = list(agg.keys())
                values = [sum(agg[l]) / len(agg[l]) if len(agg[l]) else 0.0 for l in labels]
            except Exception as e:
                self.appendoutput(f"Error preparing attendance data: {e}")
                return
            try:
                import matplotlib
                matplotlib.use('TkAgg')
                import matplotlib.pyplot as plt
                from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
            except Exception:
                self.appendoutput("matplotlib is required to show graphs. Install with: pip install matplotlib")
                return
            try:
                plt.style.use('seaborn-whitegrid')
                cmap = plt.get_cmap('tab10')
                colors = [cmap(i % cmap.N) for i in range(len(labels))]
                pairs = sorted(zip(labels, values), key=lambda x: x[1], reverse=True)
                labels_sorted = [p[0] for p in pairs]
                values_sorted = [p[1] for p in pairs]
                many = len(labels_sorted) > 12
                fig_height = 5 if not many else max(6, 0.35 * len(labels_sorted))
                fig, ax = plt.subplots(figsize=(10, fig_height), facecolor='white')
                fig.patch.set_facecolor('white')
                if many:
                    y_pos = list(range(len(labels_sorted)))
                    bars = ax.barh(y_pos, values_sorted, color=colors)
                    ax.set_yticks(y_pos)
                    ax.set_yticklabels(labels_sorted, fontsize=10)
                    ax.set_xlabel('Average Attendance (%)', fontsize=12)
                    ax.set_xlim(0, 100)
                    for b, v in zip(bars, values_sorted):
                        ax.text(b.get_width() + 1, b.get_y() + b.get_height()/2, f"{v:.1f}%", va='center', fontsize=9)
                else:
                    bars = ax.bar(labels_sorted, values_sorted, color=colors)
                    ax.set_ylabel('Average Attendance (%)', fontsize=12)
                    ax.set_ylim(0, 100)
                    plt.setp(ax.get_xticklabels(), rotation=35, ha='right', fontsize=10)
                    for b, v in zip(bars, values_sorted):
                        ax.text(b.get_x() + b.get_width()/2, v + 1, f"{v:.1f}%", ha='center', va='bottom', fontsize=9)
                ax.grid(axis='y', color='#f0f0f0')
                ax.set_title('Average Attendance per Subject', fontsize=14, weight='bold')
                fig.tight_layout()
                if all(v == 0 for v in values_sorted):
                    ax.text(0.5, 0.5, 'All attendance percentages are 0\n(try marking attendance first)', ha='center', va='center', transform=ax.transAxes, fontsize=12, color='#666666')
                win = tk.Toplevel(self)
                win.title('Attendance Graph')
                canvas = FigureCanvasTkAgg(fig, master=win)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                try:
                    toolbar = NavigationToolbar2Tk(canvas, win)
                    toolbar.update()
                    toolbar.pack(side=tk.BOTTOM, fill=tk.X)
                except Exception:
                    pass
            except Exception as e:
                self.appendoutput(f"Error rendering graph: {e}")

        def opendatafolder(self):
            folder = projectroot()
            try:
                if sys.platform.startswith("win"):
                    os.startfile(folder)  
                elif sys.platform == "darwin":
                    os.system(f'open "{folder}"')
                else:
                    os.system(f'xdg-open "{folder}"')
            except Exception:
                self.appendoutput(f"Data folder: {folder}")

        def onclose(self):
            try:
                self.destroy()
            except Exception:
                pass

else:
    class edutrackapp:
        def __init__(self):
            raise RuntimeError(
                "Tkinter failed to initialize or is not available.\n"
                f"Original error: {repr(tk_import_error)}\n\n"
                "If you don't need the GUI, run CLI: python main.py"
            )

if __name__ == "__main__":
    app = edutrackapp()
    if tk_available:
        app.mainloop()
