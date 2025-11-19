import os
import sys
import threading
import contextlib
import io
import builtins
from datetime import date
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
    tkavailable = True
except Exception as tkerr:
    tk = ttk = messagebox = simpledialog = filedialog = None
    tkavailable = False
    tkimporterror = tkerr

def projectroot():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def path(name: str):
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

if tkavailable:

    class edutrackapp(tk.Tk):
        def __init__(self):
            super().__init__()
            self.title("EduTrack")
            self.geometry("1100x720")
            self.configure(bg="#101820")
            self.users = None
            self.createstyle()
            self.createchrome()
            self.showlogin()

        def createstyle(self):
            self.style = ttk.Style()
            try:
                self.style.theme_use("clam")
            except Exception:
                pass
            self.style.configure("app.TFrame", background="#101820")
            self.style.configure("panel.TFrame", background="#161f29")
            self.style.configure("header.TLabel", background="#101820", foreground="#ffd166", font=("Segoe UI", 18, "bold"))
            self.style.configure("status.TLabel", background="#101820", foreground="#06d6a0", font=("Segoe UI", 10))
            self.style.configure("title.TLabel", background="#161f29", foreground="#ef476f", font=("Segoe UI", 14, "bold"))
            self.style.configure("text.TLabel", background="#161f29", foreground="#eeeeee", font=("Segoe UI", 10))
            self.style.configure("app.TButton", foreground="#ffffff", font=("Segoe UI", 10, "bold"))
            self.style.map("app.TButton",
                           foreground=[("!disabled", "#ffffff")],
                           background=[("!disabled", "#118ab2"), ("active", "#073b4c")])
            self.style.configure("accent.TButton", foreground="#ffffff", font=("Segoe UI", 10, "bold"))
            self.style.map("accent.TButton",
                           foreground=[("!disabled", "#ffffff")],
                           background=[("!disabled", "#ef476f"), ("active", "#d43d62")])

        def createchrome(self):
            header = ttk.Label(self, text="EduTrack", style="header.TLabel")
            header.pack(fill=tk.X, padx=12, pady=8)
            menubar = tk.Menu(self)
            filemenu = tk.Menu(menubar, tearoff=0)
            filemenu.add_command(label="Exit", command=self.onclose)
            menubar.add_cascade(label="File", menu=filemenu)
            helpmenu = tk.Menu(menubar, tearoff=0)
            helpmenu.add_command(label="About", command=lambda: messagebox.showinfo("About", "EduTrack GUI"))
            menubar.add_cascade(label="Help", menu=helpmenu)
            try:
                self.config(menu=menubar)
            except Exception:
                pass
            self.body = ttk.Frame(self, style="app.TFrame")
            self.body.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
            self.statusvar = tk.StringVar(value="ready")
            status = ttk.Label(self, textvariable=self.statusvar, style="status.TLabel", anchor="w")
            status.pack(fill=tk.X, side=tk.BOTTOM, padx=12, pady=6)

        def clearbody(self):
            for w in list(self.body.winfo_children()):
                w.destroy()

        def showlogin(self):
            self.clearbody()
            wrap = ttk.Frame(self.body, style="panel.TFrame")
            wrap.pack(pady=24, padx=24)
            ttk.Label(wrap, text="login", style="title.TLabel").grid(row=0, column=0, columnspan=2, pady=8)
            ttk.Label(wrap, text="username", style="text.TLabel").grid(row=1, column=0, sticky="w", pady=6)
            ttk.Label(wrap, text="password", style="text.TLabel").grid(row=2, column=0, sticky="w", pady=6)
            self.usernamevar = tk.StringVar()
            self.passwordvar = tk.StringVar()
            userentry = ttk.Entry(wrap, textvariable=self.usernamevar, width=30)
            pwentry = ttk.Entry(wrap, textvariable=self.passwordvar, show="*", width=30)
            userentry.grid(row=1, column=1, padx=8)
            pwentry.grid(row=2, column=1, padx=8)
            pwentry.focus_set()
            rowbtn = ttk.Frame(wrap, style="panel.TFrame")
            rowbtn.grid(row=3, column=0, columnspan=2, pady=12)
            btnlogin = ttk.Button(rowbtn, text="login", style="accent.TButton", command=self.onlogin)
            btnlogin.pack(side=tk.LEFT, padx=6)
            btnexit = ttk.Button(rowbtn, text="exit", style="app.TButton", command=self.onclose)
            btnexit.pack(side=tk.LEFT, padx=6)
            self.bind("<Return>", lambda e: self.onlogin())
            self.bind("<Control-Return>", lambda e: self.onlogin())
            rowlin = ttk.Frame(wrap, style="panel.TFrame")
            rowlin.grid(row=4, column=0, columnspan=2, pady=8)
            ttk.Button(rowlin, text="create account", style="app.TButton", command=self.createaccountdialog).pack(side=tk.LEFT, padx=6)
            ttk.Button(rowlin, text="forgot password", style="app.TButton", command=self.forgotpassworddialog).pack(side=tk.LEFT, padx=6)
            try:
                self.users = login.load_users()
            except Exception:
                self.users = None

        def onlogin(self):
            try:
                uname = (self.usernamevar.get() or "").strip()
                pwd = (self.passwordvar.get() or "").strip()
                if not uname or not pwd:
                    messagebox.showerror("login", "username and password required")
                    return
                users = self.users or login.load_users()
                uobj = users.find(uname) if users else None
                if not uobj:
                    messagebox.showerror("login", "user not found")
                    return
                ok = False
                try:
                    ok = login.hmac.compare_digest(login.make_hash(pwd, uobj.salt), uobj.pwd_hash)
                except Exception:
                    ok = False
                if not ok:
                    messagebox.showerror("login", "wrong password")
                    return
                self.user = uname
                self.role = uobj.role
                self.roll = subject.lookupRollNumber(uname, self.role)
                self.showmainmenu()
            except Exception as e:
                messagebox.showerror("login", str(e))

        def showmainmenu(self):
            self.clearbody()
            container = ttk.Frame(self.body, style="app.TFrame")
            container.pack(fill=tk.BOTH, expand=True)
            leftspace = ttk.Frame(container, style="app.TFrame")
            leftspace.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            centercol = ttk.Frame(container, style="panel.TFrame")
            centercol.pack(side=tk.LEFT, padx=10, pady=10)
            rightpanel = ttk.Frame(container, style="panel.TFrame")
            rightpanel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            ttk.Label(centercol, text=f"user: {getattr(self,'user','')}, role: {getattr(self,'role','')}", style="text.TLabel").pack(pady=4)
            ttk.Button(centercol, text="view dashboard", style="accent.TButton", width=28, command=self.viewdashboard).pack(pady=4)
            ttk.Button(centercol, text="attendance graph", style="accent.TButton", width=28, command=self.showattendancegraph).pack(pady=4)
            if self.role == "admin":
                self.addadmin(centercol)
            elif self.role == "teacher":
                self.addteacher(centercol)
            else:
                self.addstudent(centercol)
            ttk.Button(centercol, text="logout", style="app.TButton", width=28, command=self.showlogin).pack(pady=6)
            ttk.Button(centercol, text="exit", style="app.TButton", width=28, command=self.onclose).pack(pady=6)
            self.outputbox = tk.Text(rightpanel, wrap="word", bg="#0b1320", fg="#e2e2e2", insertbackground="#e2e2e2")
            self.outputbox.pack(fill=tk.BOTH, expand=True)

        def appendoutput(self, text):
            try:
                self.outputbox.insert("end", str(text) + "\n")
                self.outputbox.see("end")
            except Exception:
                pass

        def runandcapture(self, func):
            buf = io.StringIO()
            def job():
                try:
                    with contextlib.redirect_stdout(buf):
                        func()
                except Exception as e:
                    self.appendoutput(f"error: {e}")
            def done():
                out = buf.getvalue()
                if out.strip():
                    self.appendoutput(out.strip())
            runbg(job, ondone=done)

        def viewdashboard(self):
            roll = self.ensureroll()
            sec = section.getSectionForRoll(roll) if roll else "Not assigned"
            self.appendoutput(f"dashboard\nuser: {self.user} ({self.role})\nroll: {roll or 'N/A'}\nsection: {sec}")

        def ensureroll(self):
            if getattr(self, "roll", None):
                return self.roll
            created = subject.getRollNumber(self.user, self.role, create_if_missing=True)
            self.roll = created
            return created

        def addadmin(self, parent):
            ttk.Label(parent, text="admin actions", style="title.TLabel").pack(pady=6)
            ttk.Button(parent, text="add subject", style="app.TButton", width=28, command=self.addsubjectdialog).pack(pady=4)
            ttk.Button(parent, text="list subjects", style="app.TButton", width=28, command=lambda: self.runandcapture(subject.listSubjects)).pack(pady=4)
            ttk.Button(parent, text="create section", style="app.TButton", width=28, command=self.createsectiondialog).pack(pady=4)
            ttk.Button(parent, text="list sections", style="app.TButton", width=28, command=lambda: self.runandcapture(section.listSections)).pack(pady=4)
            ttk.Button(parent, text="assign section to student", style="app.TButton", width=28, command=self.assignsectionstudentdialog).pack(pady=4)
            ttk.Button(parent, text="assign sections to teacher", style="app.TButton", width=28, command=self.assignsectionteacherdialog).pack(pady=4)
            ttk.Button(parent, text="initialize all attendance", style="app.TButton", width=28, command=lambda: self.runandcapture(section.initialize_all_attendance_records)).pack(pady=4)
            ttk.Button(parent, text="set/update exam dates", style="app.TButton", width=28, command=self.setexamdatesdialog).pack(pady=4)
            ttk.Button(parent, text="view all exam dates", style="app.TButton", width=28, command=lambda: self.runandcapture(exam_date.viewAllExamDates)).pack(pady=4)
            ttk.Button(parent, text="view section assignments", style="app.TButton", width=28, command=lambda: self.runandcapture(section.viewSectionAssignments)).pack(pady=4)
            ttk.Button(parent, text="view student info", style="app.TButton", width=28, command=self.viewstudentinfodialog).pack(pady=4)
            ttk.Button(parent, text="view any student dashboard", style="app.TButton", width=28, command=self.viewstudentdashboarddialog).pack(pady=4)
            ttk.Button(parent, text="change own password", style="app.TButton", width=28, command=self.changeownpassworddialog).pack(pady=4)
            ttk.Button(parent, text="change another user's password", style="app.TButton", width=28, command=self.changeuserpassworddialog).pack(pady=4)
            ttk.Button(parent, text="migrate user data", style="app.TButton", width=28, command=self.migrateuserdatadialog).pack(pady=4)

        def addteacher(self, parent):
            ttk.Label(parent, text="teacher actions", style="title.TLabel").pack(pady=6)
            ttk.Button(parent, text="view my sections", style="app.TButton", width=28, command=lambda: self.runandcapture(lambda: section.viewMySections(self.user))).pack(pady=4)
            ttk.Button(parent, text="mark present", style="app.TButton", width=28, command=self.markpresentdialog).pack(pady=4)
            ttk.Button(parent, text="mark absent", style="app.TButton", width=28, command=self.markabsentdialog).pack(pady=4)
            ttk.Button(parent, text="update attendance totals", style="app.TButton", width=28, command=self.updateattendancetotalsdialog).pack(pady=4)
            ttk.Button(parent, text="view attendance chart", style="app.TButton", width=28, command=lambda: self.runandcapture(lambda: attendance.view_attendance(teachername=self.user))).pack(pady=4)
            ttk.Button(parent, text="add topic covered", style="app.TButton", width=28, command=self.addtopicdialog).pack(pady=4)
            ttk.Button(parent, text="view topics covered", style="app.TButton", width=28, command=self.viewmytopics).pack(pady=4)
            ttk.Button(parent, text="view submitted assignments", style="app.TButton", width=28, command=lambda: self.runandcapture(lambda: assignments.view_assignments(self.user))).pack(pady=4)
            ttk.Button(parent, text="view pdf content", style="app.TButton", width=28, command=self.viewpdfcontentdialog).pack(pady=4)
            ttk.Button(parent, text="change password", style="app.TButton", width=28, command=self.changepassworddialog).pack(pady=4)

        def addstudent(self, parent):
            ttk.Label(parent, text="student actions", style="title.TLabel").pack(pady=6)
            ttk.Button(parent, text="view my exam schedule", style="app.TButton", width=28, command=self.viewmyexamschedule_cli).pack(pady=4)
            ttk.Button(parent, text="view my exam schedule (by section)", style="app.TButton", width=28, command=self.viewmyexamschedule).pack(pady=4)
            ttk.Button(parent, text="view my attendance", style="app.TButton", width=28, command=self.viewmyattendance).pack(pady=4)
            ttk.Button(parent, text="view attendance summary", style="app.TButton", width=28, command=self.viewmyattendancesummary).pack(pady=4)
            ttk.Button(parent, text="view topics covered", style="app.TButton", width=28, command=self.viewmytopicsasstudent).pack(pady=4)
            ttk.Button(parent, text="submit assignment pdf", style="accent.TButton", width=28, command=self.submitassignmentdialog).pack(pady=4)
            ttk.Button(parent, text="change password", style="app.TButton", width=28, command=self.changepassworddialog).pack(pady=4)

        def addsubjectdialog(self):
            name = simpledialog.askstring("add subject", "subject name")
            if not name:
                return
            code = simpledialog.askstring("add subject", "subject code (e.g., TMA101)")
            if not code:
                return
            code = code.upper().strip()
            data = subject.loadJson(subject.subjectsFile, {"subjects": []})
            subs = data.get("subjects", []) if isinstance(data, dict) else []
            if any((s.get("code") or "").upper() == code for s in subs if isinstance(s, dict)):
                messagebox.showerror("subject", "code already exists")
                return
            subs.append({"name": name.strip(), "code": code})
            subject.saveJson(subject.subjectsFile, {"subjects": subs})
            self.appendoutput(f"subject added: {name} ({code})")

        def createsectiondialog(self):
            s = simpledialog.askstring("create section", "section name (e.g., A, AI, AIII)")
            if not s:
                return
            s = s.strip().upper()
            lst = section.loadJson(section.sectionListFile, [])
            lst = sorted({str(x).strip().upper() for x in lst if str(x).strip()})
            if s in lst:
                messagebox.showerror("section", "already exists")
                return
            lst.append(s)
            section.saveJson(section.sectionListFile, sorted(lst))
            secsubs = section.loadJson(section.sectionSubjectsFile, {})
            if s in ["AI", "BI", "CI", "DI"]:
                secsubs[s] = ["Basic Maths", "English-I", "C Lang", "Electronics", "Computer Networking"]
            elif s in ["AIII", "BIII", "CIII", "DIII"]:
                secsubs[s] = ["DSA", "English-III", "Maths-III", "Artificial Intelligence", "Operating System"]
            elif s in ["AV", "BV", "CV", "DV"]:
                secsubs[s] = ["English-V", "Machine Learning", "Algorithm", "OOP", "Database"]
            section.saveJson(section.sectionSubjectsFile, secsubs)
            self.appendoutput(f"section created: {s}")

        def assignsectionstudentdialog(self):
            rollnumbers = section.loadJson("rollnumbers.json", {})
            studentmap = rollnumbers.get("map", {}).get("student", {}) if isinstance(rollnumbers, dict) else {}
            if not studentmap:
                messagebox.showerror("assign", "no students found")
                return
            sroll = simpledialog.askstring("assign section", "enter student roll number")
            if not sroll or sroll not in studentmap.values():
                messagebox.showerror("assign", "invalid roll")
                return
            sname = next((n for n, r in studentmap.items() if r == sroll), sroll)
            secchoice = simpledialog.askstring("assign section", f"enter section for {sname} ({sroll})")
            if not secchoice:
                return
            secchoice = secchoice.strip().upper()
            sections = section.loadJson("sections.json", {})
            sections[sroll] = secchoice
            section.saveJson("sections.json", sections)
            secsubs = section.loadJson("sectionsubjects.json", {})
            subjectslist = secsubs.get(secchoice)
            if not subjectslist or not isinstance(subjectslist, list):
                messagebox.showerror("assign", "section not in sectionsubjects.json")
                return
            studentsubs = section.loadJson("studentsubjects.json", {})
            studentsubs[sroll] = {"section": secchoice, "subjects": subjectslist}
            section.saveJson("studentsubjects.json", studentsubs)
            am = section.loadJson("attendance_master.json", {"attendance_records": {}, "metadata": {}})
            records = am.get("attendance_records", {})
            if sroll not in records:
                subsdict = {
                    sub: {"subject_name": sub, "total_working_days": 0, "total_present_days": 0,
                          "attendance_percentage": 0.0, "last_updated": str(date.today())}
                    for sub in subjectslist
                }
                records[sroll] = {"name": sname, "section": secchoice, "subjects": subsdict}
            else:
                records[sroll]["section"] = secchoice
            am["attendance_records"] = records
            am.setdefault("metadata", {})
            am["metadata"]["last_updated"] = str(date.today())
            am["metadata"]["total_students"] = len(records)
            section.saveJson("attendance_master.json", am)
            self.appendoutput(f"assigned section {secchoice} to {sname} ({sroll})")

        def assignsectionteacherdialog(self):
            teacher = simpledialog.askstring("assign teacher", "enter teacher username")
            if not teacher:
                return
            lst = section.listSections(returnList=True) or []
            if not lst:
                messagebox.showerror("assign", "no sections")
                return
            choices = simpledialog.askstring("assign teacher", f"sections available: {', '.join(lst)}\nenter comma-separated sections")
            if not choices:
                return
            chosen = [x.strip().upper() for x in choices.split(",") if x.strip()]
            tmap = section.loadJson(section.teacherSectionsFile, {})
            tmap[teacher] = sorted(set(chosen))
            section.saveJson(section.teacherSectionsFile, tmap)
            self.appendoutput(f"assigned sections {', '.join(tmap[teacher])} to {teacher}")

        def setexamdatesdialog(self):
            subs = exam_date.loadSubjects()
            if not subs:
                messagebox.showerror("exam", "no subjects")
                return
            names = [f"{s.get('name','')} ({s.get('code','')})" for s in subs]
            msg = "choose subject numbers (comma):\n" + "\n".join([f"{i+1}. {names[i]}" for i in range(len(names))])
            sel = simpledialog.askstring("exam dates", msg)
            if not sel:
                return
            try:
                idxs = [int(x.strip()) - 1 for x in sel.split(",") if x.strip().isdigit()]
            except Exception:
                messagebox.showerror("exam", "invalid input")
                return
            m = exam_date.loadExamMap()
            for idx in idxs:
                if 0 <= idx < len(subs):
                    s = subs[idx]
                    code = (s.get("code") or "").upper()
                    name = s.get("name") or ""
                    d = simpledialog.askstring("exam date", f"{name} ({code}) date [DD/MM/YYYY]")
                    if not d:
                        continue
                    try:
                        from datetime import datetime as dt
                        dt.strptime(d, "%d/%m/%Y")
                    except Exception:
                        self.appendoutput(f"skipped {code}: invalid date")
                        continue
                    m[code] = {"subjectName": name, "examDate": d}
            exam_date.saveExamMap(m)
            self.appendoutput("exam dates saved")

        def viewstudentinfodialog(self):
            uname = simpledialog.askstring("student info", "enter student username")
            if not uname:
                return
            roll = subject.lookupRollNumber(uname, "student")
            if not roll:
                self.appendoutput("no roll found")
                return
            sec = section.getSectionForRoll(roll)
            self.appendoutput(f"student: {uname}\nroll: {roll}\nsection: {sec}")
            if sec and sec != "Not assigned":
                self.runandcapture(lambda: exam_date.viewSectionExamDates(sec))

        def viewstudentdashboarddialog(self):
            uname = simpledialog.askstring("student dashboard", "enter student username")
            if not uname:
                return
            roll = subject.lookupRollNumber(uname, "student")
            sec = section.getSectionForRoll(roll) if roll else "Not assigned"
            self.appendoutput(f"dashboard\nuser: {uname}\nroll: {roll or 'N/A'}\nsection: {sec}")
            if sec and sec != "Not assigned":
                self.runandcapture(lambda: exam_date.viewSectionExamDates(sec))

        def markpresentdialog(self):
            roll = simpledialog.askstring("mark present", "enter student roll")
            code = simpledialog.askstring("mark present", "enter subject code")
            if not roll or not code:
                return
            orig = builtins.input
            builtins.input = lambda p="": "y"
            try:
                self.runandcapture(lambda: attendance.mark_attendance(self.user, roll, code, True))
            finally:
                builtins.input = orig

        def markabsentdialog(self):
            roll = simpledialog.askstring("mark absent", "enter student roll")
            code = simpledialog.askstring("mark absent", "enter subject code")
            if not roll or not code:
                return
            orig = builtins.input
            builtins.input = lambda p="": "y"
            try:
                self.runandcapture(lambda: attendance.mark_attendance(self.user, roll, code, False))
            finally:
                builtins.input = orig

        def updateattendancetotalsdialog(self):
            roll = simpledialog.askstring("update totals", "enter student roll")
            code = simpledialog.askstring("update totals", "enter subject code or name")
            if not roll or not code:
                return
            work = simpledialog.askstring("update totals", "new total working days")
            pres = simpledialog.askstring("update totals", "new total present days")
            if not work or not pres or not work.isdigit() or not pres.isdigit():
                messagebox.showerror("attendance", "invalid numbers")
                return
            seq = [work.strip(), pres.strip(), "y"]
            it = iter(seq)
            orig = builtins.input
            builtins.input = lambda p="": next(it)
            try:
                self.runandcapture(lambda: attendance.update_attendance(self.user, roll, code))
            finally:
                builtins.input = orig

        def addtopicdialog(self):
            tmap = topics.load_teacher_sections()
            secs = tmap.get(self.user, [])
            if not secs:
                messagebox.showerror("topic", "no sections assigned")
                return
            if len(secs) == 1:
                sec = secs[0]
            else:
                msg = "choose section number:\n" + "\n".join([f"{i+1}. {secs[i]}" for i in range(len(secs))])
                ch = simpledialog.askstring("topic", msg)
                if not ch or not ch.isdigit():
                    return
                idx = int(ch) - 1
                if idx < 0 or idx >= len(secs):
                    return
                sec = secs[idx]
            top = simpledialog.askstring("topic", "enter topic")
            if not top:
                return
            data = topics.load_json(topics.TOPICS_FILE)
            data.setdefault(sec, []).append({"teacher": self.user, "topic": top.strip(), "date": __import__("datetime").datetime.now().strftime("%d/%m/%Y")})
            topics.save_json(topics.TOPICS_FILE, data)
            self.appendoutput(f"topic added for {sec}: {top.strip()}")

        def viewmytopics(self):
            tmap = topics.load_teacher_sections()
            secs = tmap.get(self.user, [])
            if not secs:
                self.appendoutput("no sections assigned")
                return
            data = topics.load_json(topics.TOPICS_FILE)
            anyp = False
            for sec in secs:
                entries = data.get(sec) or []
                if entries:
                    self.appendoutput(f"\ntopics for section {sec}:")
                    for i, t in enumerate(entries, 1):
                        self.appendoutput(f" {i}. {t.get('topic')} (by {t.get('teacher')} on {t.get('date')})")
                    anyp = True
            if not anyp:
                self.appendoutput("no topics recorded yet")

        def submitassignmentdialog(self):
            roll = self.ensureroll()
            if not roll:
                self.appendoutput("no roll")
                return
            pdfpath = filedialog.askopenfilename(title="select pdf")
            if not pdfpath:
                return
            self.runandcapture(lambda: assignments.submit_assignment(roll, pdfpath))

        def viewpdfcontentdialog(self):
            pdfpath = filedialog.askopenfilename(title="select pdf")
            if not pdfpath:
                return
            pg = simpledialog.askstring("pdf page", "page number (blank for all)")
            pnum = int(pg) if pg and pg.isdigit() else None
            self.runandcapture(lambda: assignments.view_pdf_content(pdfpath, pnum))

        def viewmyexamschedule(self):
            roll = self.ensureroll()
            sec = section.getSectionForRoll(roll) if roll else "Not assigned"
            if sec == "Not assigned":
                self.appendoutput("section not assigned")
                return
            self.runandcapture(lambda: exam_date.viewSectionExamDates(sec))

        def viewmyexamschedule_cli(self):
            self.runandcapture(lambda: exam_date.viewStudentExamSchedule(self.user))

        def viewmyattendance(self):
            roll = self.ensureroll()
            if not roll:
                self.appendoutput("no roll")
                return
            self.runandcapture(lambda: attendance.view_attendance(student_roll=roll))

        def viewmyattendancesummary(self):
            roll = self.ensureroll()
            if not roll:
                self.appendoutput("no roll")
                return
            self.runandcapture(lambda: attendance.get_student_attendance_summary(roll))

        def viewmytopicsasstudent(self):
            roll = self.ensureroll()
            if not roll:
                self.appendoutput("no roll")
                return
            self.runandcapture(lambda: topics.view_topics_for_student(roll))

        def showattendancegraph(self):
            if self.role == "student":
                roll = self.ensureroll()
                if not roll:
                    self.appendoutput("no roll")
                    return
                self.runandcapture(lambda: attendance.view_attendance(student_roll=roll))
                return
            if self.role == "teacher":
                self.runandcapture(lambda: attendance.view_attendance(teachername=self.user))
                return
            ch = simpledialog.askstring("attendance graph", "type: student / teacher")
            if not ch:
                return
            if ch.strip().lower().startswith("s"):
                sid = simpledialog.askstring("student", "enter student username")
                if not sid:
                    return
                roll = subject.lookupRollNumber(sid, "student")
                if not roll:
                    self.appendoutput("no roll for that username")
                    return
                self.runandcapture(lambda: attendance.view_attendance(student_roll=roll))
            else:
                tname = simpledialog.askstring("teacher", "enter teacher username")
                if not tname:
                    return
                self.runandcapture(lambda: attendance.view_attendance(teachername=tname))

        def onclose(self):
            try:
                self.destroy()
            except Exception:
                pass

        def createaccountdialog(self):
            try:
                roles = ("student", "teacher", "admin")
                role = simpledialog.askstring("create account", "role: student / teacher / admin")
                if not role:
                    return
                role = role.strip().lower()
                if role not in roles:
                    messagebox.showerror("account", "invalid role")
                    return
                if role == "admin":
                    admsec = simpledialog.askstring("admin", "admin creation password")
                    if not admsec or admsec != "admin@123":
                        messagebox.showerror("account", "incorrect admin creation password")
                        return
                uname = simpledialog.askstring("create account", "username")
                if not uname:
                    return
                users = self.users or login.load_users()
                if users.find(uname):
                    messagebox.showerror("account", "username exists")
                    return
                qs = [
                    "What is the name of your first pet?",
                    "What is the first dish you learned to cook?",
                    "What is your favorite book?",
                    "What is the first word you said (except mother and father)?",
                    "What city were you born in?"
                ]
                qnum = simpledialog.askstring("security", "question number 1-5")
                if not qnum or not qnum.isdigit():
                    return
                qidx = int(qnum)
                if qidx < 1 or qidx > len(qs):
                    messagebox.showerror("security", "invalid number")
                    return
                secq = qs[qidx - 1]
                seca = simpledialog.askstring("security", "answer")
                if not seca:
                    return
                pwd = simpledialog.askstring("password", "enter password (min 5 chars)")
                if not pwd or len(pwd) <= 4:
                    messagebox.showerror("account", "password too short")
                    return
                salt = login.make_salt()
                pwh = login.make_hash(pwd, salt)
                asalt = login.make_salt()
                ahash = login.make_hash(seca, asalt)
                users.add(uname, role, salt, pwh, secq, asalt, ahash)
                login.save_users(users)
                rno = subject.getRollNumber(uname, role)
                self.users = users
                self.appendoutput(f"account created: {uname} ({role}) roll: {rno}")
                messagebox.showinfo("account", f"created\nroll: {rno}")
            except Exception as e:
                messagebox.showerror("account", str(e))

        def forgotpassworddialog(self):
            try:
                users = self.users or login.load_users()
                uname = simpledialog.askstring("forgot password", "username")
                if not uname:
                    return
                uobj = users.find(uname)
                if not uobj:
                    messagebox.showerror("password", "user not found")
                    return
                ans = simpledialog.askstring("security", f"{uobj.question}")
                if not ans:
                    return
                if login.make_hash(ans, uobj.ans_salt) != uobj.ans_hash:
                    messagebox.showerror("password", "incorrect answer")
                    return
                newp = simpledialog.askstring("reset", "new password (min 5 chars)")
                if not newp or len(newp) <= 4:
                    messagebox.showerror("password", "password too short")
                    return
                ns = login.make_salt()
                nh = login.make_hash(newp, ns)
                uobj.salt = ns
                uobj.pwd_hash = nh
                login.save_users(users)
                self.users = users
                messagebox.showinfo("password", "changed")
                self.appendoutput(f"password changed for {uname}")
            except Exception as e:
                messagebox.showerror("password", str(e))

        def changepassworddialog(self):
            try:
                users = self.users or login.load_users()
                uobj = users.find(self.user)
                if not uobj:
                    messagebox.showerror("password", "user not found")
                    return
                newp = simpledialog.askstring("change password", "new password (min 5 chars)")
                if not newp or len(newp) <= 4:
                    messagebox.showerror("password", "password too short")
                    return
                ns = login.make_salt()
                nh = login.make_hash(newp, ns)
                uobj.salt = ns
                uobj.pwd_hash = nh
                login.save_users(users)
                self.users = users
                messagebox.showinfo("password", "changed")
                self.appendoutput(f"password changed for {self.user}")
            except Exception as e:
                messagebox.showerror("password", str(e))

        def changeownpassworddialog(self):
            self.changepassworddialog()

        def changeuserpassworddialog(self):
            try:
                users = self.users or login.load_users()
                target = simpledialog.askstring("change user password", "username")
                if not target:
                    return
                tuser = users.find(target)
                if not tuser:
                    messagebox.showerror("password", "user not found")
                    return
                if tuser.role == "admin":
                    messagebox.showerror("password", "cannot change another admin's password")
                    return
                newp = simpledialog.askstring("change user password", "new password (min 5 chars)")
                if not newp or len(newp) <= 4:
                    messagebox.showerror("password", "password too short")
                    return
                ns = login.make_salt()
                nh = login.make_hash(newp, ns)
                tuser.salt = ns
                tuser.pwd_hash = nh
                login.save_users(users)
                self.users = users
                messagebox.showinfo("password", "changed")
                self.appendoutput(f"password changed for {target}")
            except Exception as e:
                messagebox.showerror("password", str(e))

        def migrateuserdatadialog(self):
            try:
                roles = ("admin", "teacher", "student")
                default = simpledialog.askstring("migrate", "default role for missing entries (admin/teacher/student) [student]")
                if not default:
                    default = "student"
                default = default.strip().lower()
                if default not in roles:
                    default = "student"
                def job():
                    orig = builtins.input
                    builtins.input = lambda p="": default
                    try:
                        login.migrate_userdata_interactive()
                    finally:
                        builtins.input = orig
                self.runandcapture(job)
            except Exception as e:
                messagebox.showerror("migrate", str(e))

else:
    class edutrackapp:
        def __init__(self):
            raise RuntimeError("Tkinter not available: " + repr(tkimporterror))

if __name__ == "__main__":
    app = edutrackapp()
    if tkavailable:
        app.mainloop()
