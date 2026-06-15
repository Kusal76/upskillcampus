"""
Verification script to programmatically test StudentManager functions,
validations, and JSON persistence. Run this inside the student_management_system directory.
"""

import os
import sys

# Ensure the script's folder is in the Python search path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from student import Student
from manager import StudentManager, ValidationError, DuplicateIDError, StudentNotFoundError

def run_tests():
    # Setup test file path
    test_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "test_students.json")
    if os.path.exists(test_db):
        os.remove(test_db)
        
    print(f"Initializing StudentManager with test DB: {test_db}")
    mgr = StudentManager(data_file_path=test_db)
    
    # 1. Test addition of valid students
    print("\n--- Test 1: Adding valid students ---")
    s1 = mgr.add_student("101", "John Doe", 20, "Male", "Computer Science", 85.5, "john@example.com")
    s2 = mgr.add_student("102", "Alice Smith", 22, "Female", "Mathematics", 95.0, "alice@example.com")
    s3 = mgr.add_student("103", "Bob Johnson", 19, "Male", "Physics", 72.3, "bob@example.com")
    
    print(f"Added: {s1.name}, {s2.name}, {s3.name}")
    assert len(mgr.students) == 3, "Failed to add all 3 students"
    
    # 2. Test duplicate ID prevention
    print("\n--- Test 2: Validation of duplicate IDs ---")
    try:
        mgr.add_student("101", "Duplicate John", 21, "Male", "Chemistry", 80.0, "dup@example.com")
        assert False, "Duplicate ID was not caught"
    except DuplicateIDError as e:
        print(f"[Expected Exception] Duplicate ID caught: {e}")

    # 3. Test invalid age validation
    print("\n--- Test 3: Validation of invalid age ---")
    try:
        mgr.add_student("104", "Charlie", -1, "Male", "Biology", 80.0, "charlie@example.com")
        assert False, "Negative age was not caught"
    except ValidationError as e:
        print(f"[Expected Exception] Invalid age caught: {e}")

    # 4. Test invalid marks validation
    print("\n--- Test 4: Validation of invalid marks ---")
    try:
        mgr.add_student("104", "Charlie", 20, "Male", "Biology", 150.0, "charlie@example.com")
        assert False, "Out of range marks (>100) not caught"
    except ValidationError as e:
        print(f"[Expected Exception] Invalid marks caught: {e}")

    # 5. Test invalid email validation
    print("\n--- Test 5: Validation of invalid email ---")
    try:
        mgr.add_student("104", "Charlie", 20, "Male", "Biology", 75.0, "charlie_at_domain.com")
        assert False, "Invalid email format not caught"
    except ValidationError as e:
        print(f"[Expected Exception] Invalid email caught: {e}")

    # 6. Test search
    print("\n--- Test 6: Searching records ---")
    found = mgr.search_student("102")
    assert found is not None and found.name == "Alice Smith", "Failed to search existing student"
    print(f"Found student '102': {found.name}")
    
    not_found = mgr.search_student("999")
    assert not_found is None, "Search returned result for non-existent student"
    print("Non-existent student returned None as expected.")

    # 7. Test sorting
    print("\n--- Test 7: Sorting records ---")
    sorted_names = [s.name for s in mgr.view_students(sort_by="name")]
    print(f"Sorted by name: {sorted_names}")
    assert sorted_names == ["Alice Smith", "Bob Johnson", "John Doe"], "Sort by name failed"

    sorted_marks_desc = [s.marks for s in mgr.view_students(sort_by="marks", reverse=True)]
    print(f"Sorted by marks (desc): {sorted_marks_desc}")
    assert sorted_marks_desc == [95.0, 85.5, 72.3], "Sort by marks desc failed"

    # 8. Test update
    print("\n--- Test 8: Updating records ---")
    updated_student = mgr.update_student("103", name="Robert Johnson", marks=78.5)
    assert updated_student.name == "Robert Johnson" and updated_student.marks == 78.5, "Update failed"
    print(f"Updated Student ID 103 name to '{updated_student.name}' and marks to {updated_student.marks}")

    # Test file reloading to verify persistence
    print("\n--- Test 9: Data persistence load/save ---")
    mgr2 = StudentManager(data_file_path=test_db)
    assert len(mgr2.students) == 3, "Persisted database failed to load correct number of records"
    assert mgr2.students["103"].name == "Robert Johnson", "Updates were not persisted to JSON file"
    print("Database verified load and save: Updates correctly loaded in a separate manager instance.")

    # 9. Test delete
    print("\n--- Test 10: Deleting records ---")
    deleted = mgr.delete_student("101")
    assert deleted.student_id == "101", "Delete failed"
    assert len(mgr.students) == 2, "Student not removed from manager memory"
    assert "101" not in mgr.students, "Student ID still present in manager memory"
    
    # Reload and check
    mgr3 = StudentManager(data_file_path=test_db)
    assert len(mgr3.students) == 2, "Deletion was not persisted"
    assert "101" not in mgr3.students, "Deleted student ID found in reloaded file"
    print("Record deletion verified and correctly persisted.")

    print("\n==============================")
    print("  ALL PROGRAMMATIC TESTS PASSED")
    print("==============================")

    # Clean up test file
    if os.path.exists(test_db):
        try:
            os.remove(test_db)
        except Exception:
            pass

if __name__ == "__main__":
    run_tests()
