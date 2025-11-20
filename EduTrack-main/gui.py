import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog

# Attempt to import customtkinter for modern UI; fallback to tkinter if not available
try:
    import customtkinter as ctk
    CTk = ctk.CTk
    CTkFrame = ctk.CTkFrame
    CTkLabel = ctk.CTkLabel
    CTkButton = ctk.CTkButton
    CTkEntry = ctk.CTkEntry
    CTkOptionMenu = ctk.CTkOptionMenu
    CTkSegmentedButton = ctk.CTkSegmentedButton
    CTkCheckBox = ctk.CTkCheckBox
    BooleanVar = tk.BooleanVar
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    CUSTOM = True
except ImportError:
    CTk = tk.Tk
    CTkFrame = tk.Frame
    CTkLabel = tk.Label
    CTkButton = tk.Button
    CTkEntry = tk.Entry
    CTkOptionMenu = ttk.Combobox
    CTkSegmentedButton = None
    CTkCheckBox = tk.Checkbutton
    BooleanVar = tk.BooleanVar
    CUSTOM = False

# Common font and colors
FONT_NAME = "Courier New"
HEADER_BG = "#6A5ACD"   # Purple theme
HEADER_FG = "#FF69B4"   # Pink theme
BUTTON_BG = "#FF69B4"
BUTTON_FG = "#FFFFFF"
SIDEBAR_BG = "#6A5ACD"
CONTENT_BG = "#FFFFFF"

class EduTrackApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EduTrack - Student ERP System")
        self.root.geometry("1024x768")
        # File paths
        self.userdata_file = "userdata.bin"
        self.subjects_file = "subjects.json"
        self.sections_file = "sections.json"
        self.topics_file = "topics.json"
        self.exams_file = "exam_date.json"
        self.teachersections_file = "teachersections.json"
        self.attendance_file = "attendance_master.json"
        self.rollnumbers_file = "rollnumbers.json"
        # Load data
        self.load_user_data()
        self.subjects_data = self.load_data(self.subjects_file)
        self.sections_data = self.load_data(self.sections_file)
        self.topics_data = self.load_data(self.topics_file)
        self.exams_data = self.load_data(self.exams_file)
        self.teachers_data = self.load_data(self.teachersections_file)
        self.attendance_data = self.load_data(self.attendance_file)
        # Initialize frames
        self.login_frame = None
        self.dashboard_frame = None
        self.show_login()

    def load_user_data(self):
        try:
            with open(self.userdata_file, 'r') as f:
                self.userdata = json.load(f)
        except Exception:
            self.userdata = {}

    def save_user_data(self):
        with open(self.userdata_file, 'w') as f:
            json.dump(self.userdata, f)

    def load_data(self, filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception:
            return []

    def save_data(self, filename, data):
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def show_login(self):
        if self.dashboard_frame:
            self.dashboard_frame.destroy()
        # Login Frame
        self.login_frame = CTkFrame(self.root, fg_color=HEADER_BG if CUSTOM else HEADER_BG)
        self.login_frame.pack(expand=True)
        # Title
        if CUSTOM:
            title_label = CTkLabel(self.login_frame, text="EduTrack Login", font=(FONT_NAME, 18),
                                   fg_color=HEADER_BG, text_color=HEADER_FG)
        else:
            title_label = tk.Label(self.login_frame, text="EduTrack Login", font=(FONT_NAME, 18),
                                   bg=HEADER_BG, fg=HEADER_FG)
        title_label.pack(pady=20)
        # Username
        if CUSTOM:
            user_label = CTkLabel(self.login_frame, text="Username:", font=(FONT_NAME, 12), fg_color=HEADER_BG, text_color="#000")
        else:
            user_label = tk.Label(self.login_frame, text="Username:", font=(FONT_NAME, 12), bg=HEADER_BG, fg="#000")
        user_label.pack(pady=(10,0))
        self.username_entry = CTkEntry(self.login_frame, font=(FONT_NAME, 12))
        self.username_entry.pack()
        # Password
        if CUSTOM:
            pass_label = CTkLabel(self.login_frame, text="Password:", font=(FONT_NAME, 12), fg_color=HEADER_BG, text_color="#000")
        else:
            pass_label = tk.Label(self.login_frame, text="Password:", font=(FONT_NAME, 12), bg=HEADER_BG, fg="#000")
        pass_label.pack(pady=(10,0))
        self.password_entry = CTkEntry(self.login_frame, font=(FONT_NAME, 12), show="*")
        self.password_entry.pack()
        # Buttons
        if CUSTOM:
            login_btn = CTkButton(self.login_frame, text="Login", font=(FONT_NAME, 12),
                                  fg_color=BUTTON_BG, text_color=BUTTON_FG, command=self.login)
            create_btn = CTkButton(self.login_frame, text="Create Account", font=(FONT_NAME, 12),
                                   fg_color=BUTTON_BG, text_color=BUTTON_FG, command=self.create_account)
            forgot_btn = CTkButton(self.login_frame, text="Forgot Password", font=(FONT_NAME, 12),
                                   fg_color=BUTTON_BG, text_color=BUTTON_FG, command=self.forgot_password)
        else:
            login_btn = tk.Button(self.login_frame, text="Login", font=(FONT_NAME, 12),
                                  bg=BUTTON_BG, fg=BUTTON_FG, command=self.login)
            create_btn = tk.Button(self.login_frame, text="Create Account", font=(FONT_NAME, 12),
                                   bg=BUTTON_BG, fg=BUTTON_FG, command=self.create_account)
            forgot_btn = tk.Button(self.login_frame, text="Forgot Password", font=(FONT_NAME, 12),
                                   bg=BUTTON_BG, fg=BUTTON_FG, command=self.forgot_password)
        login_btn.pack(pady=(15,5))
        create_btn.pack(pady=5)
        forgot_btn.pack(pady=5)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            return
        if username in self.userdata and self.userdata[username] == password:
            self.show_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def create_account(self):
        if CUSTOM:
            win = ctk.CTkToplevel(self.root)
        else:
            win = tk.Toplevel(self.root)
        win.title("Create Account")
        win.geometry("300x200")
        if CUSTOM:
            lbl1 = CTkLabel(win, text="New Username:", font=(FONT_NAME, 12), fg_color=SIDEBAR_BG, text_color="#000")
        else:
            lbl1 = tk.Label(win, text="New Username:", font=(FONT_NAME, 12), bg=SIDEBAR_BG, fg="#000")
        lbl1.pack(pady=(10,0))
        new_user_entry = CTkEntry(win, font=(FONT_NAME, 12))
        new_user_entry.pack(pady=5)
        if CUSTOM:
            lbl2 = CTkLabel(win, text="New Password:", font=(FONT_NAME, 12), fg_color=SIDEBAR_BG, text_color="#000")
        else:
            lbl2 = tk.Label(win, text="New Password:", font=(FONT_NAME, 12), bg=SIDEBAR_BG, fg="#000")
        lbl2.pack(pady=(10,0))
        new_pass_entry = CTkEntry(win, font=(FONT_NAME, 12), show="*")
        new_pass_entry.pack(pady=5)
        def add_user():
            new_user = new_user_entry.get().strip()
            new_pass = new_pass_entry.get().strip()
            if not new_user or not new_pass:
                messagebox.showerror("Error", "Fields cannot be empty")
                return
            if new_user in self.userdata:
                messagebox.showerror("Error", "User already exists")
                return
            self.userdata[new_user] = new_pass
            self.save_user_data()
            messagebox.showinfo("Success", "Account created successfully")
            win.destroy()
        if CUSTOM:
            save_btn = CTkButton(win, text="Create", font=(FONT_NAME, 12),
                                 fg_color=BUTTON_BG, text_color=BUTTON_FG, command=add_user)
        else:
            save_btn = tk.Button(win, text="Create", font=(FONT_NAME, 12),
                                 bg=BUTTON_BG, fg=BUTTON_FG, command=add_user)
        save_btn.pack(pady=10)

    def forgot_password(self):
        if CUSTOM:
            win = ctk.CTkToplevel(self.root)
        else:
            win = tk.Toplevel(self.root)
        win.title("Forgot Password")
        win.geometry("300x150")
        if CUSTOM:
            lbl = CTkLabel(win, text="Enter Username:", font=(FONT_NAME, 12), fg_color=SIDEBAR_BG, text_color="#000")
        else:
            lbl = tk.Label(win, text="Enter Username:", font=(FONT_NAME, 12), bg=SIDEBAR_BG, fg="#000")
        lbl.pack(pady=(10,0))
        user_entry = CTkEntry(win, font=(FONT_NAME, 12))
        user_entry.pack(pady=5)
        def retrieve():
            user = user_entry.get().strip()
            if user in self.userdata:
                messagebox.showinfo("Password", f"Password for {user}: {self.userdata[user]}")
                win.destroy()
            else:
                messagebox.showerror("Error", "User not found")
        if CUSTOM:
            retrieve_btn = CTkButton(win, text="Retrieve", font=(FONT_NAME, 12),
                                     fg_color=BUTTON_BG, text_color=BUTTON_FG, command=retrieve)
        else:
            retrieve_btn = tk.Button(win, text="Retrieve", font=(FONT_NAME, 12),
                                     bg=BUTTON_BG, fg=BUTTON_FG, command=retrieve)
        retrieve_btn.pack(pady=10)

    def show_dashboard(self):
        if self.login_frame:
            self.login_frame.destroy()
        self.dashboard_frame = CTkFrame(self.root, fg_color=CONTENT_BG if CUSTOM else CONTENT_BG)
        self.dashboard_frame.pack(fill="both", expand=True)
        # Header
        if CUSTOM:
            header_frame = CTkFrame(self.dashboard_frame, fg_color=HEADER_BG)
            header_label = CTkLabel(header_frame, text="EDUTRACK", font=(FONT_NAME, 24), fg_color=HEADER_BG, text_color=BUTTON_FG)
        else:
            header_frame = tk.Frame(self.dashboard_frame, bg=HEADER_BG)
            header_label = tk.Label(header_frame, text="EDUTRACK", font=(FONT_NAME, 24), bg=HEADER_BG, fg=BUTTON_FG)
        header_frame.pack(side="top", fill="x")
        header_label.pack(pady=10)
        # Sidebar
        if CUSTOM:
            sidebar_frame = CTkFrame(self.dashboard_frame, fg_color=SIDEBAR_BG)
        else:
            sidebar_frame = tk.Frame(self.dashboard_frame, bg=SIDEBAR_BG)
        sidebar_frame.pack(side="left", fill="y")
        self.content_frame = CTkFrame(self.dashboard_frame, fg_color=CONTENT_BG if CUSTOM else CONTENT_BG)
        self.content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        # Sidebar buttons
        if CUSTOM:
            btn_att = CTkButton(sidebar_frame, text="Attendance", font=(FONT_NAME, 12),
                                fg_color=BUTTON_BG, text_color=BUTTON_FG, command=self.show_attendance)
            btn_sub = CTkButton(sidebar_frame, text="Subjects", font=(FONT_NAME, 12),
                                fg_color=BUTTON_BG, text_color=BUTTON_FG, command=self.show_subjects)
            btn_sec = CTkButton(sidebar_frame, text="Sections", font=(FONT_NAME, 12),
                                fg_color=BUTTON_BG, text_color=BUTTON_FG, command=self.show_sections)
            btn_tea = CTkButton(sidebar_frame, text="Teachers", font=(FONT_NAME, 12),
                                fg_color=BUTTON_BG, text_color=BUTTON_FG, command=self.show_teachers)
            btn_exm = CTkButton(sidebar_frame, text="Exams", font=(FONT_NAME, 12),
                                fg_color=BUTTON_BG, text_color=BUTTON_FG, command=self.show_exams)
            btn_top = CTkButton(sidebar_frame, text="Topics", font=(FONT_NAME, 12),
                                fg_color=BUTTON_BG, text_color=BUTTON_FG, command=self.show_topics)
            btn_logout = CTkButton(sidebar_frame, text="Logout", font=(FONT_NAME, 12),
                                   fg_color=BUTTON_BG, text_color=BUTTON_FG, command=self.logout)
            btn_quit = CTkButton(sidebar_frame, text="Quit", font=(FONT_NAME, 12),
                                 fg_color=BUTTON_BG, text_color=BUTTON_FG, command=self.root.quit)
        else:
            btn_att = tk.Button(sidebar_frame, text="Attendance", font=(FONT_NAME, 12),
                                bg=BUTTON_BG, fg=BUTTON_FG, command=self.show_attendance)
            btn_sub = tk.Button(sidebar_frame, text="Subjects", font=(FONT_NAME, 12),
                                bg=BUTTON_BG, fg=BUTTON_FG, command=self.show_subjects)
            btn_sec = tk.Button(sidebar_frame, text="Sections", font=(FONT_NAME, 12),
                                bg=BUTTON_BG, fg=BUTTON_FG, command=self.show_sections)
            btn_tea = tk.Button(sidebar_frame, text="Teachers", font=(FONT_NAME, 12),
                                bg=BUTTON_BG, fg=BUTTON_FG, command=self.show_teachers)
            btn_exm = tk.Button(sidebar_frame, text="Exams", font=(FONT_NAME, 12),
                                bg=BUTTON_BG, fg=BUTTON_FG, command=self.show_exams)
            btn_top = tk.Button(sidebar_frame, text="Topics", font=(FONT_NAME, 12),
                                bg=BUTTON_BG, fg=BUTTON_FG, command=self.show_topics)
            btn_logout = tk.Button(sidebar_frame, text="Logout", font=(FONT_NAME, 12),
                                   bg=BUTTON_BG, fg=BUTTON_FG, command=self.logout)
            btn_quit = tk.Button(sidebar_frame, text="Quit", font=(FONT_NAME, 12),
                                 bg=BUTTON_BG, fg=BUTTON_FG, command=self.root.quit)
        btn_att.pack(pady=5, padx=5)
        btn_sub.pack(pady=5, padx=5)
        btn_sec.pack(pady=5, padx=5)
        btn_tea.pack(pady=5, padx=5)
        btn_exm.pack(pady=5, padx=5)
        btn_top.pack(pady=5, padx=5)
        btn_logout.pack(pady=20, padx=5)
        btn_quit.pack(pady=5, padx=5)

    def logout(self):
        if self.dashboard_frame:
            self.dashboard_frame.destroy()
        self.show_login()

    def show_attendance(self):
        self.clear_frame(self.content_frame)
        if CUSTOM:
            label = CTkLabel(self.content_frame, text="Attendance Module", font=(FONT_NAME, 18), fg_color=CONTENT_BG, text_color="#000")
        else:
            label = tk.Label(self.content_frame, text="Attendance Module", font=(FONT_NAME, 18), bg=CONTENT_BG, fg="#000")
        label.pack(pady=10)
        students = []
        try:
            students = self.load_data(self.attendance_file)
        except Exception:
            students = []
        self.attendance_vars = {}
        if not students:
            if CUSTOM:
                info = CTkLabel(self.content_frame, text="No students found in attendance data.",
                                font=(FONT_NAME, 12), fg_color=CONTENT_BG, text_color="#000")
            else:
                info = tk.Label(self.content_frame, text="No students found in attendance data.",
                                font=(FONT_NAME, 12), bg=CONTENT_BG, fg="#000")
            info.pack(pady=10)
        else:
            for student in students:
                name = str(student.get("name", student.get("Name", student)))
                var = BooleanVar()
                self.attendance_vars[name] = var
                if CUSTOM:
                    cb = CTkCheckBox(self.content_frame, text=name, text_color="#000", font=(FONT_NAME,12))
                else:
                    cb = tk.Checkbutton(self.content_frame, text=name, variable=var,
                                         font=(FONT_NAME,12), bg=CONTENT_BG, anchor="w")
                cb.pack(anchor="w", padx=10, pady=2)
        # Buttons
        if CUSTOM:
            summary_btn = CTkButton(self.content_frame, text="Show Summary", font=(FONT_NAME, 12),
                                    fg_color=BUTTON_BG, text_color=BUTTON_FG, command=self.attendance_summary)
            export_btn = CTkButton(self.content_frame, text="Export Attendance", font=(FONT_NAME, 12),
                                   fg_color=BUTTON_BG, text_color=BUTTON_FG, command=self.export_attendance)
        else:
            summary_btn = tk.Button(self.content_frame, text="Show Summary", font=(FONT_NAME, 12),
                                     bg=BUTTON_BG, fg=BUTTON_FG, command=self.attendance_summary)
            export_btn = tk.Button(self.content_frame, text="Export Attendance", font=(FONT_NAME, 12),
                                    bg=BUTTON_BG, fg=BUTTON_FG, command=self.export_attendance)
        summary_btn.pack(pady=10)
        export_btn.pack(pady=5)

    def attendance_summary(self):
        present_count = sum(var.get() for var in self.attendance_vars.values())
        total = len(self.attendance_vars)
        absent_count = total - present_count
        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except ImportError:
            messagebox.showerror("Missing Library", "matplotlib is required for summary graph.")
            return
        fig = Figure(figsize=(4,3))
        ax = fig.add_subplot(111)
        categories = ['Present','Absent']
        counts = [present_count, absent_count]
        bars = ax.bar(categories, counts, color=['#6A5ACD','#FF69B4'])
        ax.set_title("Attendance Summary")
        for i, v in enumerate(counts):
            ax.text(i, v + 0.1, str(v), ha='center', fontname=FONT_NAME)
        canvas = FigureCanvasTkAgg(fig, master=self.content_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)

    def export_attendance(self):
        records = []
        for name, var in self.attendance_vars.items():
            present = bool(var.get())
            records.append({"student": name, "present": present})
        filetypes = [('CSV file','*.csv'),('JSON file','*.json')]
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=filetypes)
        if not filepath:
            return
        if filepath.endswith(".csv"):
            try:
                with open(filepath, 'w', newline='') as csvfile:
                    import csv
                    writer = csv.DictWriter(csvfile, fieldnames=["student","present"])
                    writer.writeheader()
                    for rec in records:
                        writer.writerow(rec)
                messagebox.showinfo("Export", f"Attendance exported to {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export CSV: {e}")
        else:
            try:
                with open(filepath, 'w') as jf:
                    json.dump(records, jf, indent=4)
                messagebox.showinfo("Export", f"Attendance exported to {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export JSON: {e}")

    def show_subjects(self):
        self.clear_frame(self.content_frame)
        if CUSTOM:
            label = CTkLabel(self.content_frame, text="Subjects Module", font=(FONT_NAME, 18), fg_color=CONTENT_BG, text_color="#000")
        else:
            label = tk.Label(self.content_frame, text="Subjects Module", font=(FONT_NAME, 18), bg=CONTENT_BG, fg="#000")
        label.pack(pady=10)
        # Table of subjects
        columns = ("ID", "Name")
        tree = ttk.Treeview(self.content_frame, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
        for subj in self.subjects_data:
            sid = subj.get("id", subj.get("ID", ""))
            name = subj.get("name", subj.get("Name", ""))
            tree.insert("", "end", values=(sid, name))
        tree.pack(padx=10, pady=10, fill="x")
        # Buttons
        if CUSTOM:
            btn_frame = CTkFrame(self.content_frame, fg_color=CONTENT_BG)
        else:
            btn_frame = tk.Frame(self.content_frame, bg=CONTENT_BG)
        btn_frame.pack(pady=10)
        if CUSTOM:
            add_btn = CTkButton(btn_frame, text="Add", font=(FONT_NAME, 12),
                                fg_color=BUTTON_BG, text_color=BUTTON_FG, command=lambda: self.add_subject(tree))
            edit_btn = CTkButton(btn_frame, text="Edit", font=(FONT_NAME, 12),
                                fg_color=BUTTON_BG, text_color=BUTTON_FG, command=lambda: self.edit_subject(tree))
            del_btn = CTkButton(btn_frame, text="Delete", font=(FONT_NAME, 12),
                                fg_color=BUTTON_BG, text_color=BUTTON_FG, command=lambda: self.delete_subject(tree))
        else:
            add_btn = tk.Button(btn_frame, text="Add", font=(FONT_NAME, 12),
                                bg=BUTTON_BG, fg=BUTTON_FG, command=lambda: self.add_subject(tree))
            edit_btn = tk.Button(btn_frame, text="Edit", font=(FONT_NAME, 12),
                                bg=BUTTON_BG, fg=BUTTON_FG, command=lambda: self.edit_subject(tree))
            del_btn = tk.Button(btn_frame, text="Delete", font=(FONT_NAME, 12),
                                bg=BUTTON_BG, fg=BUTTON_FG, command=lambda: self.delete_subject(tree))
        add_btn.pack(side="left", padx=5)
        edit_btn.pack(side="left", padx=5)
        del_btn.pack(side="left", padx=5)

    def add_subject(self, tree):
        if CUSTOM:
            win = ctk.CTkToplevel(self.root)
        else:
            win = tk.Toplevel(self.root)
        win.title("Add Subject")
        win.geometry("300x200")
        if CUSTOM:
            lbl1 = CTkLabel(win, text="Subject ID:", font=(FONT_NAME, 12), text_color="#000")
        else:
            lbl1 = tk.Label(win, text="Subject ID:", font=(FONT_NAME, 12))
        lbl1.pack(pady=(10,0))
        id_entry = CTkEntry(win, font=(FONT_NAME, 12))
        id_entry.pack(pady=5)
        if CUSTOM:
            lbl2 = CTkLabel(win, text="Subject Name:", font=(FONT_NAME, 12), text_color="#000")
        else:
            lbl2 = tk.Label(win, text="Subject Name:", font=(FONT_NAME, 12))
        lbl2.pack(pady=(10,0))
        name_entry = CTkEntry(win, font=(FONT_NAME, 12))
        name_entry.pack(pady=5)
        def save():
            sid = id_entry.get().strip()
            name = name_entry.get().strip()
            if not sid or not name:
                messagebox.showerror("Error", "All fields are required")
                return
            self.subjects_data.append({"id": sid, "name": name})
            self.save_data(self.subjects_file, self.subjects_data)
            tree.insert("", "end", values=(sid, name))
            win.destroy()
        if CUSTOM:
            save_btn = CTkButton(win, text="Save", font=(FONT_NAME, 12),
                                 fg_color=BUTTON_BG, text_color=BUTTON_FG, command=save)
        else:
            save_btn = tk.Button(win, text="Save", font=(FONT_NAME, 12),
                                 bg=BUTTON_BG, fg=BUTTON_FG, command=save)
        save_btn.pack(pady=10)

    def edit_subject(self, tree):
        selected = tree.focus()
        if not selected:
            messagebox.showerror("Error", "Select a subject to edit")
            return
        values = tree.item(selected, 'values')
        sid_val, name_val = values
        if CUSTOM:
            win = ctk.CTkToplevel(self.root)
        else:
            win = tk.Toplevel(self.root)
        win.title("Edit Subject")
        win.geometry("300x200")
        if CUSTOM:
            lbl1 = CTkLabel(win, text="Subject ID:", font=(FONT_NAME, 12), text_color="#000")
        else:
            lbl1 = tk.Label(win, text="Subject ID:", font=(FONT_NAME, 12))
        lbl1.pack(pady=(10,0))
        id_entry = CTkEntry(win, font=(FONT_NAME, 12))
        id_entry.insert(0, sid_val)
        id_entry.pack(pady=5)
        id_entry.configure(state="readonly")
        if CUSTOM:
            lbl2 = CTkLabel(win, text="Subject Name:", font=(FONT_NAME, 12), text_color="#000")
        else:
            lbl2 = tk.Label(win, text="Subject Name:", font=(FONT_NAME, 12))
        lbl2.pack(pady=(10,0))
        name_entry = CTkEntry(win, font=(FONT_NAME, 12))
        name_entry.insert(0, name_val)
        name_entry.pack(pady=5)
        def save():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Name cannot be empty")
                return
            for subj in self.subjects_data:
                if str(subj.get("id","")) == sid_val:
                    subj["name"] = name
            self.save_data(self.subjects_file, self.subjects_data)
            tree.item(selected, values=(sid_val, name))
            win.destroy()
        if CUSTOM:
            save_btn = CTkButton(win, text="Save", font=(FONT_NAME, 12),
                                 fg_color=BUTTON_BG, text_color=BUTTON_FG, command=save)
        else:
            save_btn = tk.Button(win, text="Save", font=(FONT_NAME, 12),
                                 bg=BUTTON_BG, fg=BUTTON_FG, command=save)
        save_btn.pack(pady=10)

    def delete_subject(self, tree):
        selected = tree.focus()
        if not selected:
            messagebox.showerror("Error", "Select a subject to delete")
            return
        values = tree.item(selected, 'values')
        sid_val, _ = values
        confirm = messagebox.askyesno("Confirm", "Delete selected subject?")
        if not confirm:
            return
        self.subjects_data = [subj for subj in self.subjects_data if str(subj.get("id","")) != sid_val]
        self.save_data(self.subjects_file, self.subjects_data)
        tree.delete(selected)

    def show_sections(self):
        self.clear_frame(self.content_frame)
        if CUSTOM:
            label = CTkLabel(self.content_frame, text="Sections Module", font=(FONT_NAME, 18), fg_color=CONTENT_BG, text_color="#000")
        else:
            label = tk.Label(self.content_frame, text="Sections Module", font=(FONT_NAME, 18), bg=CONTENT_BG, fg="#000")
        label.pack(pady=10)
        columns = ("ID", "Name")
        tree = ttk.Treeview(self.content_frame, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
        for sec in self.sections_data:
            sid = sec.get("id", sec.get("ID", ""))
            name = sec.get("name", sec.get("Name", ""))
            tree.insert("", "end", values=(sid, name))
        tree.pack(padx=10, pady=10, fill="x")
        if CUSTOM:
            btn_frame = CTkFrame(self.content_frame, fg_color=CONTENT_BG)
            add_btn = CTkButton(btn_frame, text="Add", font=(FONT_NAME, 12),
                                fg_color=BUTTON_BG, text_color=BUTTON_FG, command=lambda: self.add_section(tree))
            edit_btn = CTkButton(btn_frame, text="Edit", font=(FONT_NAME, 12),
                                fg_color=BUTTON_BG, text_color=BUTTON_FG, command=lambda: self.edit_section(tree))
            del_btn = CTkButton(btn_frame, text="Delete", font=(FONT_NAME, 12),
                                fg_color=BUTTON_BG, text_color=BUTTON_FG, command=lambda: self.delete_section(tree))
        else:
            btn_frame = tk.Frame(self.content_frame, bg=CONTENT_BG)
            add_btn = tk.Button(btn_frame, text="Add", font=(FONT_NAME, 12),
                                bg=BUTTON_BG, fg=BUTTON_FG, command=lambda: self.add_section(tree))
            edit_btn = tk.Button(btn_frame, text="Edit", font=(FONT_NAME, 12),
                                bg=BUTTON_BG, fg=BUTTON_FG, command=lambda: self.edit_section(tree))
            del_btn = tk.Button(btn_frame, text="Delete", font=(FONT_NAME, 12),
                                bg=BUTTON_BG, fg=BUTTON_FG, command=lambda: self.delete_section(tree))
        btn_frame.pack(pady=10)
        add_btn.pack(side="left", padx=5)
        edit_btn.pack(side="left", padx=5)
        del_btn.pack(side="left", padx=5)

    def add_section(self, tree):
        if CUSTOM:
            win = ctk.CTkToplevel(self.root)
        else:
            win = tk.Toplevel(self.root)
        win.title("Add Section")
        win.geometry("300x200")
        if CUSTOM:
            lbl1 = CTkLabel(win, text="Section ID:", font=(FONT_NAME, 12), text_color="#000")
        else:
            lbl1 = tk.Label(win, text="Section ID:", font=(FONT_NAME, 12))
        lbl1.pack(pady=(10,0))
        id_entry = CTkEntry(win, font=(FONT_NAME, 12))
        id_entry.pack(pady=5)
        if CUSTOM:
            lbl2 = CTkLabel(win, text="Section Name:", font=(FONT_NAME, 12), text_color="#000")
        else:
            lbl2 = tk.Label(win, text="Section Name:", font=(FONT_NAME, 12))
        lbl2.pack(pady=(10,0))
        name_entry = CTkEntry(win, font=(FONT_NAME, 12))
        name_entry.pack(pady=5)
        def save():
            sid = id_entry.get().strip()
            name = name_entry.get().strip()
            if not sid or not name:
                messagebox.showerror("Error", "All fields are required")
                return
            self.sections_data.append({"id": sid, "name": name})
            self.save_data(self.sections_file, self.sections_data)
            tree.insert("", "end", values=(sid, name))
            win.destroy()
        if CUSTOM:
            save_btn = CTkButton(win, text="Save", font=(FONT_NAME, 12),
                                 fg_color=BUTTON_BG, text_color=BUTTON_FG, command=save)
        else:
            save_btn = tk.Button(win, text="Save", font=(FONT_NAME, 12),
                                 bg=BUTTON_BG, fg=BUTTON_FG, command=save)
        save_btn.pack(pady=10)

    def edit_section(self, tree):
        selected = tree.focus()
        if not selected:
            messagebox.showerror("Error", "Select a section to edit")
            return
        values = tree.item(selected, 'values')
        sid_val, name_val = values
        if CUSTOM:
            win = ctk.CTkToplevel(self.root)
        else:
            win = tk.Toplevel(self.root)
        win.title("Edit Section")
        win.geometry("300x200")
        if CUSTOM:
            lbl1 = CTkLabel(win, text="Section ID:", font=(FONT_NAME, 12), text_color="#000")
        else:
            lbl1 = tk.Label(win, text="Section ID:", font=(FONT_NAME, 12))
        lbl1.pack(pady=(10,0))
        id_entry = CTkEntry(win, font=(FONT_NAME, 12))
        id_entry.insert(0, sid_val)
        id_entry.pack(pady=5)
        id_entry.configure(state="readonly")
        if CUSTOM:
            lbl2 = CTkLabel(win, text="Section Name:", font=(FONT_NAME, 12), text_color="#000")
        else:
            lbl2 = tk.Label(win, text="Section Name:", font=(FONT_NAME, 12))
        lbl2.pack(pady=(10,0))
        name_entry = CTkEntry(win, font=(FONT_NAME, 12))
        name_entry.insert(0, name_val)
        name_entry.pack(pady=5)
        def save():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Name cannot be empty")
                return
            for sec in self.sections_data:
                if str(sec.get("id","")) == sid_val:
                    sec["name"] = name
            self.save_data(self.sections_file, self.sections_data)
            tree.item(selected, values=(sid_val, name))
            win.destroy()
        if CUSTOM:
            save_btn = CTkButton(win, text="Save", font=(FONT_NAME, 12),
                                 fg_color=BUTTON_BG, text_color=BUTTON_FG, command=save)
        else:
            save_btn = tk.Button(win, text="Save", font=(FONT_NAME, 12),
                                 bg=BUTTON_BG, fg=BUTTON_FG, command=save)
        save_btn.pack(pady=10)

    def delete_section(self, tree):
        selected = tree.focus()
        if not selected:
            messagebox.showerror("Error", "Select a section to delete")
            return
        values = tree.item(selected, 'values')
        sid_val, _ = values
        confirm = messagebox.askyesno("Confirm", "Delete selected section?")
        if not confirm:
            return
        self.sections_data = [sec for sec in self.sections_data if str(sec.get("id","")) != sid_val]
        self.save_data(self.sections_file, self.sections_data)
        tree.delete(selected)

    def show_teachers(self):
        self.clear_frame(self.content_frame)
        if CUSTOM:
            label = CTkLabel(self.content_frame, text="Teachers Module", font=(FONT_NAME, 18), fg_color=CONTENT_BG, text_color="#000")
        else:
            label = tk.Label(self.content_frame, text="Teachers Module", font=(FONT_NAME, 18), bg=CONTENT_BG, fg="#000")
        label.pack(pady=10)
        columns = ("Teacher", "Sections")
        tree = ttk.Treeview(self.content_frame, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
        for tea in self.teachers_data:
            name = tea.get("teacher", tea.get("Teacher", ""))
            secs = tea.get("sections", tea.get("Sections", []))
            tree.insert("", "end", values=(name, ", ".join(secs) if isinstance(secs, list) else secs))
        tree.pack(padx=10, pady=10, fill="x")
        if CUSTOM:
            btn_frame = CTkFrame(self.content_frame, fg_color=CONTENT_BG)
            add_btn = CTkButton(btn_frame, text="Add", font=(FONT_NAME, 12),
                                fg_color=BUTTON_BG, text_color=BUTTON_FG, command=lambda: self.add_teacher(tree))
            edit_btn = CTkButton(btn_frame, text="Edit", font=(FONT_NAME, 12),
                                fg_color=BUTTON_BG, text_color=BUTTON_FG, command=lambda: self.edit_teacher(tree))
            del_btn = CTkButton(btn_frame, text="Delete", font=(FONT_NAME, 12),
                                fg_color=BUTTON_BG, text_color=BUTTON_FG, command=lambda: self.delete_teacher(tree))
        else:
            btn_frame = tk.Frame(self.content_frame, bg=CONTENT_BG)
            add_btn = tk.Button(btn_frame, text="Add", font=(FONT_NAME, 12),
                                bg=BUTTON_BG, fg=BUTTON_FG, command=lambda: self.add_teacher(tree))
            edit_btn = tk.Button(btn_frame, text="Edit", font=(FONT_NAME, 12),
                                bg=BUTTON_BG, fg=BUTTON_FG, command=lambda: self.edit_teacher(tree))
            del_btn = tk.Button(btn_frame, text="Delete", font=(FONT_NAME, 12),
                                bg=BUTTON_BG, fg=BUTTON_FG, command=lambda: self.delete_teacher(tree))
        btn_frame.pack(pady=10)
        add_btn.pack(side="left", padx=5)
        edit_btn.pack(side="left", padx=5)
        del_btn.pack(side="left", padx=5)

    def add_teacher(self, tree):
        if CUSTOM:
            win = ctk.CTkToplevel(self.root)
        else:
            win = tk.Toplevel(self.root)
        win.title("Add Teacher")
        win.geometry("300x250")
        if CUSTOM:
            lbl1 = CTkLabel(win, text="Teacher Name:", font=(FONT_NAME, 12), text_color="#000")
        else:
            lbl1 = tk.Label(win, text="Teacher Name:", font=(FONT_NAME, 12))
        lbl1.pack(pady=(10,0))
        name_entry = CTkEntry(win, font=(FONT_NAME, 12))
        name_entry.pack(pady=5)
        if CUSTOM:
            lbl2 = CTkLabel(win, text="Sections (comma-separated):", font=(FONT_NAME, 12), text_color="#000")
        else:
            lbl2 = tk.Label(win, text="Sections (comma-separated):", font=(FONT_NAME, 12))
        lbl2.pack(pady=(10,0))
        sections_entry = CTkEntry(win, font=(FONT_NAME, 12))
        sections_entry.pack(pady=5)
        def save():
            name = name_entry.get().strip()
            secs = sections_entry.get().split(',')
            secs = [s.strip() for s in secs if s.strip()]
            if not name:
                messagebox.showerror("Error", "Name cannot be empty")
                return
            self.teachers_data.append({"teacher": name, "sections": secs})
            self.save_data(self.teachersections_file, self.teachers_data)
            tree.insert("", "end", values=(name, ", ".join(secs)))
            win.destroy()
        if CUSTOM:
            save_btn = CTkButton(win, text="Save", font=(FONT_NAME, 12),
                                 fg_color=BUTTON_BG, text_color=BUTTON_FG, command=save)
        else:
            save_btn = tk.Button(win, text="Save", font=(FONT_NAME, 12),
                                 bg=BUTTON_BG, fg=BUTTON_FG, command=save)
        save_btn.pack(pady=10)

    def edit_teacher(self, tree):
        selected = tree.focus()
        if not selected:
            messagebox.showerror("Error", "Select a teacher to edit")
            return
        values = tree.item(selected, 'values')
        name_val, secs_val = values
        if CUSTOM:
            win = ctk.CTkToplevel(self.root)
        else:
            win = tk.Toplevel(self.root)
        win.title("Edit Teacher")
        win.geometry("300x250")
        if CUSTOM:
            lbl1 = CTkLabel(win, text="Teacher Name:", font=(FONT_NAME, 12), text_color="#000")
        else:
            lbl1 = tk.Label(win, text="Teacher Name:", font=(FONT_NAME, 12))
        lbl1.pack(pady=(10,0))
        name_entry = CTkEntry(win, font=(FONT_NAME, 12))
        name_entry.insert(0, name_val)
        name_entry.pack(pady=5)
        name_entry.configure(state="readonly")
        if CUSTOM:
            lbl2 = CTkLabel(win, text="Sections (comma-separated):", font=(FONT_NAME, 12), text_color="#000")
        else:
            lbl2 = tk.Label(win, text="Sections (comma-separated):", font=(FONT_NAME, 12))
        lbl2.pack(pady=(10,0))
        sections_entry = CTkEntry(win, font=(FONT_NAME, 12))
        sections_entry.insert(0, secs_val)
        sections_entry.pack(pady=5)
        def save():
            secs = sections_entry.get().split(',')
            secs = [s.strip() for s in secs if s.strip()]
            for tea in self.teachers_data:
                if tea.get("teacher","") == name_val:
                    tea["sections"] = secs
            self.save_data(self.teachersections_file, self.teachers_data)
            tree.item(selected, values=(name_val, ", ".join(secs)))
            win.destroy()
        if CUSTOM:
            save_btn = CTkButton(win, text="Save", font=(FONT_NAME, 12),
                                 fg_color=BUTTON_BG, text_color=BUTTON_FG, command=save)
        else:
            save_btn = tk.Button(win, text="Save", font=(FONT_NAME, 12),
                                 bg=BUTTON_BG, fg=BUTTON_FG, command=save)
        save_btn.pack(pady=10)

    def delete_teacher(self, tree):
        selected = tree.focus()
        if not selected:
            messagebox.showerror("Error", "Select a teacher to delete")
            return
        values = tree.item(selected, 'values')
        name_val = values[0]
        confirm = messagebox.askyesno("Confirm", "Delete selected teacher?")
        if not confirm:
            return
        self.teachers_data = [tea for tea in self.teachers_data if tea.get("teacher","") != name_val]
        self.save_data(self.teachersections_file, self.teachers_data)
        tree.delete(selected)

    def show_exams(self):
        self.clear_frame(self.content_frame)
        if CUSTOM:
            label = CTkLabel(self.content_frame, text="Exams Module", font=(FONT_NAME, 18), fg_color=CONTENT_BG, text_color="#000")
        else:
            label = tk.Label(self.content_frame, text="Exams Module", font=(FONT_NAME, 18), bg=CONTENT_BG, fg="#000")
        label.pack(pady=10)
        columns = ("Exam", "Date")
        tree = ttk.Treeview(self.content_frame, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
        for ex in self.exams_data:
            exam = ex.get("exam", ex.get("Exam", ""))
            date = ex.get("date", ex.get("Date", ""))
            tree.insert("", "end", values=(exam, date))
        tree.pack(padx=10, pady=10, fill="x")
        if CUSTOM:
            btn_frame = CTkFrame(self.content_frame, fg_color=CONTENT_BG)
            add_btn = CTkButton(btn_frame, text="Add", font=(FONT_NAME, 12),
                                fg_color=BUTTON_BG, text_color=BUTTON_FG, command=lambda: self.add_exam(tree))
            edit_btn = CTkButton(btn_frame, text="Edit", font=(FONT_NAME, 12),
                                fg_color=BUTTON_BG, text_color=BUTTON_FG, command=lambda: self.edit_exam(tree))
            del_btn = CTkButton(btn_frame, text="Delete", font=(FONT_NAME, 12),
                                fg_color=BUTTON_BG, text_color=BUTTON_FG, command=lambda: self.delete_exam(tree))
        else:
            btn_frame = tk.Frame(self.content_frame, bg=CONTENT_BG)
            add_btn = tk.Button(btn_frame, text="Add", font=(FONT_NAME, 12),
                                bg=BUTTON_BG, fg=BUTTON_FG, command=lambda: self.add_exam(tree))
            edit_btn = tk.Button(btn_frame, text="Edit", font=(FONT_NAME, 12),
                                bg=BUTTON_BG, fg=BUTTON_FG, command=lambda: self.edit_exam(tree))
            del_btn = tk.Button(btn_frame, text="Delete", font=(FONT_NAME, 12),
                                bg=BUTTON_BG, fg=BUTTON_FG, command=lambda: self.delete_exam(tree))
        btn_frame.pack(pady=10)
        add_btn.pack(side="left", padx=5)
        edit_btn.pack(side="left", padx=5)
        del_btn.pack(side="left", padx=5)

    def add_exam(self, tree):
        if CUSTOM:
            win = ctk.CTkToplevel(self.root)
        else:
            win = tk.Toplevel(self.root)
        win.title("Add Exam")
        win.geometry("300x200")
        if CUSTOM:
            lbl1 = CTkLabel(win, text="Exam Name:", font=(FONT_NAME, 12), text_color="#000")
        else:
            lbl1 = tk.Label(win, text="Exam Name:", font=(FONT_NAME, 12))
        lbl1.pack(pady=(10,0))
        exam_entry = CTkEntry(win, font=(FONT_NAME, 12))
        exam_entry.pack(pady=5)
        if CUSTOM:
            lbl2 = CTkLabel(win, text="Date (YYYY-MM-DD):", font=(FONT_NAME, 12), text_color="#000")
        else:
            lbl2 = tk.Label(win, text="Date (YYYY-MM-DD):", font=(FONT_NAME, 12))
        lbl2.pack(pady=(10,0))
        date_entry = CTkEntry(win, font=(FONT_NAME, 12))
        date_entry.pack(pady=5)
        def save():
            exam = exam_entry.get().strip()
            date = date_entry.get().strip()
            if not exam or not date:
                messagebox.showerror("Error", "All fields are required")
                return
            self.exams_data.append({"exam": exam, "date": date})
            self.save_data(self.exams_file, self.exams_data)
            tree.insert("", "end", values=(exam, date))
            win.destroy()
        if CUSTOM:
            save_btn = CTkButton(win, text="Save", font=(FONT_NAME, 12),
                                 fg_color=BUTTON_BG, text_color=BUTTON_FG, command=save)
        else:
            save_btn = tk.Button(win, text="Save", font=(FONT_NAME, 12),
                                 bg=BUTTON_BG, fg=BUTTON_FG, command=save)
        save_btn.pack(pady=10)

    def edit_exam(self, tree):
        selected = tree.focus()
        if not selected:
            messagebox.showerror("Error", "Select an exam to edit")
            return
        values = tree.item(selected, 'values')
        exam_val, date_val = values
        if CUSTOM:
            win = ctk.CTkToplevel(self.root)
        else:
            win = tk.Toplevel(self.root)
        win.title("Edit Exam")
        win.geometry("300x200")
        if CUSTOM:
            lbl1 = CTkLabel(win, text="Exam Name:", font=(FONT_NAME, 12), text_color="#000")
        else:
            lbl1 = tk.Label(win, text="Exam Name:", font=(FONT_NAME, 12))
        lbl1.pack(pady=(10,0))
        exam_entry = CTkEntry(win, font=(FONT_NAME, 12))
        exam_entry.insert(0, exam_val)
        exam_entry.pack(pady=5)
        if CUSTOM:
            lbl2 = CTkLabel(win, text="Date (YYYY-MM-DD):", font=(FONT_NAME, 12), text_color="#000")
        else:
            lbl2 = tk.Label(win, text="Date (YYYY-MM-DD):", font=(FONT_NAME, 12))
        lbl2.pack(pady=(10,0))
        date_entry = CTkEntry(win, font=(FONT_NAME, 12))
        date_entry.insert(0, date_val)
        date_entry.pack(pady=5)
        def save():
            exam = exam_entry.get().strip()
            date = date_entry.get().strip()
            if not exam or not date:
                messagebox.showerror("Error", "All fields are required")
                return
            for ex in self.exams_data:
                if ex.get("exam","") == exam_val and ex.get("date","") == date_val:
                    ex["exam"] = exam
                    ex["date"] = date
            self.save_data(self.exams_file, self.exams_data)
            tree.item(selected, values=(exam, date))
            win.destroy()
        if CUSTOM:
            save_btn = CTkButton(win, text="Save", font=(FONT_NAME, 12),
                                 fg_color=BUTTON_BG, text_color=BUTTON_FG, command=save)
        else:
            save_btn = tk.Button(win, text="Save", font=(FONT_NAME, 12),
                                 bg=BUTTON_BG, fg=BUTTON_FG, command=save)
        save_btn.pack(pady=10)

    def delete_exam(self, tree):
        selected = tree.focus()
        if not selected:
            messagebox.showerror("Error", "Select an exam to delete")
            return
        values = tree.item(selected, 'values')
        exam_val = values[0]
        confirm = messagebox.askyesno("Confirm", "Delete selected exam?")
        if not confirm:
            return
        self.exams_data = [ex for ex in self.exams_data if ex.get("exam","") != exam_val]
        self.save_data(self.exams_file, self.exams_data)
        tree.delete(selected)

    def show_topics(self):
        self.clear_frame(self.content_frame)
        if CUSTOM:
            label = CTkLabel(self.content_frame, text="Topics Module", font=(FONT_NAME, 18), fg_color=CONTENT_BG, text_color="#000")
        else:
            label = tk.Label(self.content_frame, text="Topics Module", font=(FONT_NAME, 18), bg=CONTENT_BG, fg="#000")
        label.pack(pady=10)
        columns = ("Topic", "Subject")
        tree = ttk.Treeview(self.content_frame, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
        for top in self.topics_data:
            topic = top.get("topic", top.get("Topic", ""))
            subj = top.get("subject", top.get("Subject", ""))
            tree.insert("", "end", values=(topic, subj))
        tree.pack(padx=10, pady=10, fill="x")
        if CUSTOM:
            btn_frame = CTkFrame(self.content_frame, fg_color=CONTENT_BG)
            add_btn = CTkButton(btn_frame, text="Add", font=(FONT_NAME, 12),
                                fg_color=BUTTON_BG, text_color=BUTTON_FG, command=lambda: self.add_topic(tree))
            edit_btn = CTkButton(btn_frame, text="Edit", font=(FONT_NAME, 12),
                                fg_color=BUTTON_BG, text_color=BUTTON_FG, command=lambda: self.edit_topic(tree))
            del_btn = CTkButton(btn_frame, text="Delete", font=(FONT_NAME, 12),
                                fg_color=BUTTON_BG, text_color=BUTTON_FG, command=lambda: self.delete_topic(tree))
        else:
            btn_frame = tk.Frame(self.content_frame, bg=CONTENT_BG)
            add_btn = tk.Button(btn_frame, text="Add", font=(FONT_NAME, 12),
                                bg=BUTTON_BG, fg=BUTTON_FG, command=lambda: self.add_topic(tree))
            edit_btn = tk.Button(btn_frame, text="Edit", font=(FONT_NAME, 12),
                                bg=BUTTON_BG, fg=BUTTON_FG, command=lambda: self.edit_topic(tree))
            del_btn = tk.Button(btn_frame, text="Delete", font=(FONT_NAME, 12),
                                bg=BUTTON_BG, fg=BUTTON_FG, command=lambda: self.delete_topic(tree))
        btn_frame.pack(pady=10)
        add_btn.pack(side="left", padx=5)
        edit_btn.pack(side="left", padx=5)
        del_btn.pack(side="left", padx=5)

    def add_topic(self, tree):
        if CUSTOM:
            win = ctk.CTkToplevel(self.root)
        else:
            win = tk.Toplevel(self.root)
        win.title("Add Topic")
        win.geometry("300x250")
        if CUSTOM:
            lbl1 = CTkLabel(win, text="Topic Name:", font=(FONT_NAME, 12), text_color="#000")
        else:
            lbl1 = tk.Label(win, text="Topic Name:", font=(FONT_NAME, 12))
        lbl1.pack(pady=(10,0))
        topic_entry = CTkEntry(win, font=(FONT_NAME, 12))
        topic_entry.pack(pady=5)
        if CUSTOM:
            lbl2 = CTkLabel(win, text="Subject:", font=(FONT_NAME, 12), text_color="#000")
        else:
            lbl2 = tk.Label(win, text="Subject:", font=(FONT_NAME, 12))
        lbl2.pack(pady=(10,0))
        subject_entry = CTkEntry(win, font=(FONT_NAME, 12))
        subject_entry.pack(pady=5)
        def save():
            topic = topic_entry.get().strip()
            subj = subject_entry.get().strip()
            if not topic or not subj:
                messagebox.showerror("Error", "All fields are required")
                return
            self.topics_data.append({"topic": topic, "subject": subj})
            self.save_data(self.topics_file, self.topics_data)
            tree.insert("", "end", values=(topic, subj))
            win.destroy()
        if CUSTOM:
            save_btn = CTkButton(win, text="Save", font=(FONT_NAME, 12),
                                 fg_color=BUTTON_BG, text_color=BUTTON_FG, command=save)
        else:
            save_btn = tk.Button(win, text="Save", font=(FONT_NAME, 12),
                                 bg=BUTTON_BG, fg=BUTTON_FG, command=save)
        save_btn.pack(pady=10)

    def edit_topic(self, tree):
        selected = tree.focus()
        if not selected:
            messagebox.showerror("Error", "Select a topic to edit")
            return
        values = tree.item(selected, 'values')
        topic_val, subj_val = values
        if CUSTOM:
            win = ctk.CTkToplevel(self.root)
        else:
            win = tk.Toplevel(self.root)
        win.title("Edit Topic")
        win.geometry("300x250")
        if CUSTOM:
            lbl1 = CTkLabel(win, text="Topic Name:", font=(FONT_NAME, 12), text_color="#000")
        else:
            lbl1 = tk.Label(win, text="Topic Name:", font=(FONT_NAME, 12))
        lbl1.pack(pady=(10,0))
        topic_entry = CTkEntry(win, font=(FONT_NAME, 12))
        topic_entry.insert(0, topic_val)
        topic_entry.pack(pady=5)
        if CUSTOM:
            lbl2 = CTkLabel(win, text="Subject:", font=(FONT_NAME, 12), text_color="#000")
        else:
            lbl2 = tk.Label(win, text="Subject:", font=(FONT_NAME, 12))
        lbl2.pack(pady=(10,0))
        subject_entry = CTkEntry(win, font=(FONT_NAME, 12))
        subject_entry.insert(0, subj_val)
        subject_entry.pack(pady=5)
        def save():
            topic = topic_entry.get().strip()
            subj = subject_entry.get().strip()
            if not topic or not subj:
                messagebox.showerror("Error", "All fields are required")
                return
            for t in self.topics_data:
                if t.get("topic","") == topic_val and t.get("subject","") == subj_val:
                    t["topic"] = topic
                    t["subject"] = subj
            self.save_data(self.topics_file, self.topics_data)
            tree.item(selected, values=(topic, subj))
            win.destroy()
        if CUSTOM:
            save_btn = CTkButton(win, text="Save", font=(FONT_NAME, 12),
                                 fg_color=BUTTON_BG, text_color=BUTTON_FG, command=save)
        else:
            save_btn = tk.Button(win, text="Save", font=(FONT_NAME, 12),
                                 bg=BUTTON_BG, fg=BUTTON_FG, command=save)
        save_btn.pack(pady=10)

    def delete_topic(self, tree):
        selected = tree.focus()
        if not selected:
            messagebox.showerror("Error", "Select a topic to delete")
            return
        values = tree.item(selected, 'values')
        topic_val = values[0]
        confirm = messagebox.askyesno("Confirm", "Delete selected topic?")
        if not confirm:
            return
        self.topics_data = [t for t in self.topics_data if t.get("topic","") != topic_val]
        self.save_data(self.topics_file, self.topics_data)
        tree.delete(selected)

if __name__ == "__main__":
    app = CTk()
    EduTrackApp(app)
    app.mainloop()
