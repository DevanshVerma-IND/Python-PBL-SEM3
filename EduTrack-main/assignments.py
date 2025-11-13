import os
import shutil
import fitz  # PyMuPDF
import json

SECTIONS_FILE = "sections.json"       # student_id → section
TEACHER_SECTIONS_FILE = "teachersections.json"  # teacher_name → [sections]
ASSIGNMENT_FOLDER = "assignments"     # root folder


def submit_assignment(student_id, source_path):
    """
    Student submits an assignment PDF.
    The file is saved under assignments/<section>/<student_id>.pdf
    """
    # Load student section
    if not os.path.exists(SECTIONS_FILE):
        print("sections.json not found.")
        return

    with open(SECTIONS_FILE, "r") as f:
        sections = json.load(f)

    student_section = sections.get(student_id)
    if not student_section:
        print("Section not found for this student.")
        return

    # Check if file exists
    if not os.path.exists(source_path):
        print(f"File '{source_path}' not found!")
        return

    # Check PDF
    if not source_path.lower().endswith(".pdf"):
        print("Only PDF files are allowed!")
        return

    # Prepare folder
    dest_folder = os.path.join(ASSIGNMENT_FOLDER, student_section)
    os.makedirs(dest_folder, exist_ok=True)

    # Destination path
    dest_path = os.path.join(dest_folder, f"{student_id}.pdf")

    # Copy file
    shutil.copy2(source_path, dest_path)
    print(f"Assignment submitted successfully!")
    print(f"  Saved as: {dest_path}")


def view_assignments(teacher_name):
    """
    Teacher can view all student PDFs in their assigned sections.
    """
    # Load teacher sections
    if not os.path.exists(TEACHER_SECTIONS_FILE):
        print("teachersections.json not found.")
        return

    with open(TEACHER_SECTIONS_FILE, "r") as f:
        teacher_data = json.load(f)

    teacher_sections = teacher_data.get(teacher_name)
    if not teacher_sections:
        print("No sections assigned to this teacher.")
        return

    # Show PDFs from each section
    print(f"\nAssignments for {teacher_name}:")
    found = False
    for section in teacher_sections:
        section_path = os.path.join(ASSIGNMENT_FOLDER, section)
        if not os.path.exists(section_path):
            continue

        files = [f for f in os.listdir(section_path) if f.endswith(".pdf")]
        if files:
            print(f"\nSection: {section}")
            for f in files:
                print(f"   - {f}")
            found = True

    if not found:
        print("No assignment PDFs found yet.")


def view_pdf_content(pdf_path, page_number=None):
    """
    View PDF text content in terminal.
    """
    try:
        if not os.path.exists(pdf_path):
            print("File not found.")
            return

        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        print(f"\nViewing '{os.path.basename(pdf_path)}' ({total_pages} pages)\n")

        if page_number:
            if 1 <= page_number <= total_pages:
                text = doc[page_number - 1].get_text() # type: ignore
                print(text if text.strip() else "[No text content]")
            else:
                print("Invalid page number.")
        else:
            for i in range(total_pages):
                print(f"\n--- Page {i + 1} ---\n")
                print(doc[i].get_text() or "[No text content]") # type: ignore

        doc.close()
    except Exception as e:
        print(f"Error reading PDF: {e}")


if __name__ == "__main__":
    print("1. Submit assignment (Student)")
    print("2. View assignments (Teacher)")
    print("3. View PDF content")
    ch = input("Enter choice: ").strip()

    if ch == "1":
        sid = input("Enter your Student ID: ").strip()
        path = input("Enter path to your PDF file: ").strip()
        submit_assignment(sid, path)

    elif ch == "2":
        tname = input("Enter your Teacher Name: ").strip()
        view_assignments(tname)

    elif ch == "3":
        pdfp = input("Enter path to PDF: ").strip()
        pg = input("Enter page number (press Enter for all): ").strip()
        view_pdf_content(pdfp, int(pg) if pg else None)
