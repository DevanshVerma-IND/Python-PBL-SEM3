import json
import matplotlib.pyplot as plt
import numpy as np
import os

def load_attendance_data():
    """Load attendance data from JSON file"""
    if not os.path.exists("attendance.json"):
        return {"subjects": []}
    try:
        with open("attendance.json", "r") as f:
            return json.load(f)
    except:
        return {"subjects": []}

def save_attendance_data(data):
    """Save attendance data to JSON file"""
    with open("attendance.json", "w") as f:
        json.dump(data, f, indent=2)

def view_attendance():
    """View attendance chart for all subjects"""
    attendance_data = load_attendance_data()
    
    subjects = [s["subject_name"] for s in attendance_data.get("subjects", [])]
    attendance = [s.get("attendance_percentage", 0) for s in attendance_data.get("subjects", [])]

    if not subjects:
        print("No attendance data found.")
        return

    colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(subjects)))
    plt.figure(figsize=(12, 6))
    bars = plt.bar(subjects, attendance, color=colors, edgecolor="gray", linewidth=0.8)
    
    plt.title("Attendance Percentage by Subject", fontsize=16, fontweight="bold", pad=20)
    plt.xlabel("Subjects", fontsize=12, labelpad=10)
    plt.ylabel("Attendance (%)", fontsize=12, labelpad=10)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    
    for bar, value in zip(bars, attendance):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, 
                f"{value:.1f}%", ha="center", fontsize=9, fontweight="bold")
    
    plt.tight_layout()
    plt.show()

def mark_attendance(name, section, subject_code):
    """Mark attendance for a student"""
    # Load student data
    try:
        with open("student.json", "r") as f:
            student_data = json.load(f)
    except:
        print("Error loading student data.")
        return
    
    if student_data["student"]["name"] != name or student_data["student"]["section"] != section:
        print("Student not found or section mismatch!")
        return
    
    attendance_data = load_attendance_data()
    found = False
    
    for subject in attendance_data["subjects"]:
        if subject["subject_code"] == subject_code:
            found = True
            status = input(f"Was {name} present or absent for {subject['subject_name']}? ").strip().lower()
            if status not in ["present", "absent"]:
                print("Invalid input! Please enter 'present' or 'absent'.")
                return
            
            confirm = input(
                f"Are you sure you want to mark {name} as {status} for {subject['subject_name']} ({subject_code})? (y/n): "
            ).strip().lower()
            
            if confirm not in ["y", "yes"]:
                print("Action cancelled by user. No changes made.")
                return
            
            subject["total_sessions"] += 1
            if status == "present":
                subject["attended_sessions"] += 1
                print(f"Marked {name} present for {subject['subject_name']}")
            else:
                print(f"Marked {name} absent for {subject['subject_name']}")
            
            subject["attendance_percentage"] = round(
                (subject["attended_sessions"] / subject["total_sessions"]) * 100, 2
            )
            break
    
    if not found:
        print("Subject code not found!")
        return
    
    save_attendance_data(attendance_data)
    print("Attendance updated successfully!")

def update_attendance(name, section, subject_code):
    """Update existing attendance record"""
    try:
        with open("student.json", "r") as f:
            student_data = json.load(f)
    except:
        print("Error loading student data.")
        return
        
    if student_data["student"]["name"] != name or student_data["student"]["section"] != section:
        print("Student not found or section mismatch!")
        return
    
    attendance_data = load_attendance_data()
    found = False
    
    for subject in attendance_data["subjects"]:
        if subject["subject_code"] == subject_code:
            found = True
            print(f"\nCurrent attendance details for {subject['subject_name']} ({subject_code}):")
            print(f"Total sessions: {subject['total_sessions']}")
            print(f"Attended sessions: {subject['attended_sessions']}")
            print(f"Attendance %: {subject['attendance_percentage']}%")
            
            old_status = input("\nWhat was the previous marking? (present/absent): ").strip().lower()
            new_status = input("What should it be changed to? (present/absent): ").strip().lower()
            
            if old_status not in ["present", "absent"] or new_status not in ["present", "absent"]:
                print("Invalid input! Please enter 'present' or 'absent'.")
                return
            
            if old_status == new_status:
                print("No change needed — both statuses are the same.")
                return
            
            confirm = input(
                f"\nConfirm change: {name}'s status in {subject['subject_name']} from '{old_status}' to '{new_status}'? (y/n): "
            ).strip().lower()
            
            if confirm not in ["y", "yes"]:
                print("Update cancelled by user.")
                return
            
            if old_status == "present" and new_status == "absent":
                subject["attended_sessions"] -= 1
                print("Changed from PRESENT → ABSENT")
            elif old_status == "absent" and new_status == "present":
                subject["attended_sessions"] += 1
                print("Changed from ABSENT → PRESENT")
            
            subject["attendance_percentage"] = round(
                (subject["attended_sessions"] / subject["total_sessions"]) * 100, 2
            )
            break
    
    if not found:
        print("Subject code not found!")
        return
    
    save_attendance_data(attendance_data)
    print("\nAttendance updated successfully!")
    print(f"New attendance % for {subject['subject_name']}: {subject['attendance_percentage']}%")