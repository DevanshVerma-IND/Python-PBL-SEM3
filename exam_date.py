import json
from datetime import datetime

with open("exam_date.json",
          "r") as file:
    data = json.load(file)
print(data)

def view_exam_deadline():
    user_input = input("Enter subject code or 'view all': ").strip().upper()
    now = datetime.now()

    def time_left(exam_date_str):
        exam_dt = datetime.strptime(exam_date_str, "%d/%m/%Y")
        delta = exam_dt - now
        if delta.total_seconds() < 0:
            return "Exam already passed!"
        days = delta.days
        hours, rem = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(rem, 60)
        return f"{days}d {hours}h {minutes}m {seconds}s left"

    if user_input == "VIEW ALL":
        print("\nExam Deadlines for All Subjects:\n")
        for item in data['exam_schedule']:
            countdown = time_left(item['exam_date'])
            print(f"{item['subject_code']} - {item['subject_name']} : {item['exam_date']} ({countdown})")
    else:
        found = False
        for item in data['exam_schedule']:
            if item['subject_code'].upper() == user_input:
                countdown = time_left(item['exam_date'])
                print(
                    f"\nExam Date for {item['subject_code']} - {item['subject_name']} : {item['exam_date']} ({countdown})")
                found = True
                break
        if not found:
            print(f"\nSubject code '{user_input}' not found.")


view_exam_deadline()

