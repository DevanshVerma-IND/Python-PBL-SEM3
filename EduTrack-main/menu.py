import exam_date
import attendance
import subject
import section
import topics
import assignments  # ← add this at top with other imports


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
        print("3. View my attendance")
        print("4. View attendance summary")
        print("5. View topics covered in my section")
        print("6. Submit assignment PDF")
        print("7. Logout")
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
            roll = subject.getRollNumber(studentname, "student")
            attendance.view_attendance(student_roll=roll)

        elif choice == "4":
            roll = subject.getRollNumber(studentname, "student")
            attendance.get_student_attendance_summary(roll)

        elif choice == "5":
            roll = subject.getRollNumber(studentname, "student")
            topics.view_topics_for_student(roll)

        elif choice == "6":
            roll = subject.getRollNumber(studentname, "student")
            pdf_path = input("Enter path to your assignment PDF: ").strip()
            assignments.submit_assignment(roll, pdf_path) # type: ignore

        elif choice == "7":
            break

        else:
            print("Invalid choice.")


def teacherMenu(teachername):
    while True:
        print("\n--- Teacher Menu ---")
        print("1. View my sections")
        print("2. Mark present")
        print("3. Update attendance/ mark absent")
        print("4. View attendance chart")
        print("5. Add topic covered")
        print("6. View topics covered")
        print("7. View submitted assignments")
        print("8. Exit")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            section.viewMySections(teachername)

        elif choice == "2":
            roll = input("Enter student roll number: ").strip()
            code = input("Enter subject code: ").strip().upper()
            attendance.mark_attendance(teachername, roll, code)

        elif choice == "3":
            roll = input("Enter student roll number: ").strip()
            code = input("Enter subject code: ").strip().upper()
            attendance.update_attendance(teachername, roll, code)

        elif choice == "4":
            attendance.view_attendance(teachername=teachername)

        elif choice == "5":
            topics.add_topic(teachername)

        elif choice == "6":
            # teacher can see topics of their assigned section(s)
            teacher_sections = topics.load_teacher_sections()
            teacher_name_lower = teachername.lower()

            assigned_sections = []
            for tname, sections in teacher_sections.items():
                if tname.lower() == teacher_name_lower:
                    assigned_sections.extend(sections)

            if not assigned_sections:
                print("No sections assigned to you.")
                continue

            topics_data = topics.load_json(topics.TOPICS_FILE)
            found_any = False
            for sec in assigned_sections:
                if sec in topics_data and topics_data[sec]:
                    print(f"\nTopics covered for section {sec}:")
                    for i, t in enumerate(topics_data[sec], 1):
                        print(f"{i}. {t['topic']} (by {t['teacher']} on {t['date']})")
                    found_any = True

            if not found_any:
                print("No topics recorded yet for your sections.")

        elif choice == "7":
            assignments.view_assignments(teachername) # type: ignore

        elif choice == "8":
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