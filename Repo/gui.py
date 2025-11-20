from __future__ import annotations

import csv
import hmac
import importlib
import json
import os
import sys
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any, Literal
import login

customUi: Any | None
try:
    customUi = importlib.import_module("customtkinter")
    customUi.set_appearance_mode("light")
    customUi.set_default_color_theme("blue")
    customAvailable = True
except ModuleNotFoundError:
    customUi = None
    customAvailable = False

primaryDeepColor = "#2C3E50"
accentPinkColor = "#FF2F92"
secondaryBlueColor = "#3C5A99"
sidebarStrongBlueColor = "#4A90E2"
neutralGrayBlueColor = "#5D6D7E"
mainBackgroundColor = "#FFFFFF"
panelBackgroundColor = "#F7F9FC"
sidebarBackgroundColor = "#F0F3F8"

headingFontSpec = ("Courier New", 28, "bold")
titleFontSpec = ("Courier New", 20, "bold")
bodyFontSpec = ("Courier New", 13)
buttonFontSpec = ("Courier New", 14, "bold")
smallFontSpec = ("Courier New", 11)

ADMIN_CREATION_PASSWORD = "admin@123"
SECURITY_QUESTIONS = [
    "What is the name of your first pet?",
    "What is the first dish you learned to cook?",
    "What is your favorite book?",
    "What is the first word you said (except mother and father)?",
    "What city were you born in?",
]


class ViewFactory:
    def __init__(self, useCustom: bool):
        self.useCustom = useCustom

    def rootWindow(self):
        if self.useCustom and customUi:
            window = customUi.CTk()
            window.configure(fg_color=mainBackgroundColor)
            return window
        window = tk.Tk()
        window.configure(bg=mainBackgroundColor)
        return window

    def frame(self, parent, background: str, border: bool = False):
        if self.useCustom and customUi:
            borderColor = neutralGrayBlueColor if border else background
            return customUi.CTkFrame(
                parent,
                fg_color=background,
                border_color=borderColor,
                border_width=1 if border else 0,
                corner_radius=12 if border else 8,
            )
        return tk.Frame(
            parent,
            bg=background,
            highlightbackground=neutralGrayBlueColor if border else background,
            highlightthickness=1 if border else 0,
            bd=0,
        )

    def label(
        self,
        parent,
        text: str,
        fontSpec,
        textColor: str = primaryDeepColor,
        background: str = mainBackgroundColor,
        anchor: Literal["n", "ne", "e", "se", "s", "sw", "w", "nw", "center"] = "center",
    ):
        if self.useCustom and customUi:
            return customUi.CTkLabel(
                parent,
                text=text,
                font=fontSpec,
                text_color=textColor,
                fg_color=background,
            )
        return tk.Label(
            parent,
            text=text,
            font=fontSpec,
            fg=textColor,
            bg=background,
            anchor=anchor,
        )

    def button(
        self,
        parent,
        text: str,
        command,
        bgColor: str = accentPinkColor,
        hoverColor: str = secondaryBlueColor,
        textColor: str = primaryDeepColor,
        width: int = 18,
        fontSpec=buttonFontSpec,
    ):
        if self.useCustom and customUi:
            return customUi.CTkButton(
                parent,
                text=text,
                command=command,
                fg_color=bgColor,
                hover_color=hoverColor,
                text_color=textColor,
                font=fontSpec,
                width=width * 6,
            )
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bgColor,
            fg=textColor,
            activebackground=hoverColor,
            activeforeground=textColor,
            relief="flat",
            bd=0,
            font=fontSpec,
            highlightthickness=0,
            width=width,
            pady=8,
        )

    def entry(self, parent, showChar: str | None = None, width: int = 28):
        if self.useCustom and customUi:
            return customUi.CTkEntry(parent, font=bodyFontSpec, show=showChar, width=width * 10)
        entry = tk.Entry(
            parent,
            font=bodyFontSpec,
            show=showChar if showChar else "",
            width=width,
            relief="flat",
            highlightbackground=neutralGrayBlueColor,
            highlightthickness=1,
            bg=panelBackgroundColor,
            fg=primaryDeepColor,
            insertbackground=primaryDeepColor,
        )
        return entry

    def toplevel(self, parent, title: str, size: str = "360x240"):
        if self.useCustom and customUi:
            window = customUi.CTkToplevel(parent)
            window.geometry(size)
            window.title(title)
            window.configure(fg_color=panelBackgroundColor)
            return window
        window = tk.Toplevel(parent)
        window.geometry(size)
        window.title(title)
        window.configure(bg=panelBackgroundColor)
        return window

    def clear(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()


class EduTrackApp:
    def __init__(self, root):
        self.root = root
        self.view = ViewFactory(customAvailable)
        self.root.title("EDUTRACK")
        self.root.geometry("1280x820")
        if customAvailable and hasattr(self.root, "configure"):
            self.root.configure(fg_color=mainBackgroundColor)
        else:
            self.root.configure(bg=mainBackgroundColor)
        self.activeUser = ""
        self.activeRole = ""
        self.sidebarButtons: dict[str, Any] = {}
        self.activeSidebarKey = ""
        self.graphContainer: Any = None
        self.attendanceTree: ttk.Treeview | None = None
        self.attendanceSubjectBox: ttk.Combobox | None = None
        self.attendanceStatusLabel: Any = None
        self.subjectChoiceVar = tk.StringVar()
        self.loadedRoll = ""
        self.baseDir = os.path.dirname(os.path.abspath(__file__))
        self.subjectPath = os.path.join(self.baseDir, "subjects.json")
        self.sectionPath = os.path.join(self.baseDir, "sections.json")
        self.topicPath = os.path.join(self.baseDir, "topics.json")
        self.examPath = os.path.join(self.baseDir, "exam_date.json")
        self.teacherPath = os.path.join(self.baseDir, "teachersections.json")
        self.attendancePath = os.path.join(self.baseDir, "attendance_master.json")
        self.ensureFiles()
        self.users = login.load_users()
        self.subjectData = self.extractSubjectList(self.loadJsonFile(self.subjectPath, []))
        self.sectionData = self.extractSectionList(self.loadJsonFile(self.sectionPath, []))
        self.topicData = self.extractTopicList(self.loadJsonFile(self.topicPath, []))
        self.examData = self.extractExamList(self.loadJsonFile(self.examPath, []))
        self.teacherData = self.extractTeacherList(self.loadJsonFile(self.teacherPath, []))
        self.attendanceData = self.loadJsonFile(
            self.attendancePath,
            {"attendance_records": {}, "metadata": {}},
        )
        self.loginFrame = None
        self.shellFrame = None
        self.sidebarFrame = None
        self.contentFrame = None
        self.configureTreeStyle()
        self.showLogin()

    def ensureFiles(self):
        if not os.path.exists(self.attendancePath):
            with open(self.attendancePath, "w", encoding="utf-8") as file:
                json.dump({"attendance_records": {}, "metadata": {}}, file, indent=2)

    def refreshUsers(self):
        self.users = login.load_users()

    def loadJsonFile(self, path: str, fallback):
        try:
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return fallback
        except json.JSONDecodeError:
            return fallback

    def saveJsonFile(self, path: str, payload):
        with open(path, "w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2)

    def showLogin(self):
        if self.shellFrame:
            self.shellFrame.destroy()
            self.shellFrame = None
        if self.loginFrame:
            self.loginFrame.destroy()
        self.loginFrame = self.view.frame(self.root, mainBackgroundColor, border=True)
        self.loginFrame.place(relx=0.5, rely=0.5, anchor="center")
        brandingFrame = self.view.frame(self.loginFrame, mainBackgroundColor)
        brandingFrame.pack(fill="x", pady=(20, 10), padx=40)
        badge = self.view.label(
            brandingFrame,
            text="EDUTRACK",
            fontSpec=headingFontSpec,
            textColor=primaryDeepColor,
            background=mainBackgroundColor,
        )
        badge.pack(fill="x")
        accentStrip = self.view.frame(brandingFrame, accentPinkColor)
        accentStrip.configure(height=4)
        accentStrip.pack(fill="x", pady=(8, 0))
        formFrame = self.view.frame(self.loginFrame, panelBackgroundColor, border=True)
        formFrame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        welcome = self.view.label(
            formFrame,
            text="Modern campus login portal",
            fontSpec=titleFontSpec,
            textColor=primaryDeepColor,
            background=panelBackgroundColor,
        )
        welcome.pack(pady=(24, 18))
        userLabel = self.view.label(
            formFrame,
            text="Username",
            fontSpec=bodyFontSpec,
            textColor=primaryDeepColor,
            background=panelBackgroundColor,
            anchor="w",
        )
        userLabel.pack(fill="x", padx=30)
        self.userNameEntry = self.view.entry(formFrame)
        self.userNameEntry.pack(fill="x", padx=30, pady=(4, 16))
        passLabel = self.view.label(
            formFrame,
            text="Password",
            fontSpec=bodyFontSpec,
            textColor=primaryDeepColor,
            background=panelBackgroundColor,
            anchor="w",
        )
        passLabel.pack(fill="x", padx=30)
        self.passwordEntry = self.view.entry(formFrame, showChar="*")
        self.passwordEntry.pack(fill="x", padx=30, pady=(4, 24))
        buttonFrame = self.view.frame(formFrame, panelBackgroundColor)
        buttonFrame.pack(fill="x", padx=30, pady=12)
        loginButton = self.view.button(
            buttonFrame,
            text="Login",
            command=self.attemptLogin,
            width=24,
            bgColor=accentPinkColor,
            hoverColor="#ff4fa4",
        )
        loginButton.pack(fill="x", pady=6)
        createButton = self.view.button(
            buttonFrame,
            text="Create Account",
            command=self.openCreateAccountDialog,
            width=24,
            bgColor=sidebarStrongBlueColor,
            hoverColor=secondaryBlueColor,
        )
        createButton.pack(fill="x", pady=6)
        forgotButton = self.view.button(
            buttonFrame,
            text="Forgot Password",
            command=self.openForgotPasswordDialog,
            width=24,
            bgColor=primaryDeepColor,
            hoverColor=secondaryBlueColor,
        )
        forgotButton.pack(fill="x", pady=6)
        self.root.bind("<Return>", lambda _event: self.attemptLogin())
    def setAppRef(self):
        EduTrackApp.appRef = self

    def showRoleAdmin(self, username):
        container = self.prepareContent("Dashboard")
        statsFrame = self.view.frame(container, "#FFFFFF", border=True)
        statsFrame.pack(fill="x", padx=0, pady=8)
        metrics = [
            ("Students", len(self.attendanceData.get("attendance_records", {})), "Onboarded learners"),
            ("Subjects", len(self.subjectData), "Academic offerings"),
            ("Sections", len(self.sectionData), "Active homerooms"),
            ("Teachers", len(self.teacherData), "Faculty mapped"),
        ]
        for title, value, desc in metrics:
            card = self.view.frame(statsFrame, "#FFFFFF", border=True)
            card.pack(side="left", expand=True, fill="both", padx=8, pady=8)
            label = self.view.label(card, text=str(value), fontSpec=headingFontSpec, background="#FFFFFF", textColor=primaryDeepColor)
            label.pack(pady=(18, 4))
            caption = self.view.label(card, text=title.upper(), fontSpec=smallFontSpec, background="#FFFFFF", textColor=neutralGrayBlueColor)
            caption.pack()
            descLabel = self.view.label(card, text=desc, fontSpec=smallFontSpec, background="#FFFFFF", textColor=primaryDeepColor)
            descLabel.pack(pady=(4, 16))
        quickFrame = self.view.frame(container, panelBackgroundColor, border=True)
        quickFrame.pack(fill="x", pady=18)
        quickTitle = self.view.label(quickFrame, text="Admin Menu", fontSpec=bodyFontSpec, background=panelBackgroundColor, textColor=primaryDeepColor, anchor="w")
        quickTitle.pack(fill="x", padx=18, pady=(16, 8))
        quickRow = self.view.frame(quickFrame, panelBackgroundColor)
        quickRow.pack(fill="x", padx=18, pady=(0, 18))
        def openStudentInfo():
            top = self.view.toplevel(self.root, "View Student Info", "420x240")
            frame = self.view.frame(top, panelBackgroundColor)
            frame.pack(fill="both", expand=True, padx=18, pady=18)
            nameLbl = self.view.label(frame, text="Student username", fontSpec=bodyFontSpec, background=panelBackgroundColor, anchor="w")
            nameLbl.pack(fill="x")
            nameEnt = self.view.entry(frame)
            nameEnt.pack(fill="x", pady=8)
            def go():
                studentname = nameEnt.get().strip()
                if not studentname:
                    messagebox.showerror("Input", "Enter username.")
                    return
                import subject, section, exam_date
                rollVal = subject.getRollNumber(studentname, "student")
                secVal = section.getSectionForRoll(rollVal)
                infoTxt = self.view.label(frame, text=f"Roll: {rollVal}\nSection: {secVal}", fontSpec=bodyFontSpec, background=panelBackgroundColor, anchor="w")
                infoTxt.pack(fill="x", pady=8)
                if secVal != "Not assigned":
                    exam_date.viewSectionExamDates(secVal)
            okBtn = self.view.button(frame, text="Show", command=go, width=16)
            okBtn.pack(pady=8)
        def openAnyDashboard():
            top = self.view.toplevel(self.root, "Open Student Dashboard", "420x240")
            frame = self.view.frame(top, panelBackgroundColor)
            frame.pack(fill="both", expand=True, padx=18, pady=18)
            nameLbl = self.view.label(frame, text="Student username", fontSpec=bodyFontSpec, background=panelBackgroundColor, anchor="w")
            nameLbl.pack(fill="x")
            nameEnt = self.view.entry(frame)
            nameEnt.pack(fill="x", pady=8)
            def go():
                studentname = nameEnt.get().strip()
                if not studentname:
                    messagebox.showerror("Input", "Enter username.")
                    return
                self.handleSidebarSelection("Dashboard", self.showWelcomePanel)
                showDashboard("student", studentname)
            okBtn = self.view.button(frame, text="Open", command=go, width=16)
            okBtn.pack(pady=8)
        actions = [
            ("Add subject", "Subjects", self.showSubjectsPanel),
            ("List subjects", "Subjects", self.showSubjectsPanel),
            ("Create section", "Sections", self.showSectionsPanel),
            ("List sections", "Sections", self.showSectionsPanel),
            ("Assign section to student (choose from list)", "Sections", self.showSectionsPanel),
            ("Assign sections to teacher", "Teachers", self.showTeachersPanel),
            ("Set/Update exam dates", "Exams", self.showExamsPanel),
            ("View all exam dates", "Exams", self.showExamsPanel),
            ("View section assignments", "Sections", self.showSectionsPanel),
            ("View student info", "Dashboard", openStudentInfo),
            ("View any student's dashboard", "Dashboard", openAnyDashboard),
        ]
        for text, keyVal, handler in actions:
            btn = self.view.button(quickRow, text=text, command=lambda k=keyVal, h=handler: (self.handleSidebarSelection(k, h), None)[1], bgColor="#E6ECF8", hoverColor="#d4e1ff", width=24)
            btn.pack(fill="x", padx=6, pady=6)
        self.setActiveSidebar("Dashboard")

    
    def attemptLogin(self):
        self.refreshUsers()
        username = self.userNameEntry.get().strip()
        password = self.passwordEntry.get().strip()
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
        self.activeUser = username
        self.activeRole = user.role
        self.setAppRef()
        self.showDashboard()
        showDashboard(self.activeRole, self.activeUser)
        
    def showRoleTeacher(self, username):
        container = self.prepareContent("Dashboard")
        mySections = []
        for entry in self.teacherData:
            if entry.get("teacher", "") == username:
                mySections = entry.get("sections", [])
                break
        studentCount = 0
        secSet = set([s for s in mySections])
        for item in self.sectionData:
            secVal = item.get("section", "")
            if secVal in secSet:
                studentCount += 1
        statsFrame = self.view.frame(container, "#FFFFFF", border=True)
        statsFrame.pack(fill="x", padx=0, pady=8)
        metrics = [
            ("My Sections", len(mySections), "Assigned classes"),
            ("Mapped Students", studentCount, "Learners in my classes"),
        ]
        for title, value, desc in metrics:
            card = self.view.frame(statsFrame, "#FFFFFF", border=True)
            card.pack(side="left", expand=True, fill="both", padx=8, pady=8)
            label = self.view.label(card, text=str(value), fontSpec=headingFontSpec, background="#FFFFFF", textColor=primaryDeepColor)
            label.pack(pady=(18, 4))
            caption = self.view.label(card, text=title.upper(), fontSpec=smallFontSpec, background="#FFFFFF", textColor=neutralGrayBlueColor)
            caption.pack()
            descLabel = self.view.label(card, text=desc, fontSpec=smallFontSpec, background="#FFFFFF", textColor=primaryDeepColor)
            descLabel.pack(pady=(4, 16))
        quickFrame = self.view.frame(container, panelBackgroundColor, border=True)
        quickFrame.pack(fill="x", pady=18)
        quickTitle = self.view.label(quickFrame, text="Teacher Menu", fontSpec=bodyFontSpec, background=panelBackgroundColor, textColor=primaryDeepColor, anchor="w")
        quickTitle.pack(fill="x", padx=18, pady=(16, 8))
        quickRow = self.view.frame(quickFrame, panelBackgroundColor)
        quickRow.pack(fill="x", padx=18, pady=(0, 18))
        def openAssignments():
            import assignments
            assignments.view_assignments(username)
            messagebox.showinfo("Assignments", "Assignment list printed in terminal.")
        actions = [
            ("View my sections", "Teachers", self.showTeachersPanel),
            ("Mark present", "Attendance", self.showAttendancePanel),
            ("Update attendance/ mark absent", "Attendance", self.showAttendancePanel),
            ("View attendance chart", "Attendance", self.showAttendancePanel),
            ("Add topic covered", "Topics", self.showTopicsPanel),
            ("View topics covered", "Topics", self.showTopicsPanel),
            ("View submitted assignments", "Dashboard", openAssignments),
        ]
        for text, keyVal, handler in actions:
            btn = self.view.button(quickRow, text=text, command=lambda k=keyVal, h=handler: (self.handleSidebarSelection(k, h), None)[1], bgColor="#E6ECF8", hoverColor="#d4e1ff", width=22)
            btn.pack(fill="x", padx=6, pady=6)
        self.setActiveSidebar("Dashboard")

    def openCreateAccountDialog(self):
        dialog = self.view.toplevel(self.root, "Create Account", "380x260")
        prompt = self.view.label(
            dialog,
            text="Add a new campus profile",
            fontSpec=titleFontSpec,
            textColor=primaryDeepColor,
            background=panelBackgroundColor,
        )
        prompt.pack(pady=(20, 12))
        nameLabel = self.view.label(
            dialog,
            text="Username",
            fontSpec=bodyFontSpec,
            background=panelBackgroundColor,
            anchor="w",
        )
        nameLabel.pack(fill="x", padx=30)
        nameEntry = self.view.entry(dialog)
        nameEntry.pack(fill="x", padx=30, pady=(4, 16))
        roleLabel = self.view.label(
            dialog,
            text="Role",
            fontSpec=bodyFontSpec,
            background=panelBackgroundColor,
            anchor="w",
        )
        roleLabel.pack(fill="x", padx=30)
        roleVar = tk.StringVar(value="student")
        roleBox = ttk.Combobox(
            dialog,
            textvariable=roleVar,
            values=["student", "teacher", "admin"],
            state="readonly",
        )
        roleBox.pack(fill="x", padx=30, pady=(4, 16))
        passLabel = self.view.label(
            dialog,
            text="Password",
            fontSpec=bodyFontSpec,
            background=panelBackgroundColor,
            anchor="w",
        )
        passLabel.pack(fill="x", padx=30)
        passEntry = self.view.entry(dialog, showChar="*")
        passEntry.pack(fill="x", padx=30, pady=(4, 24))
        adminLabel = self.view.label(
            dialog,
            text="Admin creation password (admin only)",
            fontSpec=smallFontSpec,
            background=panelBackgroundColor,
            anchor="w",
        )
        adminLabel.pack(fill="x", padx=30)
        adminEntry = self.view.entry(dialog, showChar="*")
        adminEntry.pack(fill="x", padx=30, pady=(4, 16))
        questionLabel = self.view.label(
            dialog,
            text="Security question",
            fontSpec=bodyFontSpec,
            background=panelBackgroundColor,
            anchor="w",
        )
        questionLabel.pack(fill="x", padx=30)
        questionVar = tk.StringVar(value=SECURITY_QUESTIONS[0])
        questionBox = ttk.Combobox(
            dialog,
            textvariable=questionVar,
            values=SECURITY_QUESTIONS,
            state="readonly",
        )
        questionBox.pack(fill="x", padx=30, pady=(4, 12))
        answerLabel = self.view.label(
            dialog,
            text="Security answer",
            fontSpec=bodyFontSpec,
            background=panelBackgroundColor,
            anchor="w",
        )
        answerLabel.pack(fill="x", padx=30)
        answerEntry = self.view.entry(dialog)
        answerEntry.pack(fill="x", padx=30, pady=(4, 18))

        def saveAccount():
            name = nameEntry.get().strip()
            secret = passEntry.get().strip()
            role = roleVar.get().strip().lower()
            adminKey = adminEntry.get().strip()
            question = questionVar.get().strip()
            answer = answerEntry.get().strip()
            if not name or not secret or not role or not question or not answer:
                messagebox.showerror("Missing Data", "All fields are required.")
                return
            if role not in ("student", "teacher", "admin"):
                messagebox.showerror("Invalid Role", "Choose student, teacher, or admin.")
                return
            if role == "admin" and adminKey != ADMIN_CREATION_PASSWORD:
                messagebox.showerror("Unauthorized", "Incorrect admin creation password.")
                return
            if len(secret) <= 4:
                messagebox.showerror("Weak Password", "Password must be more than 4 characters.")
                return
            if self.users.find(name):
                messagebox.showerror("Duplicate User", "This username already exists.")
                return
            salt = login.make_salt()
            pwd_hash = login.make_hash(secret, salt)
            ans_salt = login.make_salt()
            ans_hash = login.make_hash(answer, ans_salt)
            if question not in SECURITY_QUESTIONS:
                question = SECURITY_QUESTIONS[0]
            self.users.add(name, role, salt, pwd_hash, question, ans_salt, ans_hash)
            login.save_users(self.users)
            messagebox.showinfo("Account Created", "New account added successfully.")
            dialog.destroy()

        saveButton = self.view.button(
            dialog,
            text="Save Account",
            command=saveAccount,
        )
        saveButton.pack(pady=(0, 24))

    def openForgotPasswordDialog(self):
        dialog = self.view.toplevel(self.root, "Password Help", "380x220")
        infoLabel = self.view.label(
            dialog,
            text="Recover your access",
            fontSpec=titleFontSpec,
            background=panelBackgroundColor,
        )
        infoLabel.pack(pady=(20, 10))
        userLabel = self.view.label(
            dialog,
            text="Username",
            fontSpec=bodyFontSpec,
            background=panelBackgroundColor,
            anchor="w",
        )
        userLabel.pack(fill="x", padx=30)
        userEntry = self.view.entry(dialog)
        userEntry.pack(fill="x", padx=30, pady=(4, 16))
        resetFrameHolder: dict[str, Any] = {"frame": None}

        def handleRecovery():
            username = userEntry.get().strip()
            if not username:
                messagebox.showerror("Missing Data", "Please enter your username.")
                return
            self.refreshUsers()
            user = self.users.find(username)
            if not user:
                messagebox.showerror("Unknown User", "This username is not registered.")
                return
            if resetFrameHolder["frame"]:
                resetFrameHolder["frame"].destroy()
            resetFrame = self.view.frame(dialog, panelBackgroundColor)
            resetFrameHolder["frame"] = resetFrame
            resetFrame.pack(fill="x", padx=30, pady=(8, 20))
            questionLabel = self.view.label(
                resetFrame,
                text=f"Security question:\n{user.question}",
                fontSpec=bodyFontSpec,
                background=panelBackgroundColor,
                anchor="w",
            )
            questionLabel.pack(fill="x", pady=(0, 8))
            answerLabel = self.view.label(
                resetFrame,
                text="Answer",
                fontSpec=bodyFontSpec,
                background=panelBackgroundColor,
                anchor="w",
            )
            answerLabel.pack(fill="x")
            answerEntry = self.view.entry(resetFrame)
            answerEntry.pack(fill="x", pady=(4, 10))
            newPassLabel = self.view.label(
                resetFrame,
                text="New Password",
                fontSpec=bodyFontSpec,
                background=panelBackgroundColor,
                anchor="w",
            )
            newPassLabel.pack(fill="x")
            newPassEntry = self.view.entry(resetFrame, showChar="*")
            newPassEntry.pack(fill="x", pady=(4, 12))

            def saveNewSecret():
                answer = answerEntry.get().strip()
                newSecret = newPassEntry.get().strip()
                if not answer or not newSecret:
                    messagebox.showerror("Missing Data", "Answer and password are required.")
                    return
                if len(newSecret) <= 4:
                    messagebox.showerror("Weak Password", "Password must be more than 4 characters.")
                    return
                if login.make_hash(answer, user.ans_salt) != user.ans_hash:
                    messagebox.showerror("Incorrect Answer", "Security answer does not match.")
                    return
                new_salt = login.make_salt()
                new_hash = login.make_hash(newSecret, new_salt)
                user.salt = new_salt
                user.pwd_hash = new_hash
                login.save_users(self.users)
                messagebox.showinfo("Updated", "Password has been reset.")
                dialog.destroy()

            saveResetButton = self.view.button(
                resetFrame,
                text="Save New Password",
                command=saveNewSecret,
                width=20,
            )
            saveResetButton.pack()

        recoverButton = self.view.button(
            dialog,
            text="Continue",
            command=handleRecovery,
            width=20,
        )
        recoverButton.pack(pady=(0, 24))

    def configureTreeStyle(self):
        self.treeStyle = ttk.Style()
        try:
            self.treeStyle.theme_use("clam")
        except tk.TclError:
            pass
        self.treeStyle.configure(
            "Edu.Treeview",
            background=panelBackgroundColor,
            fieldbackground=panelBackgroundColor,
            foreground=primaryDeepColor,
            rowheight=28,
            bordercolor=neutralGrayBlueColor,
        )
        self.treeStyle.map(
            "Edu.Treeview",
            background=[("selected", sidebarStrongBlueColor)],
            foreground=[("selected", mainBackgroundColor)],
        )
        self.treeStyle.configure(
            "Edu.Treeview.Heading",
            background=sidebarBackgroundColor,
            foreground=primaryDeepColor,
            font=bodyFontSpec,
        )

    def extractSubjectList(self, payload):
        if isinstance(payload, dict) and "subjects" in payload:
            return payload["subjects"]
        if isinstance(payload, list):
            return payload
        return []

    def extractExamList(self, payload):
        if isinstance(payload, dict) and "exam_schedule" in payload:
            return payload["exam_schedule"]
        if isinstance(payload, list):
            return payload
        return []

    def extractSectionList(self, payload):
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            return [{"roll": roll, "section": sec} for roll, sec in payload.items()]
        return []

    def extractTeacherList(self, payload):
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            return [{"teacher": name, "sections": sections} for name, sections in payload.items()]
        return []

    def extractTopicList(self, payload):
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            records = []
            for section, items in payload.items():
                for item in items:
                    record = {
                        "section": section,
                        "teacher": item.get("teacher", ""),
                        "topic": item.get("topic", ""),
                        "date": item.get("date", ""),
                    }
                    records.append(record)
            return records
        return []

    def persistSubjectData(self):
        self.saveJsonFile(self.subjectPath, {"subjects": self.subjectData})

    def persistExamData(self):
        self.saveJsonFile(self.examPath, {"exam_schedule": self.examData})

    def persistSectionData(self):
        payload = {item.get("roll", ""): item.get("section", "") for item in self.sectionData if item.get("roll")}
        self.saveJsonFile(self.sectionPath, payload)

    def persistTeacherData(self):
        payload = {item.get("teacher", ""): item.get("sections", []) for item in self.teacherData if item.get("teacher")}
        self.saveJsonFile(self.teacherPath, payload)

    def persistTopicData(self):
        grouped: dict[str, list] = {}
        for record in self.topicData:
            section = record.get("section", "")
            if not section:
                continue
            grouped.setdefault(section, [])
            grouped[section].append(
                {
                    "teacher": record.get("teacher", ""),
                    "topic": record.get("topic", ""),
                    "date": record.get("date", ""),
                }
            )
        self.saveJsonFile(self.topicPath, grouped)

    def showDashboard(self):
        if self.loginFrame:
            self.loginFrame.destroy()
            self.loginFrame = None
        if self.shellFrame:
            self.shellFrame.destroy()
        self.shellFrame = self.view.frame(self.root, mainBackgroundColor)
        self.shellFrame.pack(fill="both", expand=True)
        headerFrame = self.view.frame(self.shellFrame, mainBackgroundColor, border=True)
        headerFrame.pack(fill="x", padx=24, pady=20)
        titleLabel = self.view.label(
            headerFrame,
            text="EDUTRACK",
            fontSpec=headingFontSpec,
            textColor=primaryDeepColor,
            background=mainBackgroundColor,
        )
        titleLabel.pack(pady=(12, 6))
        subtitle = self.view.label(
            headerFrame,
            text="Unified academic cockpit for attendance, academics, and planning",
            fontSpec=bodyFontSpec,
            textColor=neutralGrayBlueColor,
            background=mainBackgroundColor,
        )
        subtitle.pack(pady=(0, 12))
        bodyFrame = self.view.frame(self.shellFrame, mainBackgroundColor)
        bodyFrame.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        self.sidebarFrame = self.view.frame(bodyFrame, sidebarBackgroundColor, border=True)
        self.sidebarFrame.pack(side="left", fill="y", padx=(0, 16), pady=4)
        self.contentFrame = self.view.frame(bodyFrame, panelBackgroundColor, border=True)
        self.contentFrame.pack(side="right", fill="both", expand=True, pady=4)
        modules = [
            ("Dashboard", self.showWelcomePanel),
            ("Attendance", self.showAttendancePanel),
            ("Subjects", self.showSubjectsPanel),
            ("Sections", self.showSectionsPanel),
            ("Teachers", self.showTeachersPanel),
            ("Exams", self.showExamsPanel),
            ("Topics", self.showTopicsPanel),
        ]
        self.sidebarButtons.clear()
        for name, handler in modules:
            button = self.view.button(
                self.sidebarFrame,
                text=name,
                command=lambda n=name, h=handler: self.handleSidebarSelection(n, h),
                bgColor=sidebarStrongBlueColor,
                hoverColor=secondaryBlueColor,
                width=20,
            )
            button.pack(fill="x", padx=24, pady=6)
            self.sidebarButtons[name] = button
        logoutButton = self.view.button(
            self.sidebarFrame,
            text="Logout",
            command=self.returnToLogin,
            bgColor=accentPinkColor,
            hoverColor=secondaryBlueColor,
            width=20,
        )
        logoutButton.pack(fill="x", padx=24, pady=(20, 6))
        self.showWelcomePanel()
        self.setActiveSidebar("Dashboard")

    def handleSidebarSelection(self, name, action):
        action()
        self.setActiveSidebar(name)

    def setActiveSidebar(self, activeName: str):
        self.activeSidebarKey = activeName
        for name, button in self.sidebarButtons.items():
            isActive = name == activeName
            targetColor = mainBackgroundColor if isActive else sidebarBackgroundColor
            if customAvailable and customUi and isinstance(button, customUi.CTkButton):
                button.configure(
                    fg_color=targetColor,
                    hover_color="#dfe6f5",
                    text_color=primaryDeepColor,
                )
            else:
                button.configure(
                    bg=targetColor,
                    activebackground="#dfe6f5",
                    activeforeground=primaryDeepColor,
                    fg=primaryDeepColor,
                )

    def prepareContent(self, title: str):
        self.view.clear(self.contentFrame)
        titleLabel = self.view.label(
            self.contentFrame,
            text=title,
            fontSpec=titleFontSpec,
            textColor=primaryDeepColor,
            background=panelBackgroundColor,
            anchor="w",
        )
        titleLabel.pack(fill="x", padx=20, pady=(20, 10))
        divider = self.view.frame(self.contentFrame, neutralGrayBlueColor)
        divider.configure(height=2)
        divider.pack(fill="x", padx=20, pady=(0, 10))
        container = self.view.frame(self.contentFrame, panelBackgroundColor)
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        return container

    def showWelcomePanel(self):
        container = self.prepareContent("Dashboard")
        greeting = self.view.label(
            container,
            text=f"Welcome back, {self.activeUser or 'Guest'}",
            fontSpec=bodyFontSpec,
            textColor=primaryDeepColor,
            background=panelBackgroundColor,
            anchor="w",
        )
        greeting.pack(fill="x", pady=(0, 16))
        statsFrame = self.view.frame(container, panelBackgroundColor)
        statsFrame.pack(fill="x")
        metrics = [
            ("Students", len(self.attendanceData.get("attendance_records", {})), "Onboarded learners"),
            ("Subjects", len(self.subjectData), "Academic offerings"),
            ("Sections", len(self.sectionData), "Active homerooms"),
            ("Teachers", len(self.teacherData), "Faculty mapped"),
        ]
        for title, value, desc in metrics:
            card = self.view.frame(statsFrame, "#FFFFFF", border=True)
            card.pack(side="left", expand=True, fill="both", padx=8, pady=8)
            label = self.view.label(
                card,
                text=str(value),
                fontSpec=headingFontSpec,
                background="#FFFFFF",
                textColor=primaryDeepColor,
            )
            label.pack(pady=(18, 4))
            caption = self.view.label(
                card,
                text=title.upper(),
                fontSpec=smallFontSpec,
                background="#FFFFFF",
                textColor=neutralGrayBlueColor,
            )
            caption.pack()
            descLabel = self.view.label(
                card,
                text=desc,
                fontSpec=smallFontSpec,
                background="#FFFFFF",
                textColor=primaryDeepColor,
            )
            descLabel.pack(pady=(4, 16))
        quickFrame = self.view.frame(container, panelBackgroundColor, border=True)
        quickFrame.pack(fill="x", pady=18)
        quickTitle = self.view.label(
            quickFrame,
            text="Quick Actions",
            fontSpec=bodyFontSpec,
            background=panelBackgroundColor,
            textColor=primaryDeepColor,
            anchor="w",
        )
        quickTitle.pack(fill="x", padx=18, pady=(16, 8))
        quickRow = self.view.frame(quickFrame, panelBackgroundColor)
        quickRow.pack(fill="x", padx=18, pady=(0, 18))
        actions = [
            ("Mark Attendance", "Attendance", self.showAttendancePanel),
            ("Manage Subjects", "Subjects", self.showSubjectsPanel),
            ("Assign Sections", "Sections", self.showSectionsPanel),
            ("Plan Exams", "Exams", self.showExamsPanel),
        ]
        for text, sidebarKey, handler in actions:
            btn = self.view.button(
                quickRow,
                text=text,
                command=lambda n=sidebarKey, h=handler: self.handleSidebarSelection(n, h),
                bgColor="#E6ECF8",
                hoverColor="#d4e1ff",
                width=18,
            )
            btn.pack(side="left", expand=True, fill="x", padx=6)
        noteFrame = self.view.frame(container, panelBackgroundColor, border=True)
        noteFrame.pack(fill="both", expand=True, pady=18)
        metadata = self.attendanceData.get("metadata", {})
        lastUpdated = metadata.get("last_updated", "Not recorded")
        academicYear = metadata.get("academic_year", "2024-2025")
        note = self.view.label(
            noteFrame,
            text=f"Attendance ledger last updated on {lastUpdated} for academic year {academicYear}.",
            fontSpec=bodyFontSpec,
            background=panelBackgroundColor,
            textColor=primaryDeepColor,
            anchor="w",
        )
        note.pack(fill="x", padx=18, pady=(18, 8))
        tips = [
            "Sync new sections before assigning subjects.",
            "Use Topics panel to broadcast classroom coverage.",
            "Export attendance weekly to maintain backups.",
        ]
        for tip in tips:
            bullet = self.view.label(
                noteFrame,
                text=f"• {tip}",
                fontSpec=smallFontSpec,
                background=panelBackgroundColor,
                textColor=neutralGrayBlueColor,
                anchor="w",
            )
            bullet.pack(fill="x", padx=28, pady=2)

    def showAttendancePanel(self):
        container = self.prepareContent("Attendance Intelligence")
        formFrame = self.view.frame(container, panelBackgroundColor, border=True)
        formFrame.pack(fill="x", pady=(0, 16))
        rollLabel = self.view.label(
            formFrame,
            text="Roll Number",
            fontSpec=bodyFontSpec,
            background=panelBackgroundColor,
            anchor="w",
        )
        rollLabel.pack(fill="x", padx=18, pady=(16, 4))
        self.rollEntryField = self.view.entry(formFrame, width=24)
        self.rollEntryField.pack(fill="x", padx=18, pady=(0, 12))
        loadButton = self.view.button(
            formFrame,
            text="Load Student",
            command=self.loadAttendanceStudent,
            width=18,
            bgColor=sidebarStrongBlueColor,
            hoverColor=secondaryBlueColor,
        )
        loadButton.pack(pady=(0, 12))
        subjectLabel = self.view.label(
            formFrame,
            text="Subject",
            fontSpec=bodyFontSpec,
            background=panelBackgroundColor,
            anchor="w",
        )
        subjectLabel.pack(fill="x", padx=18, pady=(8, 4))
        self.attendanceSubjectBox = ttk.Combobox(
            formFrame,
            textvariable=self.subjectChoiceVar,
            state="readonly",
            values=[],
        )
        self.attendanceSubjectBox.pack(fill="x", padx=18, pady=(0, 12))
        buttonCluster = self.view.frame(formFrame, panelBackgroundColor)
        buttonCluster.pack(pady=(8, 12))
        presentButton = self.view.button(
            buttonCluster,
            text="Mark Present",
            command=lambda: self.markAttendance(True),
            width=16,
        )
        presentButton.pack(side="left", padx=6)
        absentButton = self.view.button(
            buttonCluster,
            text="Mark Absent",
            command=lambda: self.markAttendance(False),
            width=16,
            bgColor=neutralGrayBlueColor,
            hoverColor=secondaryBlueColor,
        )
        absentButton.pack(side="left", padx=6)
        self.attendanceStatusLabel = self.view.label(
            formFrame,
            text="Load a student to begin marking attendance.",
            fontSpec=smallFontSpec,
            background=panelBackgroundColor,
            textColor=neutralGrayBlueColor,
            anchor="w",
        )
        self.attendanceStatusLabel.pack(fill="x", padx=18, pady=(0, 16))
        tableFrame = self.view.frame(container, panelBackgroundColor, border=True)
        tableFrame.pack(fill="both", expand=True, pady=(0, 16))
        columns = ("Subject", "Name", "Sessions", "Present", "Percent", "Updated")
        self.attendanceTree = ttk.Treeview(
            tableFrame,
            columns=columns,
            show="headings",
            height=10,
            style="Edu.Treeview",
        )
        for column in columns:
            self.attendanceTree.heading(column, text=column)
            self.attendanceTree.column(column, anchor="center", width=130)
        self.attendanceTree.pack(fill="both", expand=True, padx=8, pady=8)
        actionFrame = self.view.frame(container, panelBackgroundColor)
        actionFrame.pack(fill="x", pady=(0, 16))
        graphButton = self.view.button(
            actionFrame,
            text="Show Graph",
            command=self.showAttendanceGraph,
            width=18,
            bgColor=sidebarStrongBlueColor,
            hoverColor=secondaryBlueColor,
        )
        graphButton.pack(side="left", padx=6)
        exportButton = self.view.button(
            actionFrame,
            text="Export Report",
            command=self.exportAttendanceReport,
            width=18,
        )
        exportButton.pack(side="left", padx=6)
        self.graphContainer = self.view.frame(container, panelBackgroundColor, border=True)
        self.graphContainer.pack(fill="both", expand=True)

    def loadAttendanceStudent(self):
        roll = self.rollEntryField.get().strip()
        if not roll:
            messagebox.showerror("Missing Data", "Please enter a roll number.")
            return
        records = self.attendanceData.get("attendance_records", {})
        if roll not in records:
            messagebox.showerror("Not Found", f"No attendance data for roll {roll}.")
            return
        self.loadedRoll = roll
        subjectMap = records[roll].get("subjects", {})
        options = sorted(subjectMap.keys())
        subjectBox = self.attendanceSubjectBox
        if subjectBox:
            subjectBox["values"] = options
            if options:
                subjectBox.current(0)
            else:
                subjectBox.set("")
        if options:
            self.subjectChoiceVar.set(options[0])
        else:
            self.subjectChoiceVar.set("")
        self.refreshAttendanceTable(subjectMap)
        if self.attendanceStatusLabel:
            self.attendanceStatusLabel.configure(text=f"Loaded {roll}. Select a subject to mark attendance.")

    def refreshAttendanceTable(self, subjectMap):
        if not self.attendanceTree:
            return
        for item in self.attendanceTree.get_children():
            self.attendanceTree.delete(item)
        for code, details in subjectMap.items():
            name = details.get("subject_name", code)
            sessions = int(details.get("total_working_days", 0))
            present = int(details.get("total_present_days", 0))
            percent = float(details.get("attendance_percentage", 0.0))
            updated = details.get("last_updated", "-")
            self.attendanceTree.insert(
                "",
                "end",
                values=(code, name, sessions, present, f"{percent:.2f}%", updated),
            )

    def markAttendance(self, wasPresent: bool):
        if not self.loadedRoll:
            messagebox.showerror("No Student", "Load a student before marking attendance.")
            return
        subject = self.subjectChoiceVar.get()
        if not subject:
            messagebox.showerror("No Subject", "Select a subject to continue.")
            return
        records = self.attendanceData.get("attendance_records", {})
        record = records.get(self.loadedRoll, {})
        subjectMap = record.get("subjects", {})
        if subject not in subjectMap:
            messagebox.showerror("Missing Subject", "This subject is not available for the selected student.")
            return
        details = subjectMap[subject]
        workingDays = int(details.get("total_working_days", 0)) + 1
        presentDays = int(details.get("total_present_days", 0)) + (1 if wasPresent else 0)
        percent = round((presentDays / workingDays) * 100, 2) if workingDays else 0.0
        details["total_working_days"] = workingDays
        details["total_present_days"] = presentDays
        details["attendance_percentage"] = percent
        details["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        records[self.loadedRoll]["subjects"][subject] = details
        self.attendanceData["attendance_records"] = records
        metadata = self.attendanceData.setdefault("metadata", {})
        metadata["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        self.saveJsonFile(self.attendancePath, self.attendanceData)
        self.refreshAttendanceTable(subjectMap)
        message = f"{subject} marked {'present' if wasPresent else 'absent'}."
        if self.attendanceStatusLabel:
            self.attendanceStatusLabel.configure(text=message)

    def showAttendanceGraph(self):
        if not self.loadedRoll:
            messagebox.showerror("No Student", "Load a student to view the graph.")
            return
        records = self.attendanceData.get("attendance_records", {})
        record = records.get(self.loadedRoll)
        if not record:
            messagebox.showerror("No Data", "No attendance data found.")
            return
        subjects = record.get("subjects", {})
        if not subjects:
            messagebox.showerror("No Subjects", "No subjects available for graphing.")
            return
        try:
            figureModule = importlib.import_module("matplotlib.figure")
            backendModule = importlib.import_module("matplotlib.backends.backend_tkagg")
            Figure = getattr(figureModule, "Figure")
            FigureCanvasTkAgg = getattr(backendModule, "FigureCanvasTkAgg")
        except (ModuleNotFoundError, AttributeError):
            messagebox.showerror("Missing Library", "matplotlib is required for graphs.")
            return
        if not self.graphContainer:
            return
        self.view.clear(self.graphContainer)
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        names = list(subjects.keys())
        percentages = [subjects[name].get("attendance_percentage", 0.0) for name in names]
        ax.bar(names, percentages, color=sidebarStrongBlueColor)
        ax.set_ylim(0, 100)
        ax.set_ylabel("Percentage")
        ax.set_title(f"Attendance % for {self.loadedRoll}")
        ax.tick_params(axis="x", rotation=45)
        canvas = FigureCanvasTkAgg(fig, master=self.graphContainer)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.pack(fill="both", expand=True)

    def exportAttendanceReport(self):
        records = self.attendanceData.get("attendance_records", {})
        if not records:
            messagebox.showerror("No Data", "No attendance data to export.")
            return
        exportPath = os.path.join(self.baseDir, "attendance_export.csv")
        try:
            with open(exportPath, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Roll", "Subject", "Sessions", "Present", "Percentage", "Updated"])
                for roll, info in records.items():
                    subjects = info.get("subjects", {})
                    for code, details in subjects.items():
                        writer.writerow(
                            [
                                roll,
                                code,
                                details.get("total_working_days", 0),
                                details.get("total_present_days", 0),
                                details.get("attendance_percentage", 0.0),
                                details.get("last_updated", ""),
                            ]
                        )
            messagebox.showinfo("Export Complete", f"Attendance exported to {exportPath}")
        except OSError as error:
            messagebox.showerror("Export Failed", f"Unable to export report: {error}")

    def buildTable(self, parent, columns):
        tableFrame = self.view.frame(parent, panelBackgroundColor, border=True)
        tableFrame.pack(fill="both", expand=True, pady=(0, 16))
        tree = ttk.Treeview(
            tableFrame,
            columns=columns,
            show="headings",
            height=12,
            style="Edu.Treeview",
        )
        for column in columns:
            tree.heading(column, text=column)
            tree.column(column, anchor="center", width=160)
        tree.pack(fill="both", expand=True, padx=8, pady=8)
        return tree

    def showSubjectsPanel(self):
        container = self.prepareContent("Subjects")
        tree = self.buildTable(container, ("Code", "Name"))
        self.subjectData = self.extractSubjectList(self.subjectData)
        for entry in self.subjectData:
            code = entry.get("code") or entry.get("id", "")
            name = entry.get("name", "")
            tree.insert("", "end", values=(code, name))
        buttonFrame = self.view.frame(container, panelBackgroundColor)
        buttonFrame.pack(fill="x")
        addButton = self.view.button(
            buttonFrame,
            text="Add Subject",
            command=lambda: self.addSubject(tree),
            width=16,
        )
        addButton.pack(side="left", padx=4, pady=4)
        editButton = self.view.button(
            buttonFrame,
            text="Edit Subject",
            command=lambda: self.editSubject(tree),
            width=16,
            bgColor=sidebarStrongBlueColor,
            hoverColor=secondaryBlueColor,
        )
        editButton.pack(side="left", padx=4, pady=4)
        deleteButton = self.view.button(
            buttonFrame,
            text="Delete Subject",
            command=lambda: self.deleteSubject(tree),
            width=16,
            bgColor=neutralGrayBlueColor,
            hoverColor=secondaryBlueColor,
        )
        deleteButton.pack(side="left", padx=4, pady=4)

    def addSubject(self, tree):
        dialog = self.view.toplevel(self.root, "Add Subject", "380x240")
        codeLabel = self.view.label(dialog, text="Subject Code", fontSpec=bodyFontSpec, background=panelBackgroundColor, anchor="w")
        codeLabel.pack(fill="x", padx=24, pady=(20, 4))
        codeEntry = self.view.entry(dialog)
        codeEntry.pack(fill="x", padx=24, pady=(0, 12))
        nameLabel = self.view.label(dialog, text="Subject Name", fontSpec=bodyFontSpec, background=panelBackgroundColor, anchor="w")
        nameLabel.pack(fill="x", padx=24, pady=(0, 4))
        nameEntry = self.view.entry(dialog)
        nameEntry.pack(fill="x", padx=24, pady=(0, 16))

        def save():
            code = codeEntry.get().strip()
            name = nameEntry.get().strip()
            if not code or not name:
                messagebox.showerror("Missing Data", "Code and name are required.")
                return
            self.subjectData.append({"code": code, "name": name})
            self.persistSubjectData()
            tree.insert("", "end", values=(code, name))
            dialog.destroy()

        saveButton = self.view.button(dialog, text="Save", command=save, width=16)
        saveButton.pack(pady=(0, 20))

    def editSubject(self, tree):
        selected = tree.focus()
        if not selected:
            messagebox.showerror("Select Row", "Choose a subject to edit.")
            return
        code, name = tree.item(selected, "values")
        dialog = self.view.toplevel(self.root, "Edit Subject", "380x220")
        nameLabel = self.view.label(dialog, text="Subject Name", fontSpec=bodyFontSpec, background=panelBackgroundColor, anchor="w")
        nameLabel.pack(fill="x", padx=24, pady=(20, 4))
        nameEntry = self.view.entry(dialog)
        nameEntry.insert(0, name)
        nameEntry.pack(fill="x", padx=24, pady=(0, 16))

        def save():
            newName = nameEntry.get().strip()
            if not newName:
                messagebox.showerror("Missing Data", "Name cannot be empty.")
                return
            for entry in self.subjectData:
                entryCode = entry.get("code") or entry.get("id")
                if entryCode == code:
                    entry["name"] = newName
            self.persistSubjectData()
            tree.item(selected, values=(code, newName))
            dialog.destroy()

        saveButton = self.view.button(dialog, text="Save Changes", command=save, width=18)
        saveButton.pack(pady=(0, 20))

    def deleteSubject(self, tree):
        selected = tree.focus()
        if not selected:
            messagebox.showerror("Select Row", "Choose a subject to delete.")
            return
        code, _ = tree.item(selected, "values")
        if not messagebox.askyesno("Confirm", f"Delete subject {code}?"):
            return
        self.subjectData = [entry for entry in self.subjectData if (entry.get("code") or entry.get("id")) != code]
        self.persistSubjectData()
        tree.delete(selected)

    def showSectionsPanel(self):
        container = self.prepareContent("Sections")
        tree = self.buildTable(container, ("Roll", "Section"))
        self.sectionData = self.extractSectionList(self.sectionData)
        for entry in self.sectionData:
            tree.insert("", "end", values=(entry.get("roll", ""), entry.get("section", "")))
        buttonFrame = self.view.frame(container, panelBackgroundColor)
        buttonFrame.pack(fill="x")
        addButton = self.view.button(buttonFrame, text="Add Mapping", command=lambda: self.addSection(tree), width=16)
        addButton.pack(side="left", padx=4, pady=4)
        editButton = self.view.button(
            buttonFrame,
            text="Edit Mapping",
            command=lambda: self.editSection(tree),
            width=16,
            bgColor=sidebarStrongBlueColor,
            hoverColor=secondaryBlueColor,
        )
        editButton.pack(side="left", padx=4, pady=4)
        deleteButton = self.view.button(
            buttonFrame,
            text="Delete Mapping",
            command=lambda: self.deleteSection(tree),
            width=16,
            bgColor=neutralGrayBlueColor,
            hoverColor=secondaryBlueColor,
        )
        deleteButton.pack(side="left", padx=4, pady=4)

    def addSection(self, tree):
        dialog = self.view.toplevel(self.root, "Add Section", "380x240")
        rollLabel = self.view.label(dialog, text="Roll Number", fontSpec=bodyFontSpec, background=panelBackgroundColor, anchor="w")
        rollLabel.pack(fill="x", padx=24, pady=(20, 4))
        rollEntry = self.view.entry(dialog)
        rollEntry.pack(fill="x", padx=24, pady=(0, 12))
        sectionLabel = self.view.label(dialog, text="Section Code", fontSpec=bodyFontSpec, background=panelBackgroundColor, anchor="w")
        sectionLabel.pack(fill="x", padx=24, pady=(0, 4))
        sectionEntry = self.view.entry(dialog)
        sectionEntry.pack(fill="x", padx=24, pady=(0, 16))

        def save():
            roll = rollEntry.get().strip()
            section = sectionEntry.get().strip()
            if not roll or not section:
                messagebox.showerror("Missing Data", "Both roll and section are required.")
                return
            self.sectionData.append({"roll": roll, "section": section})
            self.persistSectionData()
            tree.insert("", "end", values=(roll, section))
            dialog.destroy()

        saveButton = self.view.button(dialog, text="Save", command=save, width=16)
        saveButton.pack(pady=(0, 20))

    def editSection(self, tree):
        selected = tree.focus()
        if not selected:
            messagebox.showerror("Select Row", "Choose a mapping to edit.")
            return
        roll, section = tree.item(selected, "values")
        dialog = self.view.toplevel(self.root, "Edit Section", "380x220")
        sectionLabel = self.view.label(dialog, text="Section Code", fontSpec=bodyFontSpec, background=panelBackgroundColor, anchor="w")
        sectionLabel.pack(fill="x", padx=24, pady=(20, 4))
        sectionEntry = self.view.entry(dialog)
        sectionEntry.insert(0, section)
        sectionEntry.pack(fill="x", padx=24, pady=(0, 16))

        def save():
            value = sectionEntry.get().strip()
            if not value:
                messagebox.showerror("Missing Data", "Section cannot be empty.")
                return
            for entry in self.sectionData:
                if entry.get("roll") == roll:
                    entry["section"] = value
            self.persistSectionData()
            tree.item(selected, values=(roll, value))
            dialog.destroy()

        saveButton = self.view.button(dialog, text="Save Changes", command=save, width=18)
        saveButton.pack(pady=(0, 20))

    def deleteSection(self, tree):
        selected = tree.focus()
        if not selected:
            messagebox.showerror("Select Row", "Choose a mapping to delete.")
            return
        roll, _ = tree.item(selected, "values")
        if not messagebox.askyesno("Confirm", f"Delete mapping for roll {roll}?"):
            return
        self.sectionData = [entry for entry in self.sectionData if entry.get("roll") != roll]
        self.persistSectionData()
        tree.delete(selected)

    def showTeachersPanel(self):
        container = self.prepareContent("Teachers")
        tree = self.buildTable(container, ("Teacher", "Sections"))
        self.teacherData = self.extractTeacherList(self.teacherData)
        for entry in self.teacherData:
            tree.insert("", "end", values=(entry.get("teacher", ""), ", ".join(entry.get("sections", []))))
        buttonFrame = self.view.frame(container, panelBackgroundColor)
        buttonFrame.pack(fill="x")
        addButton = self.view.button(buttonFrame, text="Add Teacher", command=lambda: self.addTeacher(tree), width=16)
        addButton.pack(side="left", padx=4, pady=4)
        editButton = self.view.button(
            buttonFrame,
            text="Edit Teacher",
            command=lambda: self.editTeacher(tree),
            width=16,
            bgColor=sidebarStrongBlueColor,
            hoverColor=secondaryBlueColor,
        )
        editButton.pack(side="left", padx=4, pady=4)
        deleteButton = self.view.button(
            buttonFrame,
            text="Delete Teacher",
            command=lambda: self.deleteTeacher(tree),
            width=16,
            bgColor=neutralGrayBlueColor,
            hoverColor=secondaryBlueColor,
        )
        deleteButton.pack(side="left", padx=4, pady=4)

    def addTeacher(self, tree):
        dialog = self.view.toplevel(self.root, "Add Teacher", "380x240")
        nameLabel = self.view.label(dialog, text="Teacher Name", fontSpec=bodyFontSpec, background=panelBackgroundColor, anchor="w")
        nameLabel.pack(fill="x", padx=24, pady=(20, 4))
        nameEntry = self.view.entry(dialog)
        nameEntry.pack(fill="x", padx=24, pady=(0, 12))
        sectionsLabel = self.view.label(dialog, text="Sections (comma separated)", fontSpec=bodyFontSpec, background=panelBackgroundColor, anchor="w")
        sectionsLabel.pack(fill="x", padx=24, pady=(0, 4))
        sectionsEntry = self.view.entry(dialog)
        sectionsEntry.pack(fill="x", padx=24, pady=(0, 16))

        def save():
            name = nameEntry.get().strip()
            sections = [item.strip() for item in sectionsEntry.get().split(",") if item.strip()]
            if not name:
                messagebox.showerror("Missing Data", "Name cannot be empty.")
                return
            self.teacherData.append({"teacher": name, "sections": sections})
            self.persistTeacherData()
            tree.insert("", "end", values=(name, ", ".join(sections)))
            dialog.destroy()

        saveButton = self.view.button(dialog, text="Save", command=save, width=16)
        saveButton.pack(pady=(0, 20))

    def editTeacher(self, tree):
        selected = tree.focus()
        if not selected:
            messagebox.showerror("Select Row", "Choose a teacher to edit.")
            return
        name, sections = tree.item(selected, "values")
        dialog = self.view.toplevel(self.root, "Edit Teacher", "380x220")
        sectionsLabel = self.view.label(dialog, text="Sections (comma separated)", fontSpec=bodyFontSpec, background=panelBackgroundColor, anchor="w")
        sectionsLabel.pack(fill="x", padx=24, pady=(20, 4))
        sectionsEntry = self.view.entry(dialog)
        sectionsEntry.insert(0, sections)
        sectionsEntry.pack(fill="x", padx=24, pady=(0, 16))

        def save():
            values = [item.strip() for item in sectionsEntry.get().split(",") if item.strip()]
            for entry in self.teacherData:
                if entry.get("teacher") == name:
                    entry["sections"] = values
            self.persistTeacherData()
            tree.item(selected, values=(name, ", ".join(values)))
            dialog.destroy()

        saveButton = self.view.button(dialog, text="Save Changes", command=save, width=18)
        saveButton.pack(pady=(0, 20))

    def deleteTeacher(self, tree):
        selected = tree.focus()
        if not selected:
            messagebox.showerror("Select Row", "Choose a teacher to delete.")
            return
        name, _ = tree.item(selected, "values")
        if not messagebox.askyesno("Confirm", f"Delete teacher {name}?"):
            return
        self.teacherData = [entry for entry in self.teacherData if entry.get("teacher") != name]
        self.persistTeacherData()
        tree.delete(selected)

    def showExamsPanel(self):
        container = self.prepareContent("Exams")
        tree = self.buildTable(container, ("Code", "Name", "Exam Date"))
        for entry in self.examData:
            tree.insert("", "end", values=(entry.get("subject_code", ""), entry.get("subject_name", ""), entry.get("exam_date", "")))
        buttonFrame = self.view.frame(container, panelBackgroundColor)
        buttonFrame.pack(fill="x")
        addButton = self.view.button(buttonFrame, text="Add Exam", command=lambda: self.addExam(tree), width=16)
        addButton.pack(side="left", padx=4, pady=4)
        editButton = self.view.button(
            buttonFrame,
            text="Edit Exam",
            command=lambda: self.editExam(tree),
            width=16,
            bgColor=sidebarStrongBlueColor,
            hoverColor=secondaryBlueColor,
        )
        editButton.pack(side="left", padx=4, pady=4)
        deleteButton = self.view.button(
            buttonFrame,
            text="Delete Exam",
            command=lambda: self.deleteExam(tree),
            width=16,
            bgColor=neutralGrayBlueColor,
            hoverColor=secondaryBlueColor,
        )
        deleteButton.pack(side="left", padx=4, pady=4)

    def addExam(self, tree):
        dialog = self.view.toplevel(self.root, "Add Exam", "420x260")
        codeLabel = self.view.label(dialog, text="Subject Code", fontSpec=bodyFontSpec, background=panelBackgroundColor, anchor="w")
        codeLabel.pack(fill="x", padx=24, pady=(20, 4))
        codeEntry = self.view.entry(dialog)
        codeEntry.pack(fill="x", padx=24, pady=(0, 12))
        nameLabel = self.view.label(dialog, text="Subject Name", fontSpec=bodyFontSpec, background=panelBackgroundColor, anchor="w")
        nameLabel.pack(fill="x", padx=24, pady=(0, 4))
        nameEntry = self.view.entry(dialog)
        nameEntry.pack(fill="x", padx=24, pady=(0, 12))
        dateLabel = self.view.label(dialog, text="Exam Date (YYYY-MM-DD)", fontSpec=bodyFontSpec, background=panelBackgroundColor, anchor="w")
        dateLabel.pack(fill="x", padx=24, pady=(0, 4))
        dateEntry = self.view.entry(dialog)
        dateEntry.pack(fill="x", padx=24, pady=(0, 16))

        def save():
            code = codeEntry.get().strip()
            name = nameEntry.get().strip()
            date = dateEntry.get().strip()
            if not code or not name or not date:
                messagebox.showerror("Missing Data", "All fields are required.")
                return
            record = {"subject_code": code, "subject_name": name, "exam_date": date}
            self.examData.append(record)
            self.persistExamData()
            tree.insert("", "end", values=(code, name, date))
            dialog.destroy()

        saveButton = self.view.button(dialog, text="Save Exam", command=save, width=18)
        saveButton.pack(pady=(0, 20))

    def editExam(self, tree):
        selected = tree.focus()
        if not selected:
            messagebox.showerror("Select Row", "Choose an exam to edit.")
            return
        code, name, date = tree.item(selected, "values")
        dialog = self.view.toplevel(self.root, "Edit Exam", "420x240")
        dateLabel = self.view.label(dialog, text="Exam Date (YYYY-MM-DD)", fontSpec=bodyFontSpec, background=panelBackgroundColor, anchor="w")
        dateLabel.pack(fill="x", padx=24, pady=(20, 4))
        dateEntry = self.view.entry(dialog)
        dateEntry.insert(0, date)
        dateEntry.pack(fill="x", padx=24, pady=(0, 16))

        def save():
            value = dateEntry.get().strip()
            if not value:
                messagebox.showerror("Missing Data", "Date cannot be empty.")
                return
            for entry in self.examData:
                if entry.get("subject_code") == code:
                    entry["subject_name"] = name
                    entry["exam_date"] = value
            self.persistExamData()
            tree.item(selected, values=(code, name, value))
            dialog.destroy()

        saveButton = self.view.button(dialog, text="Save Changes", command=save, width=18)
        saveButton.pack(pady=(0, 20))

    def deleteExam(self, tree):
        selected = tree.focus()
        if not selected:
            messagebox.showerror("Select Row", "Choose an exam to delete.")
            return
        code, _, _ = tree.item(selected, "values")
        if not messagebox.askyesno("Confirm", f"Delete exam for {code}?"):
            return
        self.examData = [entry for entry in self.examData if entry.get("subject_code") != code]
        self.persistExamData()
        tree.delete(selected)

    def showTopicsPanel(self):
        container = self.prepareContent("Topics")
        tree = self.buildTable(container, ("Section", "Teacher", "Topic", "Date"))
        for entry in self.topicData:
            tree.insert("", "end", values=(entry.get("section", ""), entry.get("teacher", ""), entry.get("topic", ""), entry.get("date", "")))
        buttonFrame = self.view.frame(container, panelBackgroundColor)
        buttonFrame.pack(fill="x")
        addButton = self.view.button(buttonFrame, text="Add Topic", command=lambda: self.addTopic(tree), width=16)
        addButton.pack(side="left", padx=4, pady=4)
        editButton = self.view.button(
            buttonFrame,
            text="Edit Topic",
            command=lambda: self.editTopic(tree),
            width=16,
            bgColor=sidebarStrongBlueColor,
            hoverColor=secondaryBlueColor,
        )
        editButton.pack(side="left", padx=4, pady=4)
        deleteButton = self.view.button(
            buttonFrame,
            text="Delete Topic",
            command=lambda: self.deleteTopic(tree),
            width=16,
            bgColor=neutralGrayBlueColor,
            hoverColor=secondaryBlueColor,
        )
        deleteButton.pack(side="left", padx=4, pady=4)

    def addTopic(self, tree):
        dialog = self.view.toplevel(self.root, "Add Topic", "420x280")
        sectionLabel = self.view.label(dialog, text="Section Code", fontSpec=bodyFontSpec, background=panelBackgroundColor, anchor="w")
        sectionLabel.pack(fill="x", padx=24, pady=(20, 4))
        sectionEntry = self.view.entry(dialog)
        sectionEntry.pack(fill="x", padx=24, pady=(0, 12))
        teacherLabel = self.view.label(dialog, text="Teacher Name", fontSpec=bodyFontSpec, background=panelBackgroundColor, anchor="w")
        teacherLabel.pack(fill="x", padx=24, pady=(0, 4))
        teacherEntry = self.view.entry(dialog)
        teacherEntry.pack(fill="x", padx=24, pady=(0, 12))
        topicLabel = self.view.label(dialog, text="Topic Title", fontSpec=bodyFontSpec, background=panelBackgroundColor, anchor="w")
        topicLabel.pack(fill="x", padx=24, pady=(0, 4))
        topicEntry = self.view.entry(dialog)
        topicEntry.pack(fill="x", padx=24, pady=(0, 12))
        dateLabel = self.view.label(dialog, text="Delivery Date (DD/MM/YYYY)", fontSpec=bodyFontSpec, background=panelBackgroundColor, anchor="w")
        dateLabel.pack(fill="x", padx=24, pady=(0, 4))
        dateEntry = self.view.entry(dialog)
        dateEntry.pack(fill="x", padx=24, pady=(0, 16))

        def save():
            payload = {
                "section": sectionEntry.get().strip(),
                "teacher": teacherEntry.get().strip(),
                "topic": topicEntry.get().strip(),
                "date": dateEntry.get().strip(),
            }
            if not all(payload.values()):
                messagebox.showerror("Missing Data", "All fields are required.")
                return
            self.topicData.append(payload)
            self.persistTopicData()
            tree.insert("", "end", values=(payload["section"], payload["teacher"], payload["topic"], payload["date"]))
            dialog.destroy()

        saveButton = self.view.button(dialog, text="Save Topic", command=save, width=18)
        saveButton.pack(pady=(0, 20))

    def editTopic(self, tree):
        selected = tree.focus()
        if not selected:
            messagebox.showerror("Select Row", "Choose a topic to edit.")
            return
        section, teacher, topic, date = tree.item(selected, "values")
        dialog = self.view.toplevel(self.root, "Edit Topic", "420x260")
        topicLabel = self.view.label(dialog, text="Topic Title", fontSpec=bodyFontSpec, background=panelBackgroundColor, anchor="w")
        topicLabel.pack(fill="x", padx=24, pady=(20, 4))
        topicEntry = self.view.entry(dialog)
        topicEntry.insert(0, topic)
        topicEntry.pack(fill="x", padx=24, pady=(0, 12))
        dateLabel = self.view.label(dialog, text="Delivery Date (DD/MM/YYYY)", fontSpec=bodyFontSpec, background=panelBackgroundColor, anchor="w")
        dateLabel.pack(fill="x", padx=24, pady=(0, 4))
        dateEntry = self.view.entry(dialog)
        dateEntry.insert(0, date)
        dateEntry.pack(fill="x", padx=24, pady=(0, 16))

        def save():
            newTopic = topicEntry.get().strip()
            newDate = dateEntry.get().strip()
            if not newTopic or not newDate:
                messagebox.showerror("Missing Data", "All fields are required.")
                return
            for item in self.topicData:
                if item.get("section") == section and item.get("topic") == topic:
                    item["topic"] = newTopic
                    item["date"] = newDate
            self.persistTopicData()
            tree.item(selected, values=(section, teacher, newTopic, newDate))
            dialog.destroy()

        saveButton = self.view.button(dialog, text="Save Changes", command=save, width=18)
        saveButton.pack(pady=(0, 20))

    def deleteTopic(self, tree):
        selected = tree.focus()
        if not selected:
            messagebox.showerror("Select Row", "Choose a topic to delete.")
            return
        section, _, topic, _ = tree.item(selected, "values")
        if not messagebox.askyesno("Confirm", f"Delete topic {topic} for section {section}?"):
            return
        self.topicData = [item for item in self.topicData if not (item.get("section") == section and item.get("topic") == topic)]
        self.persistTopicData()
        tree.delete(selected)

    def returnToLogin(self):
        self.activeUser = ""
        if self.shellFrame:
            self.shellFrame.destroy()
            self.shellFrame = None
        self.showLogin()

def showDashboard(role, username):
    app = getattr(EduTrackApp, "appRef", None)
    if not app:
        return
    r = (role or "").strip().lower()
    if r == "admin":
        app.showRoleAdmin(username)
    elif r == "teacher":
        app.showRoleTeacher(username)
    elif r == "student":
        app.showRoleStudent(username)
def launchGui() -> int:
    factory = ViewFactory(customAvailable)
    try:
        root = factory.rootWindow()
    except tk.TclError as error:
        print("Unable to initialise Tk window:", error)
        return 1
    EduTrackApp(root)
    try:
        root.mainloop()
    except tk.TclError as error:
        print("Tk runtime error:", error)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(launchGui())
