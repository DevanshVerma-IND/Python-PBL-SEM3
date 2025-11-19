import os
import json
from datetime import datetime
from datetime import date

section_list_file = "sectionlist.json"
sections_file = "sections.json"
teacher_sections_file = "teachersections.json"
section_subjects_file = "sectionsubjects.json"
student_subjects_file = "studentsubjects.json"

def load_json(filename, default):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    filepath = os.path.join(base_dir, filename)
    if not os.path.exists(filepath):
        return default
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(filename, data):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    filepath = os.path.join(base_dir, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

def get_subjects_for_section(section):
    section_subjects = load_json(section_subjects_file, {})
    return section_subjects.get(section.upper(), [])

def initialize_attendance_for_student(roll, section):
    try:
        import attendance
        subjects = get_subjects_for_section(section)
        if subjects:
            attendance.initialize_student_attendance(roll, section, subjects)
            print(f"Attendance initialized for {roll} in section {section}")
        else:
            print(f"No subjects found for section {section} in sectionsubjects.json")
    except Exception as e:
        print(f"Error initializing attendance: {e}")

def create_section():
    lst = load_json(section_list_file, [])
    lst = sorted({str(s).strip().upper() for s in lst if str(s).strip()})
    s = input("Enter new section (e.g., A): ").strip().upper()
    if not s:
        print("Invalid section.")
        return
    if s in lst:
        print("Section already exists.")
        return
    lst.append(s)
    save_json(section_list_file, sorted(lst))
    section_subjects = load_json(section_subjects_file, {})
    if s in ["AI", "BI", "CI", "DI"]:
        section_subjects[s] = ["Basic Maths", "English-I", "C Lang", "Electronics", "Computer Networking"]
    elif s in ["AIII", "BIII", "CIII", "DIII"]:
        section_subjects[s] = ["DSA", "English-III", "Maths-III", "Artificial Intelligence", "Operating System"]
    elif s in ["AV", "BV", "CV", "DV"]:
        section_subjects[s] = ["English-V", "Machine Learning", "Algorithm", "OOP", "Database"]
    save_json(section_subjects_file, section_subjects)
    print(f"Section {s} created.")

def list_sections(return_list=False):
    lst = load_json(section_list_file, [])
    lst = sorted({str(s).strip().upper() for s in lst if str(s).strip()})
    if not lst:
        print("No sections available. Create one first.")
        return [] if return_list else None
    print("\nSections:")
    for i, s in enumerate(lst, 1):
        print(f" {i}. {s}")
    return lst if return_list else None

import json, os
from datetime import date

def assign_section_from_list():
    try:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        def load_json(fname, default):
            path = os.path.join(base_dir, fname)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            return default

        def save_json(fname, data):
            path = os.path.join(base_dir, fname)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

        rollnumbers = load_json("rollnumbers.json", {})
        sections = load_json("sections.json", {})
        sectionsubjects = load_json("sectionsubjects.json", {})
        studentsubjects = load_json("studentsubjects.json", {})
        attendance_master = load_json("attendance_master.json", {"attendance_records": {}, "metadata": {}})

        student_map = rollnumbers.get("map", {}).get("student", {})
        if not student_map:
            print("No students found in rollnumbers.json")
            return

        print("\n--- Assign Section to Student ---")
        for nm, rv in student_map.items():
            current_section = sections.get(rv, "Not Assigned")
            print(f"{rv} - {nm} (Section: {current_section})")

        roll = input("\nEnter student roll number to assign section: ").strip()
        if roll not in student_map.values():
            print("Invalid roll number.")
            return

        student_name = next((n for n, r in student_map.items() if r == roll), roll)
        section_choice = input(f"Enter section name to assign for {student_name} ({roll}): ").strip()

        if not section_choice:
            print("Section name cannot be empty.")
            return

        sections[roll] = section_choice
        save_json("sections.json", sections)
        print(f"Assigned section '{section_choice}' to student with roll number {roll} successfully!")

        subjects = sectionsubjects.get(section_choice)
        if not subjects or not isinstance(subjects, list):
            print(f"Section '{section_choice}' not found in sectionsubjects.json or has no subjects.")
            return

        studentsubjects[roll] = {
            "section": section_choice,
            "subjects": subjects
        }
        save_json("studentsubjects.json", studentsubjects)
        print(f"Updated studentsubjects.json for {roll}")

        attendance_records = attendance_master.get("attendance_records", {})
        if roll not in attendance_records:
            subjects_dict = {
                sub: {
                    "subject_name": sub,
                    "total_working_days": 0,
                    "total_present_days": 0,
                    "attendance_percentage": 0.0,
                    "last_updated": str(date.today())
                }
                for sub in subjects
            }
            attendance_records[roll] = {
                "name": student_name,
                "section": section_choice,
                "subjects": subjects_dict
            }
            print(f"Attendance record created for roll {roll}")
        else:
            attendance_records[roll]["section"] = section_choice
            print(f"Updated existing attendance record for roll {roll}")

        attendance_master["attendance_records"] = attendance_records
        attendance_master.setdefault("metadata", {})
        attendance_master["metadata"]["last_updated"] = str(date.today())
        attendance_master["metadata"]["total_students"] = len(attendance_records)
        save_json("attendance_master.json", attendance_master)

    except Exception as e:
        print("Error while assigning section:", e)

def assign_section_to_teacher():
    lst = list_sections(return_list=True)
    if not lst:
        return
    teacher = input("Enter teacher username: ").strip()
    if not teacher:
        print("Invalid teacher username.")
        return
    print("\nSelect section numbers to assign to this teacher (comma separated):")
    for i, sec in enumerate(lst, 1):
        print(f" {i}. {sec}")
    nums = input("Enter numbers: ").strip()
    indexes = []
    for x in nums.split(","):
        if x.strip().isdigit():
            idx = int(x.strip()) - 1
            if 0 <= idx < len(lst):
                indexes.append(idx)
    chosen = [lst[i] for i in indexes]
    if not chosen:
        print("No valid sections selected.")
        return
    tmap = load_json(teacher_sections_file, {})
    tmap[teacher] = sorted(set(chosen))
    save_json(teacher_sections_file, tmap)
    print(f"Assigned sections {', '.join(tmap[teacher])} to {teacher}.")

def view_my_sections(teacher_name):
    tmap = load_json(teacher_sections_file, {})
    secs = tmap.get(teacher_name, [])
    return secs

def view_section_assignments():
    mapping = load_json(sections_file, {})
    if not mapping:
        print("No students assigned yet.")
        return
    bysec = {}
    for roll, sec in mapping.items():
        sec = str(sec).strip().upper()
        bysec.setdefault(sec, []).append(roll)
    print("\nCurrent section assignments:")
    for sec in sorted(bysec.keys()):
        print(f" Section {sec}: {', '.join(sorted(bysec[sec]))}")

def get_section_for_roll(roll):
    mapping = load_json(sections_file, {})
    return mapping.get(str(roll).strip(), "Not assigned")

def list_teacher_sections(teacher_name):
    tmap = load_json(teacher_sections_file, {})
    return tmap.get(teacher_name, [])

def get_student_subjects(roll):
    student_subjects = load_json(student_subjects_file, {})
    student_data = student_subjects.get(roll, {})
    return student_data.get("subjects", [])

def view_student_subjects(roll):
    subjects = get_student_subjects(roll)
    section = get_section_for_roll(roll)
    if section == "Not assigned":
        print(f"Student {roll} is not assigned to any section.")
        return
    if not subjects:
        print(f"No subjects assigned to student {roll} in section {section}.")
        return
    print(f"\nSubjects assigned to {roll} (Section {section}):")
    for i, subject in enumerate(subjects, 1):
        print(f" {i}. {subject}")

def initialize_all_attendance_records():
    try:
        import attendance
        sections_data = load_json(sections_file, {})
        if not sections_data:
            print("No students have been assigned to sections yet.")
            return
        count = 0
        for roll, section in sections_data.items():
            subjects = get_subjects_for_section(section)
            if subjects:
                attendance.initialize_student_attendance(roll, section, subjects)
                count += 1
        print(f"Attendance records initialized for {count} students.")
    except Exception as e:
        print(f"Error initializing attendance records: {e}")

def check_sectionsubjects_file():
    section_subjects = load_json(section_subjects_file, {})
    if not section_subjects:
        print("Warning: sectionsubjects.json is empty or doesn't exist.")
        print("Please make sure you have the section-subject mappings in sectionsubjects.json")
        return False
    return True

check_sectionsubjects_file()
