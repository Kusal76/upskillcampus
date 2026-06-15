"""
StudentManager Class for the Student Management System.
Handles business logic, validations, CRUD operations, sorting, and JSON file handling.
"""

import os
import re
import json
from typing import List, Dict, Optional, Any
from student import Student

class SMSException(Exception):
    """Base exception class for Student Management System."""
    pass

class DuplicateIDError(SMSException):
    """Exception raised when a duplicate Student ID is detected."""
    pass

class StudentNotFoundError(SMSException):
    """Exception raised when a student record is not found."""
    pass

class ValidationError(SMSException):
    """Exception raised when input validation fails."""
    pass


class StudentManager:
    """
    Manages a collection of Student records. Handles CRUD, data validation,
    sorting, and data persistence in JSON.
    """

    def __init__(self, data_file_path: Optional[str] = None):
        """
        Initializes the StudentManager with a storage file path.

        Args:
            data_file_path (Optional[str]): Path to the JSON data file.
                                            Defaults to 'data/students.json' in the same folder.
        """
        if data_file_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.data_file_path = os.path.join(base_dir, "data", "students.json")
        else:
            self.data_file_path = os.path.abspath(data_file_path)

        # Dictionary to store Student objects in memory: {student_id: Student}
        self.students: Dict[str, Student] = {}
        
        # Load existing data on startup
        self.load_data()

    def load_data(self) -> None:
        """
        Loads student records from the JSON file into the memory cache.
        If the directory or file doesn't exist, it creates them.
        """
        if not os.path.exists(self.data_file_path):
            # Create subdirectories if they do not exist
            os.makedirs(os.path.dirname(self.data_file_path), exist_ok=True)
            self.students = {}
            self.save_data()
            return

        try:
            with open(self.data_file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, list):
                    self.students = {item["student_id"]: Student.from_dict(item) for item in data}
                elif isinstance(data, dict):
                    self.students = {k: Student.from_dict(v) for k, v in data.items()}
                else:
                    self.students = {}
        except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
            # Re-initialize to empty and back up corrupted files, or log
            print(f"[Warning] Failed to load database ({e}). Starting with a clean session.")
            self.students = {}

    def save_data(self) -> None:
        """
        Persists current in-memory student records to the JSON database.
        """
        try:
            os.makedirs(os.path.dirname(self.data_file_path), exist_ok=True)
            # Store as list of dicts to keep JSON readable
            data_to_save = [student.to_dict() for student in self.students.values()]
            with open(self.data_file_path, "w", encoding="utf-8") as file:
                json.dump(data_to_save, file, indent=4)
        except Exception as e:
            raise SMSException(f"Error saving data to file: {e}")

    # --- Validation Rules ---
    def validate_id_exists(self, student_id: str) -> None:
        """Checks if a student ID already exists."""
        if student_id in self.students:
            raise DuplicateIDError(f"Student ID '{student_id}' already exists.")

    def validate_age(self, age: int) -> None:
        """Checks if the age is greater than 0."""
        if not isinstance(age, int) or age <= 0:
            raise ValidationError("Age must be an integer greater than 0.")

    def validate_marks(self, marks: float) -> None:
        """Checks if marks are within the range 0 to 100 inclusive."""
        if not isinstance(marks, (int, float)) or not (0 <= marks <= 100):
            raise ValidationError("Marks must be a number between 0 and 100 inclusive.")

    def validate_email(self, email: str) -> None:
        """Validates the structure of the email address using regex."""
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, email):
            raise ValidationError(f"Email '{email}' is not a valid format.")

    # --- CRUD Operations ---
    def add_student(self, student_id: str, name: str, age: int, gender: str, course: str, marks: float, email: str) -> Student:
        """
        Validates details and adds a new Student.

        Args:
            student_id (str): Unique student ID.
            name (str): Full name.
            age (int): Age.
            gender (str): Gender.
            course (str): Course.
            marks (float): Marks.
            email (str): Email.

        Returns:
            Student: The created student record.
        """
        student_id_clean = str(student_id).strip()
        name_clean = str(name).strip()
        gender_clean = str(gender).strip()
        course_clean = str(course).strip()
        email_clean = str(email).strip()

        if not student_id_clean or not name_clean:
            raise ValidationError("Student ID and Name cannot be empty.")

        # Trigger validations
        self.validate_id_exists(student_id_clean)
        self.validate_age(age)
        self.validate_marks(marks)
        self.validate_email(email_clean)

        # Create and store
        student = Student(student_id_clean, name_clean, age, gender_clean, course_clean, marks, email_clean)
        self.students[student_id_clean] = student
        self.save_data()
        return student

    def view_students(self, sort_by: Optional[str] = None, reverse: bool = False) -> List[Student]:
        """
        Retrieves all students, optionally sorted by Name or Marks.

        Args:
            sort_by (Optional[str]): 'name' or 'marks'. Defaults to None.
            reverse (bool): Reverse the sorting order. Defaults to False.

        Returns:
            List[Student]: List of student instances.
        """
        student_list = list(self.students.values())
        if sort_by == "name":
            student_list.sort(key=lambda s: s.name.lower(), reverse=reverse)
        elif sort_by == "marks":
            student_list.sort(key=lambda s: s.marks, reverse=reverse)
        return student_list

    def search_student(self, student_id: str) -> Optional[Student]:
        """
        Searches for a student by ID.

        Args:
            student_id (str): ID of the student.

        Returns:
            Optional[Student]: The Student object if found, else None.
        """
        return self.students.get(str(student_id).strip())

    def update_student(self, student_id: str, **updates: Any) -> Student:
        """
        Updates fields of an existing student record.

        Args:
            student_id (str): ID of the student to update.
            **updates: Keyword arguments for updates (e.g. name, age, gender, course, marks, email).

        Returns:
            Student: The updated student object.
        """
        student_id_clean = str(student_id).strip()
        student = self.students.get(student_id_clean)
        if not student:
            raise StudentNotFoundError(f"Student with ID '{student_id}' does not exist.")

        # Validate updating fields
        if "age" in updates and updates["age"] is not None:
            self.validate_age(updates["age"])
            student.age = updates["age"]

        if "marks" in updates and updates["marks"] is not None:
            self.validate_marks(updates["marks"])
            student.marks = updates["marks"]

        if "email" in updates and updates["email"] is not None:
            email_clean = str(updates["email"]).strip()
            self.validate_email(email_clean)
            student.email = email_clean

        if "name" in updates and updates["name"] is not None:
            name_clean = str(updates["name"]).strip()
            if not name_clean:
                raise ValidationError("Name cannot be empty.")
            student.name = name_clean

        if "gender" in updates and updates["gender"] is not None:
            student.gender = str(updates["gender"]).strip()

        if "course" in updates and updates["course"] is not None:
            student.course = str(updates["course"]).strip()

        self.save_data()
        return student

    def delete_student(self, student_id: str) -> Student:
        """
        Deletes a student record by ID.

        Args:
            student_id (str): Student ID.

        Returns:
            Student: The deleted student record.
        """
        student_id_clean = str(student_id).strip()
        if student_id_clean not in self.students:
            raise StudentNotFoundError(f"Student with ID '{student_id}' does not exist.")
        
        deleted_student = self.students.pop(student_id_clean)
        self.save_data()
        return deleted_student
