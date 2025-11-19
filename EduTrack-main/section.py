import os
import json
from datetime import datetime
from datetime import date

sectionListFile = "sectionlist.json"
sectionsFile = "sections.json"
teacherSectionsFile = "teachersections.json"
sectionSubjectsFile = "sectionsubjects.json"  # This is your existing file
studentSubjectsFile = "studentsubjects.json"

def loadJson(filename, default):
    # Resolve filename relative to project root (one level above this module),
    # so JSON files placed next to the EduTrack-main folder are used.
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    filepath = os.path.join(base_dir, filename)
    if not os.path.exists(filepath):
        return default
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception:
        return default

def saveJson(filename, data):
    # Save JSON relative to project root (one level above this module)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    filepath = os.path.join(base_dir, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

def getSubjectsForSection(section):
    """Get the subjects assigned to a specific section from sectionsubjects.json"""
    section_subjects = loadJson(sectionSubjectsFile, {})
    return section_subjects.get(section.upper(), [])

def initialize_attendance_for_student(roll, section):
    """Initialize attendance record when student is assigned to section"""
    try:
        # Import attendance module
        import attendance
        
        # Get subjects for this section from sectionsubjects.json (your existing file)
        subjects = getSubjectsForSection(section)
        
        if subjects:
            attendance.initialize_student_attendance(roll, section, subjects)
            print(f"Attendance initialized for {roll} in section {section}")
        else:
            print(f"No subjects found for section {section} in sectionsubjects.json")
    except Exception as e:
        print(f"Error initializing attendance: {e}")

def createSection():
    lst = loadJson(sectionListFile, [])
    lst = sorted({str(s).strip().upper() for s in lst if str(s).strip()})
    s = input("Enter new section (e.g., A): ").strip().upper()
    if not s:
        print("Invalid section.")
        return
    if s in lst:
        print("Section already exists.")
        return
    lst.append(s)
    saveJson(sectionListFile, sorted(lst))
    
    # Initialize section subjects mapping for the new section if it matches patterns
    section_subjects = loadJson(sectionSubjectsFile, {})
    if s in ["AI", "BI", "CI", "DI"]:
        section_subjects[s] = ["Basic Maths", "English-I", "C Lang", "Electronics", "Computer Networking"]
    elif s in ["AIII", "BIII", "CIII", "DIII"]:
        section_subjects[s] = ["DSA", "English-III", "Maths-III", "Artificial Intelligence", "Operating System"]
    elif s in ["AV", "BV", "CV", "DV"]:
        section_subjects[s] = ["English-V", "Machine Learning", "Algorithm", "OOP", "Database"]
    
    saveJson(sectionSubjectsFile, section_subjects)
    print(f"Section {s} created.")

def listSections(returnList=False):
    lst = loadJson(sectionListFile, [])
    lst = sorted({str(s).strip().upper() for s in lst if str(s).strip()})
    if not lst:
        print("No sections available. Create one first.")
        return [] if returnList else None
    print("\nSections:")
    for i, s in enumerate(lst, 1):
        print(f" {i}. {s}")
    return lst if returnList else None


import json, os
from datetime import date

def assignSectionFromList():
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

        # Load required JSON files
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

        # --- Update sections.json ---
        sections[roll] = section_choice
        save_json("sections.json", sections)
        print(f"Assigned section '{section_choice}' to student with roll number {roll} successfully!")

        # --- Get subjects for this section ---
        subjects = sectionsubjects.get(section_choice)
        if not subjects or not isinstance(subjects, list):
            print(f"Section '{section_choice}' not found in sectionsubjects.json or has no subjects.")
            return

        # --- Update studentsubjects.json ---
        studentsubjects[roll] = {
            "section": section_choice,
            "subjects": subjects
        }
        save_json("studentsubjects.json", studentsubjects)
        print(f"Updated studentsubjects.json for {roll}")

        # --- Update attendance_master.json ---
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


def assignSectionToTeacher():
    lst = listSections(returnList=True)
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
    tmap = loadJson(teacherSectionsFile, {})
    tmap[teacher] = sorted(set(chosen))
    saveJson(teacherSectionsFile, tmap)
    print(f"Assigned sections {', '.join(tmap[teacher])} to {teacher}.")

def viewMySections(teachername):
    tmap = loadJson(teacherSectionsFile, {})
    secs = tmap.get(teachername, [])
    if not secs:
        print("No sections assigned to this teacher.")
        return
    print(f"\nSections assigned to {teachername}:")
    for s in secs:
        print(f" {s}")

def viewSectionAssignments():
    mapping = loadJson(sectionsFile, {})
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

def getSectionForRoll(roll):
    mapping = loadJson(sectionsFile, {})
    return mapping.get(str(roll).strip(), "Not assigned")

def listTeacherSections(teachername):
    tmap = loadJson(teacherSectionsFile, {})
    return tmap.get(teachername, [])

def getStudentSubjects(roll):
    """Get subjects assigned to a student"""
    student_subjects = loadJson(studentSubjectsFile, {})
    student_data = student_subjects.get(roll, {})
    return student_data.get("subjects", [])

def viewStudentSubjects(roll):
    """View subjects assigned to a specific student"""
    subjects = getStudentSubjects(roll)
    section = getSectionForRoll(roll)
    
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
    """Initialize attendance records for all students who have sections assigned"""
    try:
        import attendance
        
        # Load all necessary data
        sections_data = loadJson(sectionsFile, {})
        
        if not sections_data:
            print("No students have been assigned to sections yet.")
            return
        
        count = 0
        for roll, section in sections_data.items():
            subjects = getSubjectsForSection(section)  # Get from sectionsubjects.json
            if subjects:
                attendance.initialize_student_attendance(roll, section, subjects)
                count += 1
        
        print(f"Attendance records initialized for {count} students.")
        
    except Exception as e:
        print(f"Error initializing attendance records: {e}")

# Check if sectionsubjects.json exists and has data
def check_sectionsubjects_file():
    """Check if sectionsubjects.json exists and has the required data"""
    section_subjects = loadJson(sectionSubjectsFile, {})
    if not section_subjects:
        print("Warning: sectionsubjects.json is empty or doesn't exist.")
        print("Please make sure you have the section-subject mappings in sectionsubjects.json")
        return False
    return True

# Check the file when module is imported
check_sectionsubjects_file()