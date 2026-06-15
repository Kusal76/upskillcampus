"""
Student Model Class for the Student Management System.
Defines the structure, validation constraints, and serialization logic for student records.
"""

class Student:
    """
    Represents a student in the Student Management System.
    """

    def __init__(self, student_id: str, name: str, age: int, gender: str, course: str, marks: float, email: str):
        """
        Initializes a Student instance.

        Args:
            student_id (str): Unique identifier for the student.
            name (str): Full name of the student.
            age (int): Age of the student (must be > 0).
            gender (str): Gender of the student.
            course (str): Enrolled course name.
            marks (float): Marks scored by the student (0 to 100).
            email (str): Standard validated email address.
        """
        self.student_id = student_id
        self.name = name
        self.age = age
        self.gender = gender
        self.course = course
        self.marks = marks
        self.email = email

    def display(self) -> None:
        """
        Displays student details in a clean, tabular format.
        """
        print(f"| {self.student_id:<10} | {self.name:<20} | {self.age:<4} | {self.gender:<8} | {self.course:<15} | {self.marks:<6.2f} | {self.email:<28} |")

    def to_dict(self) -> dict:
        """
        Converts the student instance into a dictionary for JSON serialization.

        Returns:
            dict: Dictionary representation of the student attributes.
        """
        return {
            "student_id": self.student_id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "course": self.course,
            "marks": self.marks,
            "email": self.email
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Student":
        """
        Creates a Student instance from a dictionary.

        Args:
            data (dict): Dictionary containing student attribute key-value pairs.

        Returns:
            Student: Deserialized Student instance.
        """
        return cls(
            student_id=data["student_id"],
            name=data["name"],
            age=data["age"],
            gender=data["gender"],
            course=data["course"],
            marks=data["marks"],
            email=data["email"]
        )
