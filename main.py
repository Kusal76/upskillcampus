"""
Main Application Entry Point for the Student Management System.
Implements the CLI menu, handles user input validation loops, and routes commands.
"""

import sys
from manager import StudentManager, ValidationError, DuplicateIDError, StudentNotFoundError

def print_banner() -> None:
    """Prints a premium visual banner for the application."""
    print("\n" + "=" * 55)
    print("        S T U D E N T   M A N A G E M E N T   S Y S T E M")
    print("=" * 55)

def print_table_header() -> None:
    """Prints the table header for displaying student list."""
    border = "+------------+----------------------+------+----------+-----------------+--------+------------------------------+"
    print(border)
    print(f"| {'ID':<10} | {'Name':<20} | {'Age':<4} | {'Gender':<8} | {'Course':<15} | {'Marks':<6} | {'Email':<28} |")
    print(border)

def print_table_footer() -> None:
    """Prints the table footer border."""
    border = "+------------+----------------------+------+----------+-----------------+--------+------------------------------+"
    print(border)

def get_non_empty_input(prompt_text: str) -> str:
    """Prompts for input and requires it to be non-empty."""
    while True:
        val = input(prompt_text).strip()
        if val:
            return val
        print("[Error] Input cannot be empty. Please try again.")

def handle_add_student(manager: StudentManager) -> None:
    """Handles the flow for adding a new student record."""
    print("\n--- Add New Student ---")
    
    # 1. Student ID (must be unique)
    while True:
        student_id = get_non_empty_input("Enter Student ID: ")
        if manager.search_student(student_id):
            print(f"[Error] Student ID '{student_id}' already exists. Please enter a unique ID.")
            continue
        break

    # 2. Name
    name = get_non_empty_input("Enter Full Name: ")

    # 3. Age (> 0)
    while True:
        try:
            age_str = get_non_empty_input("Enter Age: ")
            age = int(age_str)
            manager.validate_age(age)
            break
        except ValueError:
            print("[Error] Age must be a valid integer.")
        except ValidationError as e:
            print(f"[Error] {e}")

    # 4. Gender
    gender = get_non_empty_input("Enter Gender: ")

    # 5. Course
    course = get_non_empty_input("Enter Course: ")

    # 6. Marks (0-100)
    while True:
        try:
            marks_str = get_non_empty_input("Enter Marks (0-100): ")
            marks = float(marks_str)
            manager.validate_marks(marks)
            break
        except ValueError:
            print("[Error] Marks must be a valid number.")
        except ValidationError as e:
            print(f"[Error] {e}")

    # 7. Email (valid format)
    while True:
        try:
            email = get_non_empty_input("Enter Email: ")
            manager.validate_email(email)
            break
        except ValidationError as e:
            print(f"[Error] {e}")

    # Add student
    try:
        student = manager.add_student(
            student_id=student_id,
            name=name,
            age=age,
            gender=gender,
            course=course,
            marks=marks,
            email=email
        )
        print(f"\n[Success] Student '{student.name}' added successfully and saved to database.")
    except Exception as e:
        print(f"[Error] Failed to add student: {e}")

def handle_view_students(manager: StudentManager, sort_by: str = None) -> None:
    """Displays all students in a table format, optionally sorted."""
    students = manager.view_students(sort_by=sort_by)
    if not students:
        print("\n[Info] No student records found. Add students first.")
        return

    title = " All Students "
    if sort_by == "name":
        title = " Students Sorted by Name "
    elif sort_by == "marks":
        title = " Students Sorted by Marks (High to Low) "
        # For marks sorting, standard is high to low for student reports, let's pass reverse=True
        students = manager.view_students(sort_by="marks", reverse=True)

    print(f"\n--- {title} ({len(students)} records) ---")
    print_table_header()
    for student in students:
        student.display()
    print_table_footer()

def handle_search_student(manager: StudentManager) -> None:
    """Searches for a student by ID and prints the matching record."""
    print("\n--- Search Student ---")
    student_id = get_non_empty_input("Enter Student ID to Search: ")
    student = manager.search_student(student_id)
    if student:
        print("\n[Success] Student found:")
        print_table_header()
        student.display()
        print_table_footer()
    else:
        print(f"[Error] Student with ID '{student_id}' not found.")

def handle_update_student(manager: StudentManager) -> None:
    """Guides the user through updating specific fields of an existing student."""
    print("\n--- Update Student Details ---")
    student_id = get_non_empty_input("Enter Student ID to Update: ")
    student = manager.search_student(student_id)
    if not student:
        print(f"[Error] Student with ID '{student_id}' does not exist.")
        return

    print(f"\nFound Record: ID={student.student_id}, Name={student.name}")
    print("Press Enter without typing to skip updating a field.\n")

    # Name
    name_input = input(f"New Name [{student.name}]: ").strip()
    name = name_input if name_input else None

    # Age
    while True:
        age_input = input(f"New Age [{student.age}]: ").strip()
        if not age_input:
            age = None
            break
        try:
            age = int(age_input)
            manager.validate_age(age)
            break
        except ValueError:
            print("[Error] Age must be a valid integer.")
        except ValidationError as e:
            print(f"[Error] {e}")

    # Gender
    gender_input = input(f"New Gender [{student.gender}]: ").strip()
    gender = gender_input if gender_input else None

    # Course
    course_input = input(f"New Course [{student.course}]: ").strip()
    course = course_input if course_input else None

    # Marks
    while True:
        marks_input = input(f"New Marks [{student.marks}]: ").strip()
        if not marks_input:
            marks = None
            break
        try:
            marks = float(marks_input)
            manager.validate_marks(marks)
            break
        except ValueError:
            print("[Error] Marks must be a valid number.")
        except ValidationError as e:
            print(f"[Error] {e}")

    # Email
    while True:
        email_input = input(f"New Email [{student.email}]: ").strip()
        if not email_input:
            email = None
            break
        try:
            manager.validate_email(email_input)
            email = email_input
            break
        except ValidationError as e:
            print(f"[Error] {e}")

    # Apply updates
    try:
        updated = manager.update_student(
            student_id=student_id,
            name=name,
            age=age,
            gender=gender,
            course=course,
            marks=marks,
            email=email
        )
        print(f"\n[Success] Student ID '{student_id}' updated successfully.")
        print_table_header()
        updated.display()
        print_table_footer()
    except Exception as e:
        print(f"[Error] Failed to update student: {e}")

def handle_delete_student(manager: StudentManager) -> None:
    """Handles deletion of a student record with confirmation."""
    print("\n--- Delete Student Record ---")
    student_id = get_non_empty_input("Enter Student ID to Delete: ")
    student = manager.search_student(student_id)
    if not student:
        print(f"[Error] Student with ID '{student_id}' does not exist.")
        return

    print("\nStudent Record Selected for Deletion:")
    print_table_header()
    student.display()
    print_table_footer()

    confirm = input("Are you sure you want to permanently delete this student? (y/n): ").strip().lower()
    if confirm in ("y", "yes"):
        try:
            manager.delete_student(student_id)
            print(f"[Success] Student record with ID '{student_id}' deleted.")
        except Exception as e:
            print(f"[Error] Failed to delete student: {e}")
    else:
        print("[Info] Deletion cancelled.")

def main() -> None:
    """Application main loop."""
    # Initialize Manager
    manager = StudentManager()

    while True:
        print_banner()
        print("1. Add Student")
        print("2. View Students")
        print("3. Search Student")
        print("4. Update Student")
        print("5. Delete Student")
        print("6. Sort by Name")
        print("7. Sort by Marks")
        print("8. Exit")
        print("=" * 55)

        choice = input("Enter your choice (1-8): ").strip()

        if choice == "1":
            handle_add_student(manager)
        elif choice == "2":
            handle_view_students(manager)
        elif choice == "3":
            handle_search_student(manager)
        elif choice == "4":
            handle_update_student(manager)
        elif choice == "5":
            handle_delete_student(manager)
        elif choice == "6":
            handle_view_students(manager, sort_by="name")
        elif choice == "7":
            handle_view_students(manager, sort_by="marks")
        elif choice == "8":
            print("\nThank you for using the Student Management System. Goodbye!\n")
            sys.exit(0)
        else:
            print("[Error] Invalid choice! Please enter a number from 1 to 8.")
            
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted. Exiting gracefully. Goodbye!")
        sys.exit(0)
