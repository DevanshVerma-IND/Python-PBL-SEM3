import exam_date
import attendance
import subject
import section

def viewAttendance():
    attendance.view_attendance()

def markAttendance(name, sec, subjectcode):
    attendance.mark_attendance(name, sec, subjectcode)

def updateAttendance(name, sec, subjectcode):
    attendance.update_attendance(name, sec, subjectcode)

def viewStudentInfo():
    studentname = input("Enter student username: ").strip()
    roll = subject.getRollNumber(studentname, "student")
    secmap = section.loadJson(section.sectionsFile, {})
    sec = secmap.get(roll, "Not assigned")
    print(f"\n--- Info for {studentname} ---")
    print(f"University Roll Number: {roll}")
    print(f"Section: {sec}")
    if sec != "Not assigned":
        exam_date.viewSectionExamDates(sec)

def studentDashboard(studentname):
    print(f"\n--- Dashboard for {studentname} ---")
    roll = subject.getRollNumber(studentname, "student")
    print(f"University Roll Number: {roll}")
    secmap = section.loadJson(section.sectionsFile, {})
    sec = secmap.get(roll, "Not assigned")
    print(f"Section: {sec}")
    if sec != "Not assigned":
        exam_date.viewSectionExamDates(sec)

def adminMenu():
    while True:
        print("\n--- Admin Menu ---")
        print("1. Add subject")
        print("2. List subjects")
        print("3. Create section")
        print("4. List sections")
        print("5. Assign section to student (choose from list)")
        print("6. Assign sections to teacher")
        print("7. Set/Update exam dates")
        print("8. View all exam dates")
        print("9. View section assignments")
        print("10. View student info")
        print("11. View any student's dashboard")
        print("12. Back")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            subject.addSubject()
        elif choice == "2":
            subject.listSubjects()
        elif choice == "3":
            section.createSection()
        elif choice == "4":
            section.listSections()
        elif choice == "5":
            section.assignSectionFromList()
        elif choice == "6":
            section.assignSectionToTeacher()
        elif choice == "7":
            exam_date.setExamDatesAdmin()
        elif choice == "8":
            exam_date.viewAllExamDates()
        elif choice == "9":
            section.viewSectionAssignments()
        elif choice == "10":
            viewStudentInfo()
        elif choice == "11":
            name = input("Enter student username: ").strip()
            studentDashboard(name)
        elif choice == "12":
            break
        else:
            print("Invalid choice.")

def studentMenu(studentname):
    while True:
        print("\n--- Student Menu ---")
        print("1. View dashboard")
        print("2. View my exam schedule")
        print("3. View attendance")
        print("4. Logout")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            studentDashboard(studentname)
        elif choice == "2":
            roll = subject.getRollNumber(studentname, "student")
            secmap = section.loadJson(section.sectionsFile, {})
            sec = secmap.get(roll, "Not assigned")
            if sec == "Not assigned":
                print("Section not assigned.")
            else:
                exam_date.viewStudentExamSchedule(studentname)
        elif choice == "3":
            viewAttendance()
        elif choice == "4":
            break
        else:
            print("Invalid choice.")

def teacherMenu(teachername):
    while True:
        print("\n--- Teacher Menu ---")
        print("1. View my sections")
        print("2. Mark attendance")
        print("3. Update attendance")
        print("4. View attendance chart")
        print("5. Exit")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            section.viewMySections(teachername)
        elif choice == "2":
            name = input("Enter student name: ").strip()
            sec = input("Enter section: ").strip().upper()
            code = input("Enter subject code: ").strip().upper()
            markAttendance(name, sec, code)
        elif choice == "3":
            name = input("Enter student name: ").strip()
            sec = input("Enter section: ").strip().upper()
            code = input("Enter subject code: ").strip().upper()
            updateAttendance(name, sec, code)
        elif choice == "4":
            viewAttendance()
        elif choice == "5":
            break
        else:
            print("Invalid choice.")

def openMenu(role, username):
    r = role.strip().lower()
    if r == "admin":
        adminMenu()
    elif r == "teacher":
        teacherMenu(username)
    elif r == "student":
        studentMenu(username)
    else:
        print("Unknown role.")