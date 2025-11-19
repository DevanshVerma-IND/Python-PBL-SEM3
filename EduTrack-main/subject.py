import os
import json

subjects_file = "subjects.json"
rollnumbers_file = "rollnumbers.json"

def load_json(filename, default):
    if not os.path.exists(filename):
        return default
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def add_subject():
    data = load_json(subjects_file, {"subjects": []})
    subjects = data.get("subjects", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])

    name = input("Enter subject name: ").strip()
    code = input("Enter subject code [eg- TMA101]: ").strip().upper()

    if any(s.get("code") == code for s in subjects):
        print("Subject code already exists.")
        return

    subjects.append({"name": name, "code": code})
    to_save = {"subjects": subjects}
    save_json(subjects_file, to_save)
    print("Subject added.")

def list_subjects():
    data = load_json(subjects_file, {"subjects": []})
    subjects = data.get("subjects", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])

    if not subjects:
        print("No subjects available.")
        return []

    print("\nSubjects:")
    for i, s in enumerate(subjects, 1):
        print(f" {i}. {s.get('name','')} ({s.get('code','')})")
    return subjects

def get_roll_number(name, role="student"):
    db = load_json(rollnumbers_file, {})

    if not isinstance(db, dict) or "map" not in db or "counters" not in db:
        db = {
            "map": {
                "student": {},
                "teacher": {},
                "admin": {}
            },
            "counters": {
                "student": 0,
                "teacher": 0,
                "admin": 0
            }
        }

    if name in db["map"].get(role, {}):
        return db["map"][role][name]

    db["counters"][role] = db["counters"].get(role, 0) + 1
    n = db["counters"][role]

    if role == "teacher":
        roll = f"T{str(n).zfill(4)}"
    elif role == "admin":
        roll = f"A{str(n).zfill(4)}"
    else:
        roll = f"2025{str(n).zfill(4)}"

    db["map"][role][name] = roll
    save_json(rollnumbers_file, db)
    return roll

# Note: camelCase aliases removed to enforce snake_case naming.
