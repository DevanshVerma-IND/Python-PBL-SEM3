import os
import json
from datetime import datetime

sectionListFile = "sectionlist.json"
sectionsFile = "sections.json"
teacherSectionsFile = "teachersections.json"
sectionSubjectsFile = "sectionsubjects.json"  # This is your existing file
studentSubjectsFile = "studentsubjects.json"

def loadJson(filename, default):
    if not os.path.exists(filename):
        return default
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except:
        return default

def saveJson(filename, data):
    with open(filename, "w") as f:
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

def assignSectionFromList():
    lst = listSections(returnList=True)
    if not lst:
        return
    num = input("Choose section number to assign: ").strip()
    if not num.isdigit():
        print("Invalid choice.")
        return
    idx = int(num) - 1
    if not (0 <= idx < len(lst)):
        print("Invalid section number.")
        return
    roll = input("Enter student roll no: ").strip()
    if not roll:
        print("Invalid roll no.")
        return
    mapping = loadJson(sectionsFile, {})
    section_name = lst[idx]
    mapping[roll] = section_name
    saveJson(sectionsFile, mapping)
    
    # Update studentsubjects.json
    student_subjects = loadJson(studentSubjectsFile, {})
    subjects = getSubjectsForSection(section_name)  # Get from sectionsubjects.json
    student_subjects[roll] = {
        "section": section_name,
        "subjects": subjects
    }
    saveJson(studentSubjectsFile, student_subjects)
    
    # Initialize attendance
    initialize_attendance_for_student(roll, section_name)
    
    print(f"Assigned section {section_name} to {roll}.")

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