import os
import hashlib
import secrets
import hmac
import getpass
import pwinput
import subject
import menu
DATAFILE = "userdata.bin"

class User:
    def __init__(self, username, role, salt, pwd_hash, question, ans_salt, ans_hash):
        self.username = username
        self.role = role
        self.salt = salt
        self.pwd_hash = pwd_hash
        self.question = question
        self.ans_salt = ans_salt
        self.ans_hash = ans_hash
        self.next = None

class UserList:
    def __init__(self):
        self.head = None

    def add(self, username, role, salt, pwd_hash, question, ans_salt, ans_hash):
        u = User(username, role, salt, pwd_hash, question, ans_salt, ans_hash)
        if not self.head:
            self.head = u
        else:
            t = self.head
            while t.next:
                t = t.next
            t.next = u # type: ignore

    def find(self, username):
        t = self.head
        while t:
            if t.username == username:
                return t
            t = t.next
        return None

    def all(self):
        out = []
        t = self.head
        while t:
            out.append((t.username, t.role, t.salt, t.pwd_hash, t.question, t.ans_salt, t.ans_hash))
            t = t.next
        return out

def load_users():
    users = UserList()
    if not os.path.exists(DATAFILE):
        return users
    roles = ("admin", "teacher", "student")
    try:
        with open(DATAFILE, "rb") as f:
            for line in f:
                try:
                    s = line.decode("utf-8").strip()
                    if not s:
                        continue
                    p = s.split(":")
                    if len(p) != 7:
                        continue
                    if p[1] in roles:
                        username, role, salt, pwd_hash, question, ans_salt, ans_hash = p
                    elif p[3] in roles:
                        username, salt, pwd_hash, role, question, ans_salt, ans_hash = p
                    else:
                        continue
                    users.add(username, role, salt, pwd_hash, question, ans_salt, ans_hash)
                except:
                    pass
    except:
        pass
    return users

def save_users(users):
    try:
        with open(DATAFILE, "wb") as f:
            for u in users.all():
                try:
                    f.write((":".join(u) + "\n").encode("utf-8"))
                except:
                    pass
    except:
        pass

def make_salt():
    return secrets.token_hex(16)

def make_hash(text, salt):
    h = hashlib.sha256()
    try:
        salt_bytes = bytes.fromhex(salt)
    except ValueError:
        salt_bytes = salt.encode("utf-8")
    h.update(salt_bytes)
    h.update(text.encode("utf-8"))
    return h.hexdigest()

def create_account(users):
    role = input("Are you a teacher, student, or admin? (teacher/student/admin): ").strip().lower()
    if role == "admin":
        admin_pass = "admin@123"
        entered = pwinput.pwinput("Enter admin creation password: ")
        if entered != admin_pass:
            print("Incorrect admin creation password.")
            return
    if role not in ("student", "teacher", "admin"):
        print("Invalid role.")
        return

    username = input("Enter username: ").strip()
    if not username:
        print("Username cannot be empty.")
        return
    if users.find(username):
        print("Username already exists.")
        return

    questions = [
        "What is the name of your first pet?",
        "What is the first dish you learned to cook?",
        "What is your favorite book?",
        "What is the first word you said (except mother and father)?",
        "What city were you born in?"
    ]
    for i, q in enumerate(questions, 1):
        print(f" {i}. {q}")
    while True:
        try:
            q_choice = int(input("Enter question number (1-5): "))
            if 1 <= q_choice <= len(questions):
                break
        except:
            pass
    sec_q = questions[q_choice-1]
    sec_a = input("Enter answer to your security question: ").strip()
    sec_a_salt = make_salt()
    sec_a_hash = make_hash(sec_a, sec_a_salt)

    # ✅ Password length validation
    while True:
        password = pwinput.pwinput("Enter password (must be more than 4 characters): ", mask='*')
        if len(password) <= 4:
            print("❌ Password too short! It must be more than 4 characters.")
        else:
            break

    salt = make_salt()
    pwd_hash = make_hash(password, salt)

    users.add(username, role, salt, pwd_hash, sec_q, sec_a_salt, sec_a_hash)
    save_users(users)
    rno = subject.getRollNumber(username, role)
    print(f"Your roll no is {rno}")
    print("✅ Account created successfully!\n")


def login(users):
    username = input("Enter username: ").strip()
    user = users.find(username)
    if not user:
        print("No such user.")
        return
    password = pwinput.pwinput("Enter password: ", mask='*')
    if not hmac.compare_digest(make_hash(password, user.salt), user.pwd_hash):
        print("Wrong password.")
        return
    print(f"Login successful as {user.role}!")
    if user.role == "admin":
        while True:
            print("\n1. Change own password")
            print("2. Change another user's password")
            print("3. To open admin menu")
            print("4. Logout")
            choice = input("Enter choice: ").strip()
            if choice == "1":
                print(f"Security question: {user.question}")
                ans = input("Enter answer: ").strip()
                if make_hash(ans, user.ans_salt) != user.ans_hash:
                    print("Incorrect answer. Cannot change password.")
                    continue
                newpass = pwinput.pwinput("Enter new password: ", mask='*')
                newsalt = make_salt()
                newhash = make_hash(newpass, newsalt)
                user.salt = newsalt
                user.pwd_hash = newhash
                save_users(users)
                print("Password changed!")
            elif choice == "2":
                target = input("Enter username to change password: ").strip()
                target_user = users.find(target)
                if not target_user:
                    print("User not found.")
                elif target_user.role == "admin":
                    print("Cannot change password for another admin.")
                else:
                    newpass = pwinput.pwinput("Enter new password for user: ", mask='*')
                    newsalt = make_salt()
                    newhash = make_hash(newpass, newsalt)
                    target_user.salt = newsalt
                    target_user.pwd_hash = newhash
                    save_users(users)
                    print("Password changed for user.")
            elif choice == "3":
                menu.openMenu(user.role, user.username)
            elif choice == "4":
                print("Logged out.\n")
                return
            else:
                print("Invalid choice.")
    elif user.role == "teacher":
        while True:
            print("\n1. Change password")
            print("2. To open teacher menu")
            print("3. Logout")
            choice = input("Enter choice: ").strip()
            if choice == "1":
                newpass = pwinput.pwinput("Enter new password: ", mask='*')
                newsalt = make_salt()
                newhash = make_hash(newpass, newsalt)
                user.salt = newsalt
                user.pwd_hash = newhash
                save_users(users)
                print("Password changed!")
            elif choice == "2":
                menu.openMenu(user.role, user.username)
            elif choice == "3":
                print("Logged out.\n")
                return
            else:
                print("Invalid choice.")
    elif user.role == "student":
        while True:
            print("\n1. Change password")
            print("2. To open student menu")
            print("3. Logout")
            choice = input("Enter choice: ").strip()
            if choice == "1":
                newpass = pwinput.pwinput("Enter new password: ", mask='*')
                newsalt = make_salt()
                newhash = make_hash(newpass, newsalt)
                user.salt = newsalt
                user.pwd_hash = newhash
                save_users(users)
                print("Password changed!")
            elif choice == "2":
                menu.openMenu(user.role, user.username)
            elif choice == "3":
                print("Logged out.\n")
                return
            else:
                print("Invalid choice.")

def forgot_password(users):
    username = input("Enter username to reset password: ").strip()
    user = users.find(username)
    if not user:
        return
    print(f"Security question: {user.question}")
    ans = input("Enter answer: ").strip()
    if make_hash(ans, user.ans_salt) != user.ans_hash:
        return
    newpass = pwinput.pwinput("Enter new password: ", mask='*')
    newsalt = make_salt()
    newhash = make_hash(newpass, newsalt)
    user.salt = newsalt
    user.pwd_hash = newhash
    save_users(users)
def migrate_userdata_interactive():
    roles = ("admin", "teacher", "student")
    if not os.path.exists(DATAFILE):
        print("No userdata.bin found")
        return
    lines = []
    with open(DATAFILE, "rb") as f:
        for line in f:
            s = line.decode("utf-8").strip()
            if not s:
                continue
            p = s.split(":")
            if len(p) != 7:
                continue
            if p[1] in roles:
                username, role, salt, pwd_hash, question, ans_salt, ans_hash = p
            elif p[3] in roles:
                username, salt, pwd_hash, role, question, ans_salt, ans_hash = p
            else:
                username = p[0]
                salt = p[1]
                pwd_hash = p[2]
                question = p[4]
                ans_salt = p[5]
                ans_hash = p[6]
                while True:
                    role = input(f"Enter role for '{username}' (admin/teacher/student) [student]: ").strip().lower()
                    if role == "":
                        role = "student"
                    if role in roles:
                        break
            lines.append(":".join([username, role, salt, pwd_hash, question, ans_salt, ans_hash]))
    with open(DATAFILE, "wb") as f:
        for s in lines:
            f.write((s + "\n").encode("utf-8"))
    print("Migration complete.")
