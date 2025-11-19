import json
import os
from datetime import datetime

TOPICS_FILE = "topics.json"
TEACHER_SECTIONS_FILE = "teachersections.json"
STUDENT_FILE = "students.json"
SECTIONS_FILE = "sections.json"

def load_json(filename):
    if not os.path.exists(filename):
        return {}
    with open(filename, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def load_teacher_sections():
    data = load_json(TEACHER_SECTIONS_FILE)
    return data if isinstance(data, dict) else {}

def add_topic(teacher_name):
    teacher_sections = load_teacher_sections()
    teacher_name_lower = teacher_name.lower()

    assigned_sections = [
        sec for sec, tname in teacher_sections.items()
        if tname.lower() == teacher_name_lower
    ]

    if not assigned_sections:
        print("You are not assigned to any section. Contact admin.")
        return

    print(f"\nYou are assigned to section(s): {', '.join(assigned_sections)}")

    if len(assigned_sections) > 1:
        print("Select section to add topic:")
        for i, sec in enumerate(assigned_sections, 1):
            print(f"{i}. {sec}")
        try:
            choice = int(input("Enter choice: ").strip())
            section = assigned_sections[choice - 1]
        except (ValueError, IndexError):
            print("Invalid choice.")
            return
    else:
        section = assigned_sections[0]

    topic = input("Enter topic covered: ").strip()
    if not topic:
        print("Topic cannot be empty.")
        return

    date = datetime.now().strftime("%d/%m/%Y")
    topics_data = load_json(TOPICS_FILE)

    if section not in topics_data:
        topics_data[section] = []

    topics_data[section].append({
        "teacher": teacher_name,
        "topic": topic,
        "date": date
    })

    save_json(TOPICS_FILE, topics_data)
    print(f"Topic '{topic}' added successfully for section {section} on {date}.")

def view_topics_for_student(student_id):
    if not os.path.exists("sections.json"):
        print("sections.json file not found.")
        return
    if not os.path.exists("topics.json"):
        print("topics.json file not found.")
        return

    with open("sections.json", "r") as f:
        sections_data = json.load(f)

    student_section = sections_data.get(student_id)
    if not student_section:
        print("You are not assigned to any section.")
        return

    with open("topics.json", "r") as f:
        topics_data = json.load(f)

    section_topics = topics_data.get(student_section)
    if not section_topics:
        print(f"No topics found for your section ({student_section}).")
        return

    print(f"\nTopics covered in your section ({student_section}):\n")
    for idx, topic_entry in enumerate(section_topics, start=1):
        teacher = topic_entry.get("teacher", "Unknown")
        topic = topic_entry.get("topic", "No topic title")
        date = topic_entry.get("date", "Unknown date")
        print(f"{idx}. {teacher} — {topic} ({date})")
    print("\nEnd of list.\n")

if __name__ == "__main__":
    print("1. Add topic (Teacher)")
    print("2. View topics (Student)")
    ch = input("Enter choice: ").strip()
    if ch == "1":
        tname = input("Enter teacher name: ").strip()
        add_topic(tname)
    elif ch == "2":
        sid = input("Enter student roll number: ").strip()
        view_topics_for_student(sid)
