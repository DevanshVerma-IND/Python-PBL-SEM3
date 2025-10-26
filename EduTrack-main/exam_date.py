import json
from datetime import datetime
import os

SUBJECTSFILE = "subjects.json"
EXAMFILE = "exam_date.json"
ALLOCATIONFILE = "sectionsubjects.json"
STUDENTSUBJECTSFILE = "studentsubjects.json"

# Subject name to code mapping based on your exam_date.json
SUBJECT_NAME_TO_CODE = {
    "Basic Maths": "TMA101",
    "English-I": "TEA101",
    "C Lang": "TCA101",
    "Electronics": "TEC101",
    "English-III": "TEA301",
    "Maths-III": "TMA301",
    "Computer Networking": "TCN101",
    "DSA": "TCS101",
    "Artificial Intelligence": "TAI101",
    "Operating System": "TOS01",
    "English-V": "TEA501",
    "Machine Learning": "TML101",
    "Algorithm": "TAL101",
    "OOP": "TOP101",
    "Database": "TDB101"
}

def loadSubjects():
    try:
        with open(SUBJECTSFILE, "r") as f:
            data = json.load(f)
    except:
        return []
    
    if isinstance(data, dict) and "subjects" in data:
        return data["subjects"]
    elif isinstance(data, list):
        return data
    return []

def loadSubjectAllocation():
    """Load section-subject allocation data"""
    try:
        with open(ALLOCATIONFILE, "r") as f:
            return json.load(f)
    except:
        return {}

def loadStudentSubjects():
    """Load student subjects data"""
    try:
        with open(STUDENTSUBJECTSFILE, "r") as f:
            data = json.load(f)
        return data
    except:
        return {}

def loadExamMap():
    try:
        with open(EXAMFILE, "r") as f:
            raw = json.load(f)
    except:
        raw = {}
    
    if isinstance(raw, dict) and "exam_schedule" in raw:
        items = raw["exam_schedule"]
    elif isinstance(raw, list):
        items = raw
    else:
        items = []
    
    examMap = {}
    for it in items:
        if isinstance(it, dict):
            code = (it.get("subject_code") or it.get("code") or "").upper()
            if not code:
                continue
            examMap[code] = {
                "subjectName": it.get("subject_name") or it.get("name") or "",
                "examDate": it.get("exam_date") or ""
            }
    return examMap

def saveExamMap(examMap):
    payload = {"exam_schedule": []}
    for code in sorted(examMap.keys()):
        entry = examMap[code]
        payload["exam_schedule"].append({
            "subject_code": code,
            "subject_name": entry.get("subjectName", ""),
            "exam_date": entry.get("examDate", "")
        })
    with open(EXAMFILE, "w") as f:
        json.dump(payload, f, indent=2)

def setExamDatesAdmin():
    subjects = loadSubjects()
    if not subjects:
        print("No subjects available.")
        return
    
    print("\nAvailable subjects:")
    for i, s in enumerate(subjects, 1):
        print(f"{i}. {s.get('name','')} ({s.get('code','')})")
    
    sel = input("Enter subject numbers to set exam date (comma separated): ").strip()
    if not sel:
        return
    
    try:
        indexes = [int(x.strip())-1 for x in sel.split(",") if x.strip().isdigit()]
    except:
        print("Invalid input.")
        return
    
    examMap = loadExamMap()
    for idx in indexes:
        if 0 <= idx < len(subjects):
            s = subjects[idx]
            code = (s.get("code") or "").upper()
            name = s.get("name") or ""
            dateStr = input(f"Enter exam date for {name} ({code}) [DD/MM/YYYY]: ").strip()
            try:
                datetime.strptime(dateStr, "%d/%m/%Y")
            except:
                print(f"Skipped {code}: invalid date format.")
                continue
            examMap[code] = {"subjectName": name, "examDate": dateStr}
    
    saveExamMap(examMap)
    print("Exam dates saved.")

def getExamDate(subjectCode):
    if not subjectCode:
        return "Not set"
    examMap = loadExamMap()
    return examMap.get(subjectCode.upper(), {}).get("examDate", "Not set")

def getSubjectCode(subject_name):
    """Get the proper subject code from subject name"""
    return SUBJECT_NAME_TO_CODE.get(subject_name, subject_name.upper().replace(" ", "_"))

def loadSectionSubjects(sectionName):
    """Load subjects for a section from subject allocation data"""
    sectionName = (sectionName or "").strip().upper()
    
    # First try to load from subject allocation file
    subject_allocation = loadSubjectAllocation()
    if subject_allocation and sectionName in subject_allocation:
        subjects = subject_allocation[sectionName]
        if subjects:
            # Convert subject names to proper format with correct codes
            result = []
            for subject_name in subjects:
                result.append({
                    "name": subject_name,
                    "code": getSubjectCode(subject_name)
                })
            return result, True
    
    # Fallback to student subjects data
    student_subjects = loadStudentSubjects()
    if student_subjects:
        # Find subjects from any student in this section
        for roll, data in student_subjects.items():
            if isinstance(data, dict) and data.get("section") == sectionName:
                subjects = data.get("subjects", [])
                if subjects:
                    result = []
                    for subject_name in subjects:
                        result.append({
                            "name": subject_name,
                            "code": getSubjectCode(subject_name)
                        })
                    return result, True
    
    # Final fallback to all subjects
    subjects = loadSubjects()
    return subjects, False

def viewAllExamDates():
    subjects = loadSubjects()
    if not subjects:
        print("No subjects available.")
        return
    
    examMap = loadExamMap()
    print("\nExam Dates (All Subjects):")
    for s in subjects:
        code = (s.get("code") or "").upper()
        name = s.get("name") or ""
        dateStr = examMap.get(code, {}).get("examDate", "Not set")
        print(f" {name} ({code}) - Exam: {dateStr}")

def viewSectionExamDates(sectionName):
    if sectionName == "Not assigned":
        print("Section not assigned.")
        return
        
    subs, isAllocated = loadSectionSubjects(sectionName)
    if not subs:
        print("No subjects available for this section.")
        return
    
    examMap = loadExamMap()
    title = f"Section {sectionName} Exam Dates"
    print(f"\n{title}:")
    
    if not isAllocated:
        print("(No section-specific allocation found; showing all subjects.)")
    else:
        print("(Showing section-specific subjects)")
    
    for s in subs:
        code = (s.get("code") or "").upper()
        name = s.get("name") or ""
        dateStr = examMap.get(code, {}).get("examDate", "Not set")
        print(f" {name} ({code}) - Exam: {dateStr}")

def viewStudentExamSchedule(username):
    import subject
    import section
    roll = subject.getRollNumber(username, "student")
    sec = section.getSectionForRoll(roll)
    if sec == "Not assigned":
        print("Section not assigned.")
        return
    viewSectionExamDates(sec)