import json
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime

ATTENDANCE_MASTER_FILE = "attendance_master.json"
TEACHER_SECTIONS_FILE = "teachersections.json"
SECTIONS_FILE = "sections.json"
STUDENT_SUBJECTS_FILE = "studentsubjects.json"
SUBJECTS_FILE = "subjects.json"

def _resolve_path(filename):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_dir, filename)

def load_json_file(filename):
    """Load JSON data from file (resolved to project root)"""
    filepath = _resolve_path(filename)
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception as e:
        print("Error loading JSON", e)
        return {}

def save_json_file(filename, data):
    """Save JSON data to file (resolved to project root)"""
    filepath = _resolve_path(filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def load_attendance_master():
    """Load attendance data from master file"""
    return load_json_file(ATTENDANCE_MASTER_FILE)

def save_attendance_master(data):
    """Save attendance data to master file"""
    data["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    data["metadata"]["total_students"] = len(data["attendance_records"])
    save_json_file(ATTENDANCE_MASTER_FILE, data)

def can_teacher_access_section(teachername, section):
    """Check if teacher is authorized to access this section"""
    teacher_sections = load_json_file(TEACHER_SECTIONS_FILE)
    teacher_sections_list = teacher_sections.get(teachername, [])
    return section.upper() in [s.upper() for s in teacher_sections_list]

def get_student_section(roll_number):
    """Get section of a student"""
    sections = load_json_file(SECTIONS_FILE)
    return sections.get(roll_number, "Not assigned")

def initialize_student_attendance(roll_number, section, subject_names):
    """Initialize attendance record for a new student"""
    attendance_data = load_attendance_master()
    subjects_data = load_json_file(SUBJECTS_FILE)
    
    # Create subject name to code mapping
    subject_name_to_code = {}
    for subject in subjects_data.get("subjects", []):
        subject_name_to_code[subject["name"]] = subject["code"]
    
    if roll_number not in attendance_data.get("attendance_records", {}):
        attendance_data.setdefault("attendance_records", {})[roll_number] = {
            "name": roll_number,
            "section": section,
            "subjects": {}
        }
        
        # Initialize all subjects with zero attendance
        for subject_name in subject_names:
            subject_code = subject_name_to_code.get(subject_name)
            if subject_code:
                attendance_data["attendance_records"][roll_number]["subjects"][subject_code] = {
                    "subject_name": subject_name,
                    "total_working_days": 0,
                    "total_present_days": 0,
                    "attendance_percentage": 0.0,
                    "last_updated": datetime.now().strftime("%Y-%m-%d")
                }
        
        # Initialize metadata if not exists
        if "metadata" not in attendance_data:
            attendance_data["metadata"] = {
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "total_students": 0,
                "academic_year": "2024-2025",
                "total_subjects": len(subjects_data.get("subjects", []))
            }
        
        save_attendance_master(attendance_data)
        print(f"Attendance initialized for student {roll_number} in section {section}")

def view_attendance(teachername=None, student_roll=None):
    """View attendance chart - can be used by teachers for their sections or students for their own"""
    attendance_data = load_attendance_master()
    
    if student_roll:
        # Student viewing their own attendance
        if student_roll in attendance_data.get("attendance_records", {}):
            student_data = attendance_data["attendance_records"][student_roll]
            subjects = []
            attendance_percentages = []
            
            for subject_code, subject_data in student_data["subjects"].items():
                subjects.append(subject_data["subject_name"])
                attendance_percentages.append(subject_data["attendance_percentage"])
            
            if not subjects:
                print("No attendance data found for this student.")
                return
            
            # Create chart
            colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(subjects))) # type: ignore
            plt.figure(figsize=(12, 6))
            bars = plt.bar(subjects, attendance_percentages, color=colors, edgecolor="gray", linewidth=0.8)
            
            plt.title(f"Attendance Percentage for {student_roll}", fontsize=16, fontweight="bold", pad=20)
            plt.xlabel("Subjects", fontsize=12, labelpad=10)
            plt.ylabel("Attendance (%)", fontsize=12, labelpad=10)
            plt.xticks(rotation=45, ha="right", fontsize=10)
            plt.yticks(fontsize=10)
            plt.grid(axis="y", linestyle="--", alpha=0.4)
            
            for bar, value in zip(bars, attendance_percentages):
                plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, 
                        f"{value:.1f}%", ha="center", fontsize=9, fontweight="bold")
            
            plt.tight_layout()
            plt.show()
        else:
            print("No attendance data found for this student.")
    
    elif teachername:
        # Teacher viewing attendance for their sections
        teacher_sections = load_json_file(TEACHER_SECTIONS_FILE)
        teacher_sections_list = teacher_sections.get(teachername, [])
        
        if not teacher_sections_list:
            print("No sections assigned to this teacher.")
            return
        
        # Collect data for all students in teacher's sections
        all_subjects = []
        all_attendance = []
        
        for roll_number, student_data in attendance_data.get("attendance_records", {}).items():
            if student_data["section"] in teacher_sections_list:
                for subject_code, subject_data in student_data["subjects"].items():
                    all_subjects.append(f"{roll_number} - {subject_data['subject_name']}")
                    all_attendance.append(subject_data["attendance_percentage"])
        
        if not all_subjects:
            print("No attendance data found for your sections.")
            return
        
        # Create chart
        colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(all_subjects))) # type: ignore
        plt.figure(figsize=(14, 8))
        bars = plt.bar(all_subjects, all_attendance, color=colors, edgecolor="gray", linewidth=0.8)
        
        plt.title(f"Attendance Percentage - Teacher {teachername}", fontsize=16, fontweight="bold", pad=20)
        plt.xlabel("Students - Subjects", fontsize=12, labelpad=10)
        plt.ylabel("Attendance (%)", fontsize=12, labelpad=10)
        plt.xticks(rotation=45, ha="right", fontsize=8)
        plt.yticks(fontsize=10)
        plt.grid(axis="y", linestyle="--", alpha=0.4)
        
        for bar, value in zip(bars, all_attendance):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, 
                    f"{value:.1f}%", ha="center", fontsize=7, fontweight="bold")
        
        plt.tight_layout()
        plt.show()

def mark_attendance(teachername, student_roll, subject_code, is_present=True):
    """Mark attendance for a student - only allowed for authorized teachers.
    Accepts subject_code (e.g. TEA501). Works with attendance_master.json entries
    that can be keyed by subject code or subject name; will auto-create missing entry.
    """
    try:
        # 1. Check student's section
        student_section = get_student_section(student_roll)
        if student_section == "Not assigned":
            print("Student not assigned to any section.")
            return False

        # 2. Verify teacher authorization
        if not can_teacher_access_section(teachername, student_section):
            print(f"Unauthorized: You are not assigned to section {student_section}.")
            return False

        # 3. Load attendance master
        attendance_data = load_attendance_master()
        attendance_records = attendance_data.get("attendance_records", {})

        # If student record missing, create basic one
        if student_roll not in attendance_records:
            attendance_records[student_roll] = {
                "name": student_roll,
                "section": student_section,
                "subjects": {}
            }

        student_record = attendance_records[student_roll]
        subjects_dict = student_record.get("subjects", {})

        # 4. Load subjects.json to map code -> name
        subj_file = load_json_file(SUBJECTS_FILE)
        subj_list = subj_file.get("subjects", []) if isinstance(subj_file, dict) else []
        code_to_name = {s.get("code"): s.get("name") for s in subj_list if isinstance(s, dict) and s.get("code")}

        subject_name_for_code = code_to_name.get(subject_code)

        # 5. Try to find the existing subject key in student's subjects:
        found_key = None

        # a) direct match by code (some records may already use codes as keys)
        if subject_code in subjects_dict:
            found_key = subject_code
        else:
            # b) if we can map code -> name, try name as key
            if subject_name_for_code and subject_name_for_code in subjects_dict:
                found_key = subject_name_for_code
            else:
                # c) try to find a key whose 'subject_name' equals the mapped name
                if subject_name_for_code:
                    for k, v in subjects_dict.items():
                        if isinstance(v, dict) and v.get("subject_name", "").strip().lower() == subject_name_for_code.strip().lower():
                            found_key = k
                            break

        # 6. If not found, create a new subject entry (key by code if code available, otherwise by name)
        if not found_key:
            # Determine the key we will use for the new subject entry
            new_key = subject_code if subject_code else (subject_name_for_code or subject_code or "UNKNOWN")
            new_subject_name = subject_name_for_code if subject_name_for_code else subject_code
            # ensure subjects_dict exists
            if not isinstance(subjects_dict, dict):
                subjects_dict = {}
            subjects_dict[new_key] = {
                "subject_name": new_subject_name,
                "total_working_days": 0,
                "total_present_days": 0,
                "attendance_percentage": 0.0,
                "last_updated": ""
            }
            found_key = new_key
            # attach back
            student_record["subjects"] = subjects_dict
            attendance_records[student_roll] = student_record
            # save immediately so subsequent read sees it
            save_attendance_master(attendance_data)
            print(f"⚠️ Subject entry for '{subject_code}' was missing for {student_roll}. Created new entry '{found_key}'.")

        # 7. Now get the subject data to update
        subject_data = subjects_dict.get(found_key)
        if not subject_data:
            print("Subject not found for this student after creation attempt.")
            return False

        # 8. Confirm action
        status = "present" if is_present else "absent"
        confirm = input(f"Mark {student_roll} as {status} for {subject_data.get('subject_name', found_key)}? (y/n): ").strip().lower()
        if confirm not in ["y", "yes"]:
            print("Attendance marking cancelled.")
            return False

        # 9. Update attendance counters
        subject_data["total_working_days"] = int(subject_data.get("total_working_days", 0)) + 1
        if is_present:
            subject_data["total_present_days"] = int(subject_data.get("total_present_days", 0)) + 1
            print(f"Marked {student_roll} present for {subject_data.get('subject_name', found_key)}")
        else:
            # absent: working days incremented already
            print(f"Marked {student_roll} absent for {subject_data.get('subject_name', found_key)}")

        # 10. Recalculate percentage
        tw = subject_data.get("total_working_days", 0)
        tp = subject_data.get("total_present_days", 0)
        if tw > 0:
            subject_data["attendance_percentage"] = round((tp / tw) * 100, 2)
        else:
            subject_data["attendance_percentage"] = 0.0

        # 11. Update last_updated
        subject_data["last_updated"] = datetime.now().strftime("%Y-%m-%d")

        # 12. Persist updated attendance_data
        attendance_records[student_roll] = student_record
        attendance_data["attendance_records"] = attendance_records
        save_attendance_master(attendance_data)

        print("Attendance updated successfully!")
        return True

    except Exception as e:
        print("Error while marking attendance:", e)
        return False


def update_attendance(teachername, student_roll, subject_code):
    """Update existing attendance record - only allowed for authorized teachers"""
    # Check authorization
    student_section = get_student_section(student_roll)
    if student_section == "Not assigned":
        print("Student not assigned to any section.")
        return

    if not can_teacher_access_section(teachername, student_section):
        print(f"Unauthorized: You are not assigned to section {student_section}.")
        return

    attendance_data = load_attendance_master()
    attendance_records = attendance_data.get("attendance_records", {})

    if student_roll not in attendance_records:
        print("Student not found in attendance records.")
        return

    student_record = attendance_records[student_roll]
    subjects_dict = student_record.get("subjects", {})

    # Load subjects.json to map code -> name
    subj_file = load_json_file(SUBJECTS_FILE)
    subj_list = subj_file.get("subjects", []) if isinstance(subj_file, dict) else []
    code_to_name = {s.get("code"): s.get("name") for s in subj_list if isinstance(s, dict) and s.get("code")}
    name_to_code = {s.get("name"): s.get("code") for s in subj_list if isinstance(s, dict) and s.get("name")}

    # Normalize input
    subject_code = subject_code.strip() if isinstance(subject_code, str) else subject_code

    # Try to find the student's subject entry in several ways:
    found_key = None     # key as stored in subjects_dict (could be code or name)

    # 1) Direct by code key
    if subject_code in subjects_dict:
        found_key = subject_code
    else:
        # 2) If code -> name mapping available, try that name as key
        subj_name = code_to_name.get(subject_code)
        if subj_name and subj_name in subjects_dict:
            found_key = subj_name
        else:
            # 3) Try to find a subject entry whose 'subject_name' matches the code->name
            if subj_name:
                for k, v in subjects_dict.items():
                    if isinstance(v, dict) and v.get("subject_name", "").strip().lower() == subj_name.strip().lower():
                        found_key = k
                        break
            # 4) Try if teacher passed subject *name* instead of code
            if not found_key and subject_code in name_to_code:
                # subject_code is actually a name, use it as key if present
                if subject_code in subjects_dict:
                    found_key = subject_code
            # 5) As last resort, try matching by subject_name field equals the provided string
            if not found_key:
                for k, v in subjects_dict.items():
                    if isinstance(v, dict) and v.get("subject_name", "").strip().lower() == str(subject_code).strip().lower():
                        found_key = k
                        break

    # If still not found, create a new subject entry keyed by the subject_code (preferred)
    if not found_key:
        # Determine subject_name to use
        subject_name = code_to_name.get(subject_code) or subject_code or "Unknown Subject"

        # Ensure the subjects_dict is a dict
        if not isinstance(subjects_dict, dict):
            subjects_dict = {}

        # Create entry keyed by subject_code so future marks by code work
        new_key = subject_code if subject_code else subject_name
        subjects_dict[new_key] = {
            "subject_name": subject_name,
            "total_working_days": 0,
            "total_present_days": 0,
            "attendance_percentage": 0.0,
            "last_updated": ""
        }
        # attach back
        student_record["subjects"] = subjects_dict
        attendance_records[student_roll] = student_record
        attendance_data["attendance_records"] = attendance_records
        save_attendance_master(attendance_data)
        print(f"⚠️ Subject '{subject_code}' was missing for {student_roll}. Created new entry '{new_key}'.")
        found_key = new_key

    # Now we have a valid found_key to operate on
    subject_data = subjects_dict.get(found_key)
    if not subject_data:
        print("Subject not found for this student after creation attempt.")
        return

    # Show current values
    print(f"\nCurrent attendance for {student_roll} - {subject_data.get('subject_name', found_key)}:")
    print(f"Total working days: {subject_data.get('total_working_days', 0)}")
    print(f"Total present days: {subject_data.get('total_present_days', 0)}")
    print(f"Attendance %: {subject_data.get('attendance_percentage', 0.0)}%")

    try:
        new_working_days = int(input("Enter new total working days: "))
        new_present_days = int(input("Enter new total present days: "))
    except ValueError:
        print("Invalid input! Please enter numbers.")
        return

    if new_present_days > new_working_days:
        print("Error: Present days cannot exceed working days.")
        return

    confirm = input(f"Update attendance for {student_roll}? (y/n): ").strip().lower()
    if confirm not in ["y", "yes"]:
        print("Update cancelled.")
        return

    # Update attendance
    subject_data["total_working_days"] = new_working_days
    subject_data["total_present_days"] = new_present_days

    if new_working_days > 0:
        subject_data["attendance_percentage"] = round(
            (new_present_days / new_working_days) * 100, 2
        )
    else:
        subject_data["attendance_percentage"] = 0.0

    subject_data["last_updated"] = datetime.now().strftime("%Y-%m-%d")

    # Persist changes
    attendance_records[student_roll] = student_record
    attendance_data["attendance_records"] = attendance_records
    save_attendance_master(attendance_data)

    print("\nAttendance updated successfully!")
    print(f"New attendance %: {subject_data['attendance_percentage']}%")


def get_student_attendance_summary(student_roll):
    """Get attendance summary for a student"""
    attendance_data = load_attendance_master()
    
    if student_roll in attendance_data.get("attendance_records", {}):
        student_data = attendance_data["attendance_records"][student_roll]
        print(f"\n--- Attendance Summary for {student_roll} ---")
        print(f"Section: {student_data['section']}")
        print("\nSubject-wise Attendance:")
        
        for subject_code, subject_data in student_data["subjects"].items():
            print(f"  {subject_data['subject_name']} ({subject_code}):")
            print(f"    Working Days: {subject_data['total_working_days']}")
            print(f"    Present Days: {subject_data['total_present_days']}")
            print(f"    Attendance: {subject_data['attendance_percentage']}%")
            print(f"    Last Updated: {subject_data['last_updated']}")
            print()
    else:
        print("No attendance data found for this student.")