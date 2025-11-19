import os
import sys
import ast
import json
import hashlib
import subprocess
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

def rootpath():
    return os.path.dirname(os.path.abspath(__file__))

def userfile():
    return os.path.join(rootpath(), "users.json")

def rememberfile():
    return os.path.join(rootpath(), "remember.json")

def hashpass(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def usersave(data):
    try:
        with open(userfile(), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        messagebox.showerror("save error", str(e))

def userload():
    path = userfile()
    if not os.path.exists(path):
        base = {"admin": hashpass("admin123")}
        usersave(base)
        return base
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        base = {"admin": hashpass("admin123")}
        usersave(base)
        return base

def remembersave(user):
    try:
        with open(rememberfile(), "w", encoding="utf-8") as f:
            json.dump({"user": user}, f)
    except Exception:
        pass

def rememberload():
    path = rememberfile()
    if not os.path.exists(path):
        remembersave("")
        return ""
    try:
        with open(path, "r", encoding="utf-8") as f:
            obj = json.load(f)
            return obj.get("user", "")
    except Exception:
        remembersave("")
        return ""

def ispy(path):
    return path.endswith(".py") and os.path.isfile(path)

def getdoc(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            node = ast.parse(f.read())
        note = ast.get_docstring(node)
        return note or ""
    except Exception:
        return ""

def findscripts(base):
    items = []
    for dpath, dnames, fnames in os.walk(base):
        dnames[:] = [d for d in dnames if d not in {"__pycache__", ".git", ".venv", "venv", "env"}]
        for name in fnames:
            if not name.endswith(".py"):
                continue
            if name in {"appgui.py"}:
                continue
            full = os.path.join(dpath, name)
            rel = os.path.relpath(full, base)
            doc = getdoc(full)
            items.append({"name": name, "path": full, "rel": rel, "doc": doc})
    items.sort(key=lambda x: x["rel"].lower())
    return items

class runman:
    def __init__(self, outtext, statusvar):
        self.outtext = outtext
        self.statusvar = statusvar
        self.proc = None

    def run(self, path, args, work):
        if self.proc:
            messagebox.showwarning("running", "stop current run first")
            return
        argv = [sys.executable, path]
        args = args.strip()
        if args:
            argv.extend(args.split())
        self.outtext.delete("1.0", "end")
        self.statusvar.set("running")
        try:
            self.proc = subprocess.Popen(
                argv,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=work
            )
            threading.Thread(target=self.readloop, daemon=True).start()
        except Exception as e:
            self.statusvar.set("error")
            messagebox.showerror("run error", str(e))

    def readloop(self):
        try:
            for line in self.proc.stdout:
                self.outtext.insert("end", line)
                self.outtext.see("end")
        except Exception:
            pass
        finally:
            self.statusvar.set("finished")
            self.proc = None

    def stop(self):
        if self.proc:
            try:
                self.proc.terminate()
            except Exception:
                pass
            self.proc = None
            self.statusvar.set("stopped")

class app(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("project 2 bright login and dashboard")
        self.geometry("980x680")
        self.users = userload()
        self.remember = rememberload()
        self.base = rootpath()
        self.items = findscripts(self.base)
        self.statusvar = tk.StringVar(value="ready")
        self.uservar = tk.StringVar(value=self.remember or "")
        self.passvar = tk.StringVar()
        self.keepvar = tk.BooleanVar(value=True)
        self.searchvar = tk.StringVar()
        self.argsvar = tk.StringVar()
        self.listbox = None
        self.pathlabel = None
        self.doctext = None
        self.outtext = None
        self.runner = None
        self.makehead()
        self.makelogin()

    def makehead(self):
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=10, pady=(10, 0))
        ttk.Label(bar, text="project 2", font=("Segoe UI", 14, "bold")).pack(side="left")
        ttk.Label(bar, textvariable=self.statusvar).pack(side="right")

    def makelogin(self):
        self.clearbody()
        panel = ttk.Frame(self)
        panel.pack(fill="both", expand=True, padx=20, pady=20)
        box = ttk.Frame(panel)
        box.pack(pady=30)
        ttk.Label(box, text="login", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 10))
        ttk.Label(box, text="user").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        uentry = ttk.Entry(box, textvariable=self.uservar, width=36)
        uentry.grid(row=1, column=1, sticky="ew", padx=6, pady=6)
        ttk.Label(box, text="pass").grid(row=2, column=0, sticky="w", padx=6, pady=6)
        pentry = ttk.Entry(box, textvariable=self.passvar, show="•", width=36)
        pentry.grid(row=2, column=1, sticky="ew", padx=6, pady=6)
        keep = ttk.Checkbutton(box, text="remember", variable=self.keepvar)
        keep.grid(row=3, column=0, columnspan=2, pady=(2, 10))
        ttk.Button(box, text="enter", command=self.loginsubmit).grid(row=4, column=0, pady=6)
        ttk.Button(box, text="reset", command=self.loginreset).grid(row=4, column=1, pady=6)
        box.columnconfigure(1, weight=1)
        pentry.bind("<Return>", lambda e: self.loginsubmit())
        ttk.Label(panel, text="default admin / admin123").pack(pady=8)

    def loginreset(self):
        self.uservar.set("")
        self.passvar.set("")
        self.statusvar.set("ready")

    def loginsubmit(self):
        user = self.uservar.get().strip()
        pw = self.passvar.get().strip()
        if not user or not pw:
            self.statusvar.set("enter user and pass")
            return
        code = self.users.get(user)
        if not code:
            self.statusvar.set("user not found")
            return
        if hashpass(pw) != code:
            self.statusvar.set("wrong pass")
            return
        if self.keepvar.get():
            remembersave(user)
        else:
            remembersave("")
        self.statusvar.set(f"hello {user}")
        self.makedash()

    def makedash(self):
        self.clearbody()
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=8)
        ttk.Label(top, text="search").pack(side="left")
        sentry = ttk.Entry(top, textvariable=self.searchvar, width=40)
        sentry.pack(side="left", padx=(6, 10))
        sentry.bind("<KeyRelease>", lambda e: self.refill())
        ttk.Button(top, text="refresh", command=self.clickrefresh).pack(side="left", padx=4)
        ttk.Button(top, text="logout", command=self.clicklogout).pack(side="right")
        panes = ttk.PanedWindow(self, orient="horizontal")
        panes.pack(fill="both", expand=True, padx=10, pady=8)
        left = ttk.Frame(panes)
        panes.add(left, weight=1)
        self.listbox = tk.Listbox(left, height=24)
        self.listbox.pack(side="left", fill="both", expand=True)
        sbar = ttk.Scrollbar(left, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=sbar.set)
        sbar.pack(side="right", fill="y")
        self.listbox.bind("<<ListboxSelect>>", self.pick)
        right = ttk.Frame(panes)
        panes.add(right, weight=3)
        self.pathlabel = ttk.Label(right, text="path: —", wraplength=720, justify="left")
        self.pathlabel.pack(fill="x", padx=8, pady=(8, 4))
        ttk.Label(right, text="docstring").pack(anchor="w", padx=8)
        self.doctext = tk.Text(right, height=6)
        self.doctext.pack(fill="x", padx=8, pady=4)
        self.doctext.configure(state="disabled")
        runbox = ttk.Frame(right)
        runbox.pack(fill="x", padx=8, pady=4)
        ttk.Label(runbox, text="args").pack(side="left")
        aentry = ttk.Entry(runbox, textvariable=self.argsvar, width=50)
        aentry.pack(side="left", padx=6)
        self.outtext = tk.Text(right)
        self.outtext.pack(fill="both", expand=True, padx=8, pady=(4, 8))
        btnbox = ttk.Frame(right)
        btnbox.pack(fill="x", padx=8, pady=6)
        ttk.Button(btnbox, text="run", command=self.clickrun).pack(side="left")
        ttk.Button(btnbox, text="stop", command=self.clickstop).pack(side="left")
        ttk.Button(btnbox, text="clear", command=lambda: self.outtext.delete("1.0", "end")).pack(side="left")
        ttk.Button(btnbox, text="open folder", command=self.clickopen).pack(side="right")
        self.runner = runman(self.outtext, self.statusvar)
        self.refill()

    def refill(self):
        q = self.searchvar.get().lower().strip()
        self.listbox.delete(0, "end")
        for s in self.items:
            rel = s["rel"]
            if q and q not in rel.lower():
                continue
            self.listbox.insert("end", rel)
        if self.listbox.size():
            self.listbox.selection_set(0)
            self.pick()

    def clickrefresh(self):
        self.items = findscripts(self.base)
        self.refill()
        self.statusvar.set("list refreshed")

    def pick(self, event=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        rel = self.listbox.get(sel[0])
        obj = next((x for x in self.items if x["rel"] == rel), None)
        if not obj:
            return
        self.pathlabel.configure(text=f"path: {obj['path']}")
        self.doctext.configure(state="normal")
        self.doctext.delete("1.0", "end")
        self.doctext.insert("1.0", obj["doc"] or "(no docstring)")
        self.doctext.configure(state="disabled")

    def clickrun(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("select", "pick a script first")
            return
        rel = self.listbox.get(sel[0])
        obj = next((x for x in self.items if x["rel"] == rel), None)
        if not obj:
            messagebox.showerror("not found", "script not found")
            return
        path = obj["path"]
        work = os.path.dirname(path)
        args = self.argsvar.get()
        self.runner.run(path, args, work)

    def clickstop(self):
        self.runner.stop()

    def clickopen(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        rel = self.listbox.get(sel[0])
        obj = next((x for x in self.items if x["rel"] == rel), None)
        if not obj:
            return
        folder = os.path.dirname(obj["path"])
        try:
            if sys.platform.startswith("win"):
                os.startfile(folder)  # type: ignore
            elif sys.platform == "darwin":
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["xdg-open", folder])
        except Exception as e:
            messagebox.showerror("open error", str(e))

    def clearbody(self):
        for w in list(self.winfo_children())[1:]:
            w.destroy()

    def clicklogout(self):
        self.statusvar.set("ready")
        self.makelogin()

if __name__ == "__main__":
    a = app()
    a.mainloop()