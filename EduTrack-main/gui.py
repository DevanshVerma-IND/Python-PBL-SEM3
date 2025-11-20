from __future__ import annotations
import os
import sys
import json
import hmac
import shutil
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Literal

import login

PRIMARY_DEEP = "#2C3E50"
ACCENT_PINK = "#FF2F92"
SECONDARY_BLUE = "#3C5A99"
SIDEBAR_BLUE = "#4A90E2"
NEUTRAL_GRAYBLUE = "#5D6D7E"
BG_MAIN = "#FFFFFF"
BG_PANEL = "#F7F9FC"
BG_SIDEBAR = "#F0F3F8"

HEADING = ("Courier New", 28, "bold")
TITLE = ("Courier New", 20, "bold")
BODY = ("Courier New", 13)
BUTTON = ("Courier New", 14, "bold")
SMALL = ("Courier New", 11)

ROOT = os.path.dirname(os.path.abspath(__file__))
PATH_SUBJECTS = os.path.join(ROOT, "subjects.json")
PATH_SECTIONS = os.path.join(ROOT, "sections.json")
PATH_SECTIONLIST = os.path.join(ROOT, "sectionlist.json")
PATH_TEACHERSECTIONS = os.path.join(ROOT, "teachersections.json")
PATH_SECTIONSUBJECTS = os.path.join(ROOT, "sectionsubjects.json")
PATH_STUDENTSUBJECTS = os.path.join(ROOT, "studentsubjects.json")
PATH_ATTENDANCE = os.path.join(ROOT, "attendance_master.json")
PATH_TOPICS = os.path.join(ROOT, "topics.json")
PATH_ROLLNUMBERS = os.path.join(ROOT, "rollnumbers.json")
PATH_EXAMS = os.path.join(ROOT, "exam_date.json")
PATH_ASSIGNMENTS = os.path.join(ROOT, "assignments")

def load_json(path, default):
    try:
        if not os.path.exists(path):
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path, payload):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        return True
    except Exception as e:
        messagebox.showerror("File Error", f"Unable to save {os.path.basename(path)}: {e}")
        return False

def ensure_files():
    defaults = [
        (PATH_ATTENDANCE, {"attendance_records": {}, "metadata": {}}),
        (PATH_SUBJECTS, {"subjects": []}),
        (PATH_SECTIONS, {}),
        (PATH_SECTIONLIST, []),
        (PATH_TEACHERSECTIONS, {}),
        (PATH_SECTIONSUBJECTS, {}),
        (PATH_STUDENTSUBJECTS, {}),
        (PATH_TOPICS, {}),
        (PATH_ROLLNUMBERS, {"map": {"student": {}, "teacher": {}, "admin": {}}, "counters": {"student": 0, "teacher": 0, "admin": 0}}),
        (PATH_EXAMS, {"exam_schedule": []}),
    ]
    for p, d in defaults:
        if not os.path.exists(p):
            save_json(p, d)
    os.makedirs(PATH_ASSIGNMENTS, exist_ok=True)

def subject_list():
    data = load_json(PATH_SUBJECTS, {"subjects": []})
    if isinstance(data, dict) and "subjects" in data:
        return data["subjects"]
    if isinstance(data, list):
        return data
    return []

def code_by_name(name):
    for s in subject_list():
        if s.get("name") == name:
            return s.get("code", name)
    return name

def name_by_code(code):
    for s in subject_list():
        if s.get("code") == code:
            return s.get("name", code)
    return code

def teacher_sections_map():
    return load_json(PATH_TEACHERSECTIONS, {})

def sections_map():
    return load_json(PATH_SECTIONS, {})

def section_list():
    raw = load_json(PATH_SECTIONLIST, [])
    return sorted({str(s).strip().upper() for s in raw if str(s).strip()})

def section_subjects_map():
    return load_json(PATH_SECTIONSUBJECTS, {})

def topics_map():
    return load_json(PATH_TOPICS, {})

def attendance_master():
    return load_json(PATH_ATTENDANCE, {"attendance_records": {}, "metadata": {}})

def rollnumbers_map():
    return load_json(PATH_ROLLNUMBERS, {"map": {"student": {}, "teacher": {}, "admin": {}}, "counters": {}})

def exams_payload():
    return load_json(PATH_EXAMS, {"exam_schedule": []})

def student_subjects(roll):
    sdata = load_json(PATH_STUDENTSUBJECTS, {})
    entry = sdata.get(roll)
    if entry and isinstance(entry, dict):
        names = entry.get("subjects", [])
        if isinstance(names, list):
            return names
    am = attendance_master().get("attendance_records", {}).get(roll, {})
    subs = am.get("subjects", {})
    names = []
    for k, v in subs.items():
        nm = v.get("subject_name") if isinstance(v, dict) else None
        names.append(nm or name_by_code(k))
    return names

def student_section(roll):
    sm = sections_map()
    sec = sm.get(roll)
    if sec:
        return str(sec).strip().upper()
    sdata = load_json(PATH_STUDENTSUBJECTS, {}).get(roll, {})
    return str(sdata.get("section", "Not assigned")).strip().upper()

def ensure_student_attendance(roll, sec, names):
    att = attendance_master()
    records = att.get("attendance_records", {})
    if roll not in records:
        subjects_dict = {}
        for nm in names:
            code = code_by_name(nm)
            subjects_dict[code] = {
                "subject_name": nm,
                "total_working_days": 0,
                "total_present_days": 0,
                "attendance_percentage": 0.0,
                "last_updated": datetime.now().strftime("%Y-%m-%d")
            }
        records[roll] = {"name": roll, "section": sec, "subjects": subjects_dict}
        att["attendance_records"] = records
        att.setdefault("metadata", {})["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        att["metadata"]["total_students"] = len(records)
        save_json(PATH_ATTENDANCE, att)

class View:
    def frame(self, parent, bg, border=False):
        f = tk.Frame(parent, bg=bg)
        if border:
            f.configure(highlightbackground=NEUTRAL_GRAYBLUE, highlightthickness=1, bd=0)
        return f
    def label(self, parent, text: str, font, fg: str = PRIMARY_DEEP, bg: str = BG_MAIN, anchor: Literal["nw","n","ne","w","center","e","sw","s","se"] = "center"):
        return tk.Label(parent, text=text, font=font, fg=fg, bg=bg, anchor=anchor)
    def button(self, parent, text, cmd, bg=ACCENT_PINK, fg=PRIMARY_DEEP, width=18):
        return tk.Button(
            parent,
            text=text,
            command=cmd,
            bg=bg,
            fg=fg,
            bd=0,
            font=BUTTON,
            highlightthickness=0,
            width=width,
            pady=8,
            wraplength=240,    
            justify="left",     
            anchor="w"          
        )

    def entry(self, parent, show=None, width=28):
        return tk.Entry(parent, font=BODY, show=show if show else "", width=width, relief="flat", highlightbackground=NEUTRAL_GRAYBLUE, highlightthickness=1, bg=BG_PANEL, fg=PRIMARY_DEEP, insertbackground=PRIMARY_DEEP)
    def toplevel(self, parent, title, size="420x280"):
        t = tk.Toplevel(parent)
        t.geometry(size)
        t.title(title)
        t.configure(bg=BG_PANEL)
        return t
    def clear(self, frame):
        for w in frame.winfo_children():
            w.destroy()

class App:
    def __init__(self, root):
        ensure_files()
        self.root = root
        self.root.title("EDUTRACK")
        self.root.geometry("1280x820")
        self.root.configure(bg=BG_MAIN)
        self.v = View()
        self.users = login.load_users()
        self.active_user = ""
        self.active_role = ""
        self.login_frame = None
        self.shell_frame = None
        self.sidebar_frame = None
        self.content_frame = None
        self.sidebar_buttons = {}
        self.show_login()

    def show_login(self):
        if self.shell_frame:
            self.shell_frame.destroy()
            self.shell_frame = None
        if self.login_frame:
            self.login_frame.destroy()
        self.login_frame = self.v.frame(self.root, BG_MAIN, border=True)
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")
        brand = self.v.frame(self.login_frame, BG_MAIN)
        brand.pack(fill="x", pady=(20, 10), padx=40)
        self.v.label(brand, "EDUTRACK", HEADING, PRIMARY_DEEP, BG_MAIN).pack(fill="x")
        strip = self.v.frame(brand, ACCENT_PINK); strip.configure(height=4)
        strip.pack(fill="x", pady=(8, 0))
        form = self.v.frame(self.login_frame, BG_PANEL, border=True)
        form.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        self.v.label(form, "Modern campus login portal", TITLE, PRIMARY_DEEP, BG_PANEL).pack(pady=(24, 18))
        self.v.label(form, "Username", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x", padx=30)
        self.username_entry = self.v.entry(form)
        self.username_entry.pack(fill="x", padx=30, pady=(4, 16))
        self.v.label(form, "Password", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x", padx=30)
        self.password_entry = self.v.entry(form, show="*")
        self.password_entry.pack(fill="x", padx=30, pady=(4, 24))
        buttons = self.v.frame(form, BG_PANEL); buttons.pack(fill="x", padx=30, pady=12)
        self.v.button(buttons, "Login", self.attempt_login, ACCENT_PINK).pack(fill="x", pady=6)
        self.v.button(buttons, "Create Account", self.open_create_account, SIDEBAR_BLUE).pack(fill="x", pady=6)
        self.v.button(buttons, "Forgot Password", self.open_forgot_password, PRIMARY_DEEP).pack(fill="x", pady=6)
        self.root.bind("<Return>", lambda _e: self.attempt_login())

    def attempt_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Missing Data", "Please enter both username and password.")
            return
        user = self.users.find(username)
        if not user:
            messagebox.showerror("Login Failed", "No such user. Please create an account.")
            return
        if not hmac.compare_digest(login.make_hash(password, user.salt), user.pwd_hash):
            messagebox.showerror("Login Failed", "Wrong password. Please try again.")
            return
        self.active_user = username
        self.active_role = user.role
        self.show_shell()
        self.show_role_dashboard()

    def open_create_account(self):
        d = self.v.toplevel(self.root, "Create Account", "420x360")
        self.v.label(d, "Add a new campus profile", TITLE, PRIMARY_DEEP, BG_PANEL).pack(pady=(20, 12))
        self.v.label(d, "Username", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x", padx=30)
        name_ent = self.v.entry(d); name_ent.pack(fill="x", padx=30, pady=(4, 12))
        self.v.label(d, "Role (student/teacher/admin)", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x", padx=30)
        role_ent = self.v.entry(d); role_ent.pack(fill="x", padx=30, pady=(4, 12))
        self.v.label(d, "Password", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x", padx=30)
        pass_ent = self.v.entry(d, show="*"); pass_ent.pack(fill="x", padx=30, pady=(4, 12))
        self.v.label(d, "Admin creation password (admin only)", SMALL, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x", padx=30)
        admin_ent = self.v.entry(d, show="*"); admin_ent.pack(fill="x", padx=30, pady=(4, 12))
        self.v.label(d, "Security question", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x", padx=30)

        questions_list = getattr(login, "questions", [
            "What is the name of your first pet?",
            "What is the first dish you learned to cook?",
            "What is your favorite book?",
            "What is the first word you said (except mother and father)?",
            "What city were you born in?"
        ])

        q_var = tk.StringVar(value=questions_list[0])
        q_combo = ttk.Combobox(d, textvariable=q_var, values=questions_list, state="readonly")
        q_combo.pack(fill="x", padx=30, pady=(4, 12))

        self.v.label(d, "Security answer", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x", padx=30)
        a_ent = self.v.entry(d); a_ent.pack(fill="x", padx=30, pady=(4, 18))

        def save():
            role = role_ent.get().strip().lower()
            name = name_ent.get().strip()
            secret = pass_ent.get().strip()
            admin_key = admin_ent.get().strip()
            question = q_var.get().strip()
            answer = a_ent.get().strip()
            if not name or not secret or not role or not question or not answer:
                messagebox.showerror("Missing Data", "All fields are required."); return
            if role not in ("student", "teacher", "admin"):
                messagebox.showerror("Invalid Role", "Choose student, teacher, or admin."); return
            if role == "admin" and admin_key != "admin@123":
                messagebox.showerror("Unauthorized", "Incorrect admin creation password."); return
            if len(secret) <= 4:
                messagebox.showerror("Weak Password", "Password must be more than 4 characters."); return
            if self.users.find(name):
                messagebox.showerror("Duplicate User", "This username already exists."); return
            salt = login.make_salt(); pwd_hash = login.make_hash(secret, salt)
            ans_salt = login.make_salt(); ans_hash = login.make_hash(answer, ans_salt)
            self.users.add(name, role, salt, pwd_hash, question, ans_salt, ans_hash)
            login.save_users(self.users)
            messagebox.showinfo("Account", "Account created successfully."); d.destroy()
        self.v.button(d, "Save Account", save, SIDEBAR_BLUE).pack(pady=(0, 18))

    def open_forgot_password(self):
        d = self.v.toplevel(self.root, "Password Help", "420x260")
        self.v.label(d, "Recover your access", TITLE, PRIMARY_DEEP, BG_PANEL).pack(pady=(20, 10))
        self.v.label(d, "Username", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x", padx=30)
        user_ent = self.v.entry(d); user_ent.pack(fill="x", padx=30, pady=(4, 12))
        def go():
            uname = user_ent.get().strip()
            if not uname:
                messagebox.showerror("Missing Data", "Please enter your username."); return
            self.users = login.load_users()
            u = self.users.find(uname)
            if not u:
                messagebox.showerror("Unknown User", "This username is not registered."); return
            reset = self.v.toplevel(d, "Reset Secret", "420x260")
            self.v.label(reset, f"Security question:\n{u.question}", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x", padx=24, pady=(18, 8))
            self.v.label(reset, "Answer", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x", padx=24)
            a_ent = self.v.entry(reset); a_ent.pack(fill="x", padx=24, pady=(4, 10))
            self.v.label(reset, "New Password", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x", padx=24)
            np_ent = self.v.entry(reset, show="*"); np_ent.pack(fill="x", padx=24, pady=(4, 12))
            def save_new():
                ans = a_ent.get().strip(); new_secret = np_ent.get().strip()
                if not ans or not new_secret:
                    messagebox.showerror("Missing Data", "Answer and password are required."); return
                if len(new_secret) <= 4:
                    messagebox.showerror("Weak Password", "Password must be more than 4 characters."); return
                if login.make_hash(ans, u.ans_salt) != u.ans_hash:
                    messagebox.showerror("Incorrect Answer", "Security answer does not match."); return
                new_salt = login.make_salt(); new_hash = login.make_hash(new_secret, new_salt)
                u.salt = new_salt; u.pwd_hash = new_hash
                login.save_users(self.users)
                messagebox.showinfo("Updated", "Password has been reset."); reset.destroy(); d.destroy()
            self.v.button(reset, "Save New Password", save_new, SIDEBAR_BLUE).pack(pady=(0, 18))
        self.v.button(d, "Continue", go, SIDEBAR_BLUE).pack(pady=(0, 18))

    def show_shell(self):
        if self.login_frame:
            self.login_frame.destroy()
            self.login_frame = None
        if self.shell_frame:
            self.shell_frame.destroy()
        self.shell_frame = self.v.frame(self.root, BG_MAIN); self.shell_frame.pack(fill="both", expand=True)
        header = self.v.frame(self.shell_frame, BG_MAIN, border=True); header.pack(fill="x", padx=24, pady=20)
        self.v.label(header, "EDUTRACK", HEADING, PRIMARY_DEEP, BG_MAIN).pack(pady=(12, 6))
        self.v.label(header, "Unified academic cockpit for attendance, academics, and planning", BODY, NEUTRAL_GRAYBLUE, BG_MAIN).pack(pady=(0, 12))
        body = self.v.frame(self.shell_frame, BG_MAIN); body.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        self.sidebar_frame = self.v.frame(body, BG_SIDEBAR, border=True); self.sidebar_frame.pack(side="left", fill="y", padx=(0, 16), pady=4)
        self.content_frame = self.v.frame(body, BG_PANEL, border=True); self.content_frame.pack(side="right", fill="both", expand=True, pady=4)
        self.sidebar_buttons.clear()
        self.v.button(self.sidebar_frame, "Logout", self.logout, ACCENT_PINK).pack(fill="x", padx=24, pady=(20, 10))

    def safe_call(self, func):
        try:
            func()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def set_sidebar(self, items):
        if not self.sidebar_frame:
            return
        for w in list(self.sidebar_frame.winfo_children())[1:]:
            w.destroy()
        for text, handler in items:
            b = self.v.button(self.sidebar_frame, text, lambda h=handler: self.safe_call(h), SIDEBAR_BLUE)
            b.pack(fill="x", padx=24, pady=6)
            self.sidebar_buttons[text] = b

    def container(self, title_text):
        self.v.clear(self.content_frame)
        self.v.label(self.content_frame, title_text, TITLE, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x", padx=20, pady=(20, 10))
        div = self.v.frame(self.content_frame, NEUTRAL_GRAYBLUE); div.configure(height=2); div.pack(fill="x", padx=20, pady=(0, 10))
        c = self.v.frame(self.content_frame, BG_PANEL); c.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        return c

    def logout(self):
        self.active_user = ""
        self.active_role = ""
        self.show_login()

    def show_role_dashboard(self):
        r = (self.active_role or "").strip().lower()
        if r == "admin":
            self.dashboard_admin()
        elif r == "teacher":
            self.dashboard_teacher()
        elif r == "student":
            self.dashboard_student()
        else:
            self.dashboard_guest()

    def dashboard_guest(self):
        self.set_sidebar([])
        c = self.container("Dashboard")
        self.v.label(c, "Welcome back, Guest", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x", pady=(0, 12))

    def dashboard_student(self):
        items = [
            ("View dashboard", self.student_view_dashboard),
            ("View my exam schedule", self.student_exam_schedule),
            ("View my attendance", self.student_view_attendance),
            ("View attendance summary", self.student_attendance_summary),
            ("View topics covered in my section", self.student_view_topics),
            ("Submit assignment PDF", self.student_submit_assignment),
        ]
        self.set_sidebar(items)
        self.student_view_dashboard()

    def student_roll_and_section(self):
        try:
            import subject, section
            roll = subject.getRollNumber(self.active_user, "student")
            sec = section.getSectionForRoll(roll)
        except Exception:
            rmap = rollnumbers_map()
            roll = rmap.get("map", {}).get("student", {}).get(self.active_user, self.active_user)
            sec = sections_map().get(roll, "Not assigned")
        sec = str(sec or "Not assigned").strip().upper()
        return roll, sec

    def student_view_dashboard(self):
        roll, sec = self.student_roll_and_section()
        names = student_subjects(roll)
        ensure_student_attendance(roll, sec, names)
        c = self.container("Student Dashboard")
        self.v.label(c, "Subjects:", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x", pady=(12, 6))
        if names:
            for nm in names:
                self.v.label(c, f"• {nm}", SMALL, NEUTRAL_GRAYBLUE, BG_PANEL, anchor="w").pack(fill="x", pady=2)
        else:
            self.v.label(c, "No subjects mapped.", SMALL, NEUTRAL_GRAYBLUE, BG_PANEL, anchor="w").pack(fill="x", pady=2)
        if names:
            for nm in names:
                self.v.label(c, f"• {nm}", SMALL, NEUTRAL_GRAYBLUE, BG_PANEL, anchor="w").pack(fill="x", pady=2)
        else:
            self.v.label(c, "No subjects mapped.", SMALL, NEUTRAL_GRAYBLUE, BG_PANEL, anchor="w").pack(fill="x", pady=2)

    def student_exam_schedule(self):
        roll, sec = self.student_roll_and_section()
        names = student_subjects(roll)
        codes = [code_by_name(nm) for nm in names]
        schedule = exams_payload().get("exam_schedule", [])
        matched = []
        for item in schedule:
            scode = item.get("subject_code") or item.get("code")
            if scode in codes:
                matched.append((item.get("subject_name", name_by_code(scode)), scode, item.get("exam_date", "")))
        c = self.container("My Exam Schedule")
        if not matched:
            self.v.label(c, "No exam dates found for your subjects.", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x")
            return
        cols = ("Subject", "Code", "Exam Date")
        tree = ttk.Treeview(c, columns=cols, show="headings", height=10)
        for col in cols:
            tree.heading(col, text=col); tree.column(col, anchor="center", width=200)
        tree.pack(fill="both", expand=True)
        for nm, code, date in matched:
            tree.insert("", "end", values=(nm, code, date))

    def _add_scroll(self, parent):
        outer = self.v.frame(parent, BG_PANEL)
        outer.pack(fill="both", expand=True)
        canvas = tk.Canvas(outer, bg=BG_PANEL, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        sb.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=sb.set)
        inner = self.v.frame(canvas, BG_PANEL)
        inner_id = canvas.create_window((0, 0), window=inner, anchor="nw")
        def on_config(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfigure(inner_id, width=event.width)
        inner.bind("<Configure>", lambda e: on_config(e))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(inner_id, width=e.width))
        return inner

    def student_view_attendance(self):
        roll, _ = self.student_roll_and_section()
        data = attendance_master().get("attendance_records", {}).get(roll, {})
        subjects = data.get("subjects", {})
        c = self.container("My Attendance")
        cols = ("Subject", "Name", "Sessions", "Present", "Percent", "Updated")
        tree = ttk.Treeview(c, columns=cols, show="headings", height=12)
        for col in cols:
            tree.heading(col, text=col); tree.column(col, anchor="center", width=140)
        tree.pack(fill="both", expand=True)
        for code, det in subjects.items():
            tree.insert("", "end", values=(code, det.get("subject_name", code), det.get("total_working_days", 0),
                                           det.get("total_present_days", 0), f"{det.get('attendance_percentage', 0.0):.2f}%",
                                           det.get("last_updated", "-")))
        if subjects:
            try:
                from matplotlib.figure import Figure
                from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
                plot_host = self._add_scroll(c)
                bar_count = len(subjects)
                fig_h = max(3.5, min(10.0, 0.45 * bar_count))
                fig = Figure(figsize=(7.0, fig_h), dpi=100)
                ax = fig.add_subplot(111)
                names = [det.get("subject_name", code) for code, det in subjects.items()]
                vals = [det.get("attendance_percentage", 0.0) for det in subjects.values()]
                ax.barh(names, vals, color=SIDEBAR_BLUE)
                ax.set_xlim(0, 100)
                ax.set_xlabel("Percentage")
                ax.set_title(f"Attendance % for {roll}")
                fig.tight_layout()
                canvas = FigureCanvasTkAgg(fig, master=plot_host); canvas.draw(); canvas.get_tk_widget().pack(fill="both", expand=True, pady=8)
            except Exception:
                self.v.label(c, "Graph unavailable. Install matplotlib.", SMALL, NEUTRAL_GRAYBLUE, BG_PANEL, anchor="w").pack(fill="x", pady=8)

    def student_attendance_summary(self):
        roll, _ = self.student_roll_and_section()
        data = attendance_master().get("attendance_records", {}).get(roll, {})
        c = self.container("Attendance Summary")
        if not data:
            self.v.label(c, "No attendance data found.", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x"); return
        self.v.label(c, f"Roll: {roll}", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x", pady=4)
        self.v.label(c, f"Section: {data.get('section','')}", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x", pady=4)
        self.v.label(c, "Subject-wise:", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x", pady=(12, 6))
        for code, det in data.get("subjects", {}).items():
            self.v.label(c, f"{det.get('subject_name','')} ({code})", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x")
            self.v.label(c, f"Working: {det.get('total_working_days',0)}  Present: {det.get('total_present_days',0)}  Attendance: {det.get('attendance_percentage',0.0)}%", SMALL, NEUTRAL_GRAYBLUE, BG_PANEL, anchor="w").pack(fill="x", pady=(0, 6))

    def student_view_topics(self):
        roll, sec = self.student_roll_and_section()
        items = topics_map().get(sec, [])
        c = self.container("Topics Covered")
        if not items:
            self.v.label(c, f"No topics found for section {sec}.", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x"); return
        cols = ("Date", "Teacher", "Topic")
        tree = ttk.Treeview(c, columns=cols, show="headings", height=12)
        for col in cols:
            tree.heading(col, text=col); tree.column(col, anchor="center", width=220)
        tree.pack(fill="both", expand=True)
        for item in items:
            tree.insert("", "end", values=(item.get("date",""), item.get("teacher",""), item.get("topic","")))

    def student_submit_assignment(self):
        roll, sec = self.student_roll_and_section()
        c = self.container("Submit Assignment")
        self.v.label(c, "Select a PDF to submit.", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x")
        def choose():
            path = filedialog.askopenfilename(title="Select Assignment PDF", filetypes=[("PDF Files", "*.pdf")])
            if not path:
                return
            if not path.lower().endswith(".pdf"):
                messagebox.showerror("File", "Only PDF files allowed."); return
            dest_folder = os.path.join(PATH_ASSIGNMENTS, sec or "UNASSIGNED")
            os.makedirs(dest_folder, exist_ok=True)
            dest_path = os.path.join(dest_folder, f"{roll}.pdf")
            try:
                shutil.copy2(path, dest_path)
                messagebox.showinfo("Assignment", f"Submitted: {dest_path}")
            except Exception as e:
                messagebox.showerror("Assignment", str(e))
        self.v.button(c, "Choose PDF and Submit", choose, SIDEBAR_BLUE).pack(pady=10)

    def dashboard_admin(self):
        items = [
            ("Admin Home", self.admin_home),
            ("Add subject", self.admin_add_subject),
            ("List subjects", self.admin_list_subjects),
            ("Create section", self.admin_create_section),
            ("List sections", self.admin_list_sections),
            ("Assign section to student (choose from list)", self.admin_assign_section_to_student),
            ("Assign sections to teacher", self.admin_assign_sections_to_teacher),
            ("Set/Update exam dates", self.admin_set_exam_dates),
            ("View all exam dates", self.admin_view_all_exam_dates),
            ("View section assignments", self.admin_view_section_assignments),
            ("View student info", self.admin_view_student_info),
            ("View any student's dashboard", self.admin_open_student_dashboard),
        ]
        self.set_sidebar(items)
        self.admin_home()

    def admin_home(self):
        c = self.container("Admin Dashboard")
        subjects = subject_list()
        sections = section_list()
        teachers = teacher_sections_map()
        att = attendance_master()
        students_count = len(att.get("attendance_records", {}))
        stats_frame = self.v.frame(c, "#FFFFFF", border=True)
        stats_frame.pack(fill="x", padx=0, pady=8)
        metrics = [
            ("Students", students_count, "Onboarded learners"),
            ("Subjects", len(subjects), "Academic offerings"),
            ("Sections", len(sections), "Active homerooms"),
            ("Teachers", len(teachers), "Faculty mapped"),
        ]
        for title, value, desc in metrics:
            card = self.v.frame(stats_frame, "#FFFFFF", border=True)
            card.pack(side="left", expand=True, fill="both", padx=8, pady=8)
            self.v.label(card, str(value), HEADING, PRIMARY_DEEP, "#FFFFFF").pack(pady=(18, 4))
            self.v.label(card, title.upper(), SMALL, NEUTRAL_GRAYBLUE, "#FFFFFF").pack()
            self.v.label(card, desc, SMALL, PRIMARY_DEEP, "#FFFFFF").pack(pady=(4, 16))
        quick = self.v.frame(c, BG_PANEL, border=True)
        quick.pack(fill="x", pady=18)
        self.v.label(quick, "Quick Actions", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x", padx=18, pady=(16, 8))
        row = self.v.frame(quick, BG_PANEL)
        row.pack(fill="x", padx=18, pady=(0, 18))
        actions = [
            ("Add Subject", self.admin_add_subject),
            ("Create Section", self.admin_create_section),
            ("Assign Student", self.admin_assign_section_to_student),
            ("Assign Teacher", self.admin_assign_sections_to_teacher),
            ("Set Exam Dates", self.admin_set_exam_dates),
            ("View All Exams", self.admin_view_all_exam_dates),
            ("Section Assignments", self.admin_view_section_assignments),
            ("Open Student Dashboard", self.admin_open_student_dashboard),
        ]
        for text, handler in actions:
            b = self.v.button(row, text, lambda h=handler: self.safe_call(h), bg="#E6ECF8")
            b.pack(side="left", expand=True, fill="x", padx=6)

    def admin_add_subject(self):
        c = self.container("Add Subject")
        self.v.label(c, "Subject Code", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x"); code_ent = self.v.entry(c); code_ent.pack(fill="x", pady=6)
        self.v.label(c, "Subject Name", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x"); name_ent = self.v.entry(c); name_ent.pack(fill="x", pady=6)
        def save():
            code = code_ent.get().strip().upper(); name = name_ent.get().strip()
            if not code or not name:
                messagebox.showerror("Input", "Code and name required."); return
            subs = subject_list()
            if any(s.get("code") == code for s in subs):
                messagebox.showerror("Duplicate", "Subject code already exists."); return
            subs.append({"code": code, "name": name}); save_json(PATH_SUBJECTS, {"subjects": subs})
            messagebox.showinfo("Subject", "Subject added."); self.admin_list_subjects()
        self.v.button(c, "Save", save, SIDEBAR_BLUE).pack(pady=8)

    def admin_list_subjects(self):
        c = self.container("Subjects")
        subs = subject_list()
        if not subs:
            self.v.label(c, "No subjects found. Use 'Add subject' to create one.", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x")
            return
        cols = ("Code", "Name")
        tree = ttk.Treeview(c, columns=cols, show="headings", height=12)
        for col in cols:
            tree.heading(col, text=col); tree.column(col, anchor="center", width=220)
        tree.pack(fill="both", expand=True)
        for s in subs:
            tree.insert("", "end", values=(s.get("code",""), s.get("name","")))

    def admin_create_section(self):
        c = self.container("Create Section")
        self.v.label(c, "New section (e.g., A)", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x"); sec_ent = self.v.entry(c); sec_ent.pack(fill="x", pady=6)
        def save():
            s = sec_ent.get().strip().upper()
            if not s: messagebox.showerror("Input", "Invalid section."); return
            lst = section_list()
            if s in lst: messagebox.showerror("Duplicate", "Section already exists."); return
            lst.append(s); save_json(PATH_SECTIONLIST, sorted(lst))
            section_subjects = section_subjects_map()
            if s in ["AI", "BI", "CI", "DI"]:
                section_subjects[s] = ["Basic Maths", "English-I", "C Lang", "Electronics", "Computer Networking"]
            elif s in ["AIII", "BIII", "CIII", "DIII"]:
                section_subjects[s] = ["DSA", "English-III", "Maths-III", "Artificial Intelligence", "Operating System"]
            elif s in ["AV", "BV", "CV", "DV"]:
                section_subjects[s] = ["English-V", "Machine Learning", "Algorithm", "OOP", "Database"]
            save_json(PATH_SECTIONSUBJECTS, section_subjects)
            messagebox.showinfo("Section", f"Section {s} created."); self.admin_list_sections()
        self.v.button(c, "Create", save, SIDEBAR_BLUE).pack(pady=8)

    def admin_list_sections(self):
        c = self.container("Sections")
        secs = section_list()
        if not secs:
            self.v.label(c, "No sections found. Use 'Create section' to add one.", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x")
            return
        cols = ("Section",)
        tree = ttk.Treeview(c, columns=cols, show="headings", height=12)
        for col in cols: tree.heading(col, text=col); tree.column(col, anchor="center", width=200)
        tree.pack(fill="both", expand=True)
        for s in secs:
            tree.insert("", "end", values=(s,))

    def admin_assign_section_to_student(self):
        c = self.container("Assign Section to Student")
        rmap = rollnumbers_map().get("map", {}).get("student", {})
        secmap = sections_map(); lst = section_list()

        nb = ttk.Notebook(c)
        nb.pack(fill="both", expand=True)

        tab_select = self.v.frame(nb, BG_PANEL)
        tab_manual = self.v.frame(nb, BG_PANEL)
        nb.add(tab_select, text="Select from lists")
        nb.add(tab_manual, text="Manual entry")

        if not lst:
            self.v.label(tab_select, "No sections available. Create a section first.", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x", padx=12, pady=12)
        else:
            self.v.label(tab_select, "Student roll", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x", padx=12)
            if rmap:
                students = sorted([(n, r) for n, r in rmap.items()], key=lambda x: x[1])
                student_var = tk.StringVar(value=students[0][1])
                ttk.Combobox(tab_select, textvariable=student_var, values=[r for _, r in students], state="readonly").pack(fill="x", padx=12, pady=6)
            else:
                student_var = tk.StringVar(value="")
                self.v.entry(tab_select).pack(fill="x", padx=12, pady=6)
                def bind_entry(e): student_var.set(e.widget.get().strip())
                tab_select.winfo_children()[-1].bind("<KeyRelease>", bind_entry)

            self.v.label(tab_select, "Section", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x", padx=12)
            section_var = tk.StringVar(value=lst[0] if lst else "")
            ttk.Combobox(tab_select, textvariable=section_var, values=lst, state="readonly").pack(fill="x", padx=12, pady=6)

            def assign_sel():
                roll = student_var.get().strip()
                sec = section_var.get().strip()
                if not roll or not sec:
                    messagebox.showerror("Input", "Choose student and section."); return
                secmap[roll] = sec; save_json(PATH_SECTIONS, secmap)
                sec_subjects = section_subjects_map().get(sec, [])
                studentsubj = load_json(PATH_STUDENTSUBJECTS, {}); studentsubj[roll] = {"section": sec, "subjects": sec_subjects}
                save_json(PATH_STUDENTSUBJECTS, studentsubj)
                ensure_student_attendance(roll, sec, sec_subjects)
                messagebox.showinfo("Assigned", f"Assigned {roll} to section {sec}.")
                self.admin_view_section_assignments()
            self.v.button(tab_select, "Assign", assign_sel, SIDEBAR_BLUE).pack(pady=10)

        self.v.label(tab_manual, "Enter student roll", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x", padx=12)
        roll_ent = self.v.entry(tab_manual); roll_ent.pack(fill="x", padx=12, pady=6)
        self.v.label(tab_manual, "Enter section", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x", padx=12)
        sec_ent = self.v.entry(tab_manual); sec_ent.pack(fill="x", padx=12, pady=6)
        def assign_manual():
            roll = roll_ent.get().strip()
            sec = sec_ent.get().strip().upper()
            if not roll or not sec:
                messagebox.showerror("Input", "Enter roll and section."); return
            if sec not in lst:
                messagebox.showerror("Input", "Section not found. Create section first."); return
            secmap[roll] = sec; save_json(PATH_SECTIONS, secmap)
            sec_subjects = section_subjects_map().get(sec, [])
            studentsubj = load_json(PATH_STUDENTSUBJECTS, {}); studentsubj[roll] = {"section": sec, "subjects": sec_subjects}
            save_json(PATH_STUDENTSUBJECTS, studentsubj)
            ensure_student_attendance(roll, sec, sec_subjects)
            messagebox.showinfo("Assigned", f"Assigned {roll} to section {sec}.")
            self.admin_view_section_assignments()
        self.v.button(tab_manual, "Assign", assign_manual, SIDEBAR_BLUE).pack(pady=10)

    def admin_assign_sections_to_teacher(self):
        c = self.container("Assign Sections to Teacher")
        tmap = teacher_sections_map(); teachers = sorted({*tmap.keys()}) if tmap else []
        teacher_var = tk.StringVar(value=(teachers[0] if teachers else ""))
        self.v.label(c, "Teacher username", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x")
        teacher_ent = self.v.entry(c); teacher_ent.insert(0, teacher_var.get()); teacher_ent.pack(fill="x", pady=6)
        self.v.label(c, "Sections (comma separated)", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x")
        sections_ent = self.v.entry(c); sections_ent.pack(fill="x", pady=6)
        def save():
            tname = teacher_ent.get().strip(); lst = [s.strip().upper() for s in sections_ent.get().split(",") if s.strip()]
            if not tname or not lst: messagebox.showerror("Input", "Enter teacher and sections."); return
            sec_all = set(section_list())
            missing = [s for s in lst if s not in sec_all]
            if missing:
                messagebox.showerror("Input", f"Unknown sections: {', '.join(missing)}"); return
            tmap[tname] = sorted(set(lst)); save_json(PATH_TEACHERSECTIONS, tmap)
            messagebox.showinfo("Teacher", f"Assigned sections {', '.join(tmap[tname])} to {tname}.")
        self.v.button(c, "Save", save, SIDEBAR_BLUE).pack(pady=8)

    def admin_set_exam_dates(self):
        c = self.container("Set/Update Exam Dates")
        subs = subject_list()
        if not subs:
            self.v.label(c, "No subjects available.", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x"); return
        self.v.label(c, "Enter exam date (DD/MM/YYYY) for selected subject", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x")
        codes = [s["code"] for s in subs]; code_var = tk.StringVar(value=codes[0]); date_ent = self.v.entry(c); date_ent.pack(fill="x", pady=6)
        ttk.Combobox(c, textvariable=code_var, values=codes, state="readonly").pack(fill="x", pady=6)
        def save_date():
            code = code_var.get().strip().upper(); date_str = date_ent.get().strip()
            if not code or not date_str: messagebox.showerror("Input", "Code and date required."); return
            payload = exams_payload(); found = False
            for item in payload.get("exam_schedule", []):
                if (item.get("subject_code") or item.get("code")) == code:
                    item["subject_code"] = code; item["exam_date"] = date_str; found = True; break
            if not found:
                name = next((s["name"] for s in subs if s["code"] == code), "")
                payload.setdefault("exam_schedule", []).append({"subject_code": code, "subject_name": name, "exam_date": date_str})
            save_json(PATH_EXAMS, payload); messagebox.showinfo("Exams", "Exam date saved.")
        self.v.button(c, "Save Date", save_date, SIDEBAR_BLUE).pack(pady=8)

    def admin_view_all_exam_dates(self):
        c = self.container("Exam Dates (All Subjects)")
        data = exams_payload().get("exam_schedule", [])
        if not data:
            self.v.label(c, "No exam dates set.", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x"); return
        cols = ("Subject", "Code", "Exam Date")
        tree = ttk.Treeview(c, columns=cols, show="headings", height=12)
        for col in cols: tree.heading(col, text=col); tree.column(col, anchor="center", width=220)
        tree.pack(fill="both", expand=True)
        for item in data:
            tree.insert("", "end", values=(item.get("subject_name",""), item.get("subject_code",""), item.get("exam_date","")))

    def admin_view_section_assignments(self):
        c = self.container("Section Assignments")
        mapping = sections_map()
        if not mapping:
            self.v.label(c, "No students assigned yet.", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x"); return
        bysec = {}
        for roll, sec in mapping.items():
            sec = str(sec).strip().upper(); bysec.setdefault(sec, []).append(roll)
        cols = ("Section", "Students")
        tree = ttk.Treeview(c, columns=cols, show="headings", height=12)
        for col in cols: tree.heading(col, text=col); tree.column(col, anchor="center", width=280)
        tree.pack(fill="both", expand=True)
        for sec, rolls in sorted(bysec.items()):
            tree.insert("", "end", values=(sec, ", ".join(sorted(rolls))))

    def admin_view_student_info(self):
        c = self.container("View Student Info")
        self.v.label(c, "Student username", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x"); name_ent = self.v.entry(c); name_ent.pack(fill="x", pady=6)
        def go():
            studentname = name_ent.get().strip()
            if not studentname: messagebox.showerror("Input", "Enter username."); return
            rmap = rollnumbers_map().get("map", {}).get("student", {})
            roll = rmap.get(studentname, studentname)
            sec = student_section(roll)
            self.v.label(c, f"Roll: {roll}", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x", pady=6)
            self.v.label(c, f"Section: {sec}", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x", pady=6)
            names = student_subjects(roll)
            if names:
                self.v.label(c, "Subjects:", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x", pady=(10, 6))
                for nm in names:
                    self.v.label(c, f"• {nm}", SMALL, NEUTRAL_GRAYBLUE, BG_PANEL, anchor="w").pack(fill="x")
            else:
                self.v.label(c, "No subjects mapped.", SMALL, NEUTRAL_GRAYBLUE, BG_PANEL, anchor="w").pack(fill="x")
        self.v.button(c, "Show", go, SIDEBAR_BLUE).pack(pady=8)

    def admin_open_student_dashboard(self):
        c = self.container("Open Student Dashboard")
        self.v.label(c, "Student username", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x")
        name_ent = self.v.entry(c)
        name_ent.pack(fill="x", pady=6)

        def go():
            studentname = name_ent.get().strip()
            if not studentname:
                messagebox.showerror("Input", "Enter username.")
                return

            try:
                import subject, section
                roll = subject.getRollNumber(studentname, "student")
                sec = section.getSectionForRoll(roll)
            except Exception:
                rmap = rollnumbers_map()
                roll = rmap.get("map", {}).get("student", {}).get(studentname, studentname)
                sec = sections_map().get(roll, "Not assigned")

            names = student_subjects(roll)
            ensure_student_attendance(roll, sec, names)

            win = tk.Toplevel(self.root)
            win.title(f"Student Dashboard - {studentname}")
            win.geometry("520x420")

            frame = tk.Frame(win, bg=BG_PANEL, padx=12, pady=12)
            frame.pack(fill="both", expand=True)

            tk.Label(frame, text=f"Username: {studentname}", font=BODY, fg=PRIMARY_DEEP, bg=BG_PANEL, anchor="w").pack(fill="x", pady=4)
            tk.Label(frame, text=f"Roll: {roll}", font=BODY, fg=PRIMARY_DEEP, bg=BG_PANEL, anchor="w").pack(fill="x", pady=4)
            tk.Label(frame, text=f"Section: {str(sec or 'Not assigned').strip().upper()}", font=BODY, fg=PRIMARY_DEEP, bg=BG_PANEL, anchor="w").pack(fill="x", pady=4)

            tk.Label(frame, text="Subjects:", font=BODY, fg=PRIMARY_DEEP, bg=BG_PANEL, anchor="w").pack(fill="x", pady=(12, 6))
            if names:
                for nm in names:
                    tk.Label(frame, text=f"• {nm}", font=SMALL, fg=NEUTRAL_GRAYBLUE, bg=BG_PANEL, anchor="w").pack(fill="x", pady=2)
            else:
                tk.Label(frame, text="(No subjects assigned)", font=SMALL, fg=NEUTRAL_GRAYBLUE, bg=BG_PANEL, anchor="w").pack(fill="x", pady=2)

            tk.Button(frame, text="Close", command=win.destroy, bg=SIDEBAR_BLUE).pack(pady=10)

            messagebox.showinfo("Dashboard", "Student dashboard opened in a new window.")

        self.v.button(c, "Open", go, SIDEBAR_BLUE).pack(pady=8)


    def dashboard_teacher(self):
        items = [
            ("View my sections", self.teacher_view_sections),
            ("Mark present", self.teacher_mark_present),
            ("Update attendance/ mark absent", self.teacher_update_attendance),
            ("View attendance chart", self.teacher_view_chart),
            ("Add topic covered", self.teacher_add_topic),
            ("View topics covered", self.teacher_view_topics),
            ("View submitted assignments", self.teacher_view_assignments),
        ]
        self.set_sidebar(items)
        self.teacher_view_sections()

    def teacher_view_sections(self):
        c = self.container("My Sections")
        secs = teacher_sections_map().get(self.active_user, [])
        if not secs:
            self.v.label(c, "No sections assigned.", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x"); return
        for s in secs:
            self.v.label(c, s, BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x", pady=2)

    def teacher_mark_present(self):
        c = self.container("Mark Present")
        self.v.label(c, "Student roll", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x"); roll_ent = self.v.entry(c); roll_ent.pack(fill="x", pady=6)
        self.v.label(c, "Subject code", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x"); code_ent = self.v.entry(c); code_ent.pack(fill="x", pady=6)
        def go():
            roll = roll_ent.get().strip(); code = code_ent.get().strip().upper()
            if not roll or not code: messagebox.showerror("Input", "Enter roll and subject code."); return
            att = attendance_master(); recs = att.get("attendance_records", {})
            if roll not in recs: messagebox.showerror("Attendance", "Student not found."); return
            subs = recs[roll].get("subjects", {})
            key = code if code in subs else None
            if not key:
                for k, v in subs.items():
                    if str(v.get("subject_name","")).strip().upper() == code.strip().upper():
                        key = k; break
            if not key: messagebox.showerror("Subject", "Subject not found for student."); return
            det = subs[key]
            det["total_working_days"] = int(det.get("total_working_days", 0)) + 1
            det["total_present_days"] = int(det.get("total_present_days", 0)) + 1
            tw = det["total_working_days"]; tp = det["total_present_days"]
            det["attendance_percentage"] = round((tp / tw) * 100, 2) if tw else 0.0
            det["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            recs[roll]["subjects"][key] = det
            att["attendance_records"] = recs
            att.setdefault("metadata", {})["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            save_json(PATH_ATTENDANCE, att)
            messagebox.showinfo("Attendance", "Marked present.")
        self.v.button(c, "Mark", go, SIDEBAR_BLUE).pack(pady=8)

    def teacher_update_attendance(self):
        c = self.container("Update Attendance / Mark Absent")
        self.v.label(c, "Student roll", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x"); roll_ent = self.v.entry(c); roll_ent.pack(fill="x", pady=6)
        self.v.label(c, "Subject code", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x"); code_ent = self.v.entry(c); code_ent.pack(fill="x", pady=6)
        self.v.label(c, "New total working days", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x"); tw_ent = self.v.entry(c); tw_ent.pack(fill="x", pady=6)
        self.v.label(c, "New total present days", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x"); tp_ent = self.v.entry(c); tp_ent.pack(fill="x", pady=6)
        def go():
            roll = roll_ent.get().strip(); code = code_ent.get().strip().upper()
            try: tw = int(tw_ent.get().strip()); tp = int(tp_ent.get().strip())
            except Exception: messagebox.showerror("Input", "Enter numeric values."); return
            if tp > tw: messagebox.showerror("Input", "Present days cannot exceed working days."); return
            att = attendance_master(); recs = att.get("attendance_records", {})
            if roll not in recs: messagebox.showerror("Attendance", "Student not found."); return
            subs = recs[roll].get("subjects", {})
            key = code if code in subs else None
            if not key:
                for k, v in subs.items():
                    if str(v.get("subject_name","")).strip().upper() == code.strip().upper():
                        key = k; break
            if not key: messagebox.showerror("Subject", "Subject not found for student."); return
            det = subs[key]
            det["total_working_days"] = tw
            det["total_present_days"] = tp
            det["attendance_percentage"] = round((tp / tw) * 100, 2) if tw else 0.0
            det["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            recs[roll]["subjects"][key] = det
            att["attendance_records"] = recs
            att.setdefault("metadata", {})["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            save_json(PATH_ATTENDANCE, att)
            messagebox.showinfo("Attendance", "Updated.")
        self.v.button(c, "Update", go, SIDEBAR_BLUE).pack(pady=8)

    def teacher_view_chart(self):
        c = self.container("Attendance Chart (My Sections)")
        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except Exception:
            self.v.label(c, "matplotlib not installed; chart unavailable.", BODY, NEUTRAL_GRAYBLUE, BG_PANEL, anchor="w").pack(fill="x"); return
        mysecs = teacher_sections_map().get(self.active_user, [])
        att = attendance_master().get("attendance_records", {})
        pairs = []
        for roll, rec in att.items():
            if rec.get("section") in mysecs:
                for code, det in rec.get("subjects", {}).items():
                    pairs.append((f"{det.get('subject_name', code)} ({roll})", det.get("attendance_percentage", 0.0)))
        if not pairs:
            self.v.label(c, "No attendance data found for your sections.", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x"); return
        pairs.sort(key=lambda x: x[1], reverse=True)
        labels = [p[0] for p in pairs]
        values = [p[1] for p in pairs]
        plot_host = self._add_scroll(c)
        fig_h = max(4.0, min(12.0, 0.45 * len(labels)))
        fig = Figure(figsize=(8.0, fig_h), dpi=100)
        ax = fig.add_subplot(111)
        ax.barh(labels, values, color=SIDEBAR_BLUE)
        ax.set_xlim(0, 100)
        ax.set_xlabel("Attendance %")
        ax.set_title(f"Teacher {self.active_user}")
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=plot_host); canvas.draw(); canvas.get_tk_widget().pack(fill="both", expand=True, pady=8)

    def teacher_add_topic(self):
        c = self.container("Add Topic Covered")
        self.v.label(c, "Section", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x"); sec_ent = self.v.entry(c); sec_ent.pack(fill="x", pady=6)
        self.v.label(c, "Topic", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x"); topic_ent = self.v.entry(c); topic_ent.pack(fill="x", pady=6)
        self.v.label(c, "Date (DD/MM/YYYY)", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x"); date_ent = self.v.entry(c); date_ent.pack(fill="x", pady=6)
        def save():
            sec = sec_ent.get().strip().upper(); topic = topic_ent.get().strip(); date = date_ent.get().strip()
            if not sec or not topic or not date: messagebox.showerror("Input", "All fields required."); return
            data = topics_map(); data.setdefault(sec, []).append({"teacher": self.active_user, "topic": topic, "date": date})
            save_json(PATH_TOPICS, data); messagebox.showinfo("Topic", "Added.")
        self.v.button(c, "Save", save, SIDEBAR_BLUE).pack(pady=8)

    def teacher_view_topics(self):
        c = self.container("Topics Covered")
        mysecs = teacher_sections_map().get(self.active_user, [])
        data = topics_map()
        if not mysecs:
            self.v.label(c, "No sections assigned.", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x"); return
        found = False
        for sec in mysecs:
            items = data.get(sec, [])
            if items:
                self.v.label(c, f"Section {sec}", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x", pady=(8, 4))
                for t in items:
                    self.v.label(c, f"{t.get('topic','')} ({t.get('date','')}) — {t.get('teacher','')}", SMALL, NEUTRAL_GRAYBLUE, BG_PANEL, anchor="w").pack(fill="x", pady=2)
                found = True
        if not found:
            self.v.label(c, "No topics recorded yet.", BODY, PRIMARY_DEEP, BG_PANEL, anchor="w").pack(fill="x")

    def teacher_view_assignments(self):
        c = self.container("Submitted Assignments")
        mysecs = teacher_sections_map().get(self.active_user, [])
        cols = ("Section", "Student Roll", "File")
        tree = ttk.Treeview(c, columns=cols, show="headings", height=14)
        for col in cols:
            tree.heading(col, text=col); tree.column(col, anchor="center", width=220 if col!="File" else 320)
        tree.pack(fill="both", expand=True)
        for sec in mysecs:
            sec_dir = os.path.join(PATH_ASSIGNMENTS, sec)
            if not os.path.isdir(sec_dir):
                continue
            for f in os.listdir(sec_dir):
                if f.lower().endswith(".pdf"):
                    roll = os.path.splitext(f)[0]
                    tree.insert("", "end", values=(sec, roll, f))

def launch():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    launch()