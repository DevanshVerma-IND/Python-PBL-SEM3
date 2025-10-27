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

def load_json_file(filename):
    """Load JSON data from file"""
    if not os.path.exists(filename):
        return {}
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except:
        return {}

def save_json_file(filename, data):
    """Save JSON data to file"""
    with open(filename, "w") as f:
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
            colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(subjects)))
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
        colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(all_subjects)))
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
    """Mark attendance for a student - only allowed for authorized teachers"""
    # Check if teacher is authorized for this student's section
    student_section = get_student_section(student_roll)
    if student_section == "Not assigned":
        print("Student not assigned to any section.")
        return False
    
    if not can_teacher_access_section(teachername, student_section):
        print(f"Unauthorized: You are not assigned to section {student_section}.")
        return False
    
    attendance_data = load_attendance_master()
    
    if student_roll not in attendance_data.get("attendance_records", {}):
        print("Student not found in attendance records.")
        return False
    
    if subject_code not in attendance_data["attendance_records"][student_roll]["subjects"]:
        print("Subject not found for this student.")
        return False
    
    subject_data = attendance_data["attendance_records"][student_roll]["subjects"][subject_code]
    
    # Get confirmation
    status = "present" if is_present else "absent"
    confirm = input(
        f"Mark {student_roll} as {status} for {subject_data['subject_name']}? (y/n): "
    ).strip().lower()
    
    if confirm not in ["y", "yes"]:
        print("Attendance marking cancelled.")
        return False
    
    # Update attendance
    subject_data["total_working_days"] += 1
    
    if is_present:
        subject_data["total_present_days"] += 1
        print(f"Marked {student_roll} present for {subject_data['subject_name']}")
    else:
        print(f"Marked {student_roll} absent for {subject_data['subject_name']}")
    
    # Calculate percentage
    if subject_data["total_working_days"] > 0:
        subject_data["attendance_percentage"] = round(
            (subject_data["total_present_days"] / subject_data["total_working_days"]) * 100, 2
        )
    
    subject_data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    
    save_attendance_master(attendance_data)
    print("Attendance updated successfully!")
    return True

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
    
    if student_roll not in attendance_data.get("attendance_records", {}):
        print("Student not found in attendance records.")
        return
    
    if subject_code not in attendance_data["attendance_records"][student_roll]["subjects"]:
        print("Subject not found for this student.")
        return
    
    subject_data = attendance_data["attendance_records"][student_roll]["subjects"][subject_code]
    
    print(f"\nCurrent attendance for {student_roll} - {subject_data['subject_name']}:")
    print(f"Total working days: {subject_data['total_working_days']}")
    print(f"Total present days: {subject_data['total_present_days']}")
    print(f"Attendance %: {subject_data['attendance_percentage']}%")
    
    try:
        new_working_days = int(input("Enter new total working days: "))
        new_present_days = int(input("Enter new total present days: "))
    except ValueError:
        print("Invalid input! Please enter numbers.")
        return
    
    if new_present_days > new_working_days:
        print("Error: Present days cannot exceed working days.")
        return
    
    confirm = input(
        f"Update attendance for {student_roll}? (y/n): "
    ).strip().lower()
    
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