"""
Flask Web Application Server for the Student Management System.
Exposes REST API endpoints for student records CRUD operations and serves the UI.
"""

import os
import re
from flask import Flask, jsonify, request, render_template
from manager import StudentManager, ValidationError, DuplicateIDError, StudentNotFoundError, SMSException

def strip_tags(value: str) -> str:
    """Removes all HTML/XML tags from a string to prevent stored XSS."""
    return re.sub(r'<[^>]+>', '', str(value)).strip()

# Initialize Flask app serving from templates/ and static/
app = Flask(__name__, static_url_path="/static", static_folder="static", template_folder="templates")

# Initialize in-memory database controller
manager = StudentManager()

@app.after_request
def add_security_headers(response):
    """Adds basic security headers to every response."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

@app.route("/")
def index():
    """Serves the central HTML dashboard view."""
    return render_template("index.html")

@app.route("/api/students", methods=["GET"])
def get_students():
    """Retrieves all students, supporting optional sort filters."""
    sort_by = request.args.get("sort_by", None)
    reverse_param = request.args.get("reverse", "false").lower()
    reverse = (reverse_param == "true")
    
    # Sort descending by default for marks
    if sort_by == "marks" and "reverse" not in request.args:
        reverse = True
        
    try:
        students = manager.view_students(sort_by=sort_by, reverse=reverse)
        return jsonify([s.to_dict() for s in students])
    except Exception as e:
        return jsonify({"error": f"Internal database error: {e}"}), 500

@app.route("/api/students/<student_id>", methods=["GET"])
def get_student(student_id):
    """Retrieves record of a specific student by ID."""
    student = manager.search_student(student_id)
    if student:
        return jsonify(student.to_dict())
    return jsonify({"error": f"Student with ID '{student_id}' not found."}), 404

@app.route("/api/students", methods=["POST"])
def add_student():
    """Validates inputs and adds a new student to database."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must contain valid JSON."}), 400

    try:
        student_id = strip_tags(data.get("student_id", ""))
        name = strip_tags(data.get("name", ""))
        gender = strip_tags(data.get("gender", ""))
        course = strip_tags(data.get("course", ""))
        email = strip_tags(data.get("email", ""))

        # Input Parsing validations
        age_raw = data.get("age")
        if age_raw is None or age_raw == "":
            raise ValidationError("Age field is required.")
        try:
            age = int(age_raw)
        except ValueError:
            raise ValidationError("Age must be an integer.")

        marks_raw = data.get("marks")
        if marks_raw is None or marks_raw == "":
            raise ValidationError("Marks field is required.")
        try:
            marks = float(marks_raw)
        except ValueError:
            raise ValidationError("Marks must be a valid numeric rating.")

        # Business validations and insert
        student = manager.add_student(
            student_id=student_id,
            name=name,
            age=age,
            gender=gender,
            course=course,
            marks=marks,
            email=email
        )
        return jsonify({
            "message": f"Student '{student.name}' created successfully.",
            "student": student.to_dict()
        }), 201

    except (ValidationError, DuplicateIDError) as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

@app.route("/api/students/<student_id>", methods=["PUT"])
def update_student(student_id):
    """Updates fields of an existing student record."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No update fields provided."}), 400

    updates = {}
    try:
        if "name" in data:
            updates["name"] = strip_tags(data["name"])
        if "gender" in data:
            updates["gender"] = strip_tags(data["gender"])
        if "course" in data:
            updates["course"] = strip_tags(data["course"])
        if "email" in data:
            updates["email"] = strip_tags(data["email"])

        if "age" in data and data["age"] is not None and data["age"] != "":
            try:
                updates["age"] = int(data["age"])
            except ValueError:
                raise ValidationError("Age must be a valid integer.")

        if "marks" in data and data["marks"] is not None and data["marks"] != "":
            try:
                updates["marks"] = float(data["marks"])
            except ValueError:
                raise ValidationError("Marks must be a valid numeric rating.")

        updated_student = manager.update_student(student_id, **updates)
        return jsonify({
            "message": "Student profile updated successfully.",
            "student": updated_student.to_dict()
        })

    except StudentNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

@app.route("/api/students/<student_id>", methods=["DELETE"])
def delete_student(student_id):
    """Deletes a student record from database."""
    try:
        deleted = manager.delete_student(student_id)
        return jsonify({"message": f"Student '{deleted.name}' deleted successfully."})
    except StudentNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

if __name__ == "__main__":
    print("Starting Student Management System Web Server...")
    app.run(host="127.0.0.1", port=5000, debug=True)
