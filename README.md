# Student Management System (EduCore SMS)

A professional, object-oriented full-stack application for managing student records. This project features a modern **Flask Web Dashboard** alongside a robust **Console-based Interface**, both sharing the same business logic, validation rules, and persistent JSON database.

---

## 🌟 Key Features

- **Dual Interfaces**: 
  - **Web Dashboard**: Modern single-page web app with interactive cards, search filters, forms, and real-time status counters.
  - **Console Application**: Prompt-based interactive terminal loop with colored feedback.
- **Data Synchronization**: Real-time saving/loading of student records using a standard JSON database.
- **Input Validations**:
  - Student ID uniqueness constraints.
  - Regular expression-based email format validation.
  - Grade/Marks limit check (0 to 100).
  - Age limits (must be strictly greater than 0).
- **Responsive Aesthetics**: Modern dark mode UI styled using premium vanilla CSS with glassmorphic accents, responsive grid cards, and smooth hover micro-animations.
- **Advance Data Sorting**: Toggle sorting list views by Name (A-Z) or Marks (Highest to Lowest) instantly in both web and console modes.

---

## 📂 Project Structure

```
student_management_system/
│
├── server.py              # Flask Web Server & REST API endpoints
├── main.py                # Console terminal interface
├── student.py             # Student data model representation
├── manager.py             # Business logic (CRUD, validations, JSON IO)
├── requirements.txt       # Project requirements (includes Flask)
├── README.md              # Installation and usage instructions
├── REPORT.md              # Project report containing design diagrams & analysis
├── verify_sms.py          # Programmatic unit test suite
│
├── data/
│   └── students.json      # Persistent JSON data store
│
├── templates/
│   └── index.html         # Web Dashboard HTML structure
│
└── static/
    ├── css/
    │   └── style.css      # Premium layout styles & glassmorphic details
    └── js/
        └── app.js         # JavaScript application controller (fetch, DOM, alerts)
```

---

## 🚀 Getting Started

### Prerequisites

Ensure you have **Python 3.8 or higher** installed.

### Installation

1. Navigate to the project directory:
   ```bash
   cd student_management_system
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 💻 Running the Application

### Option A: Launch the Web Dashboard (Recommended)

1. Start the Flask server:
   ```bash
   python server.py
   ```
2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```
3. Use the sidebar form to add/edit profiles, filter entries via the search bar, or delete student profiles.

### Option B: Run the Console Application

If you prefer using the terminal command-line interface:
```bash
python main.py
```

---

## 🧪 Testing and Verification

To execute the programmatic unit test suite (runs 10 automated CRUD, validation, and serialization assertions):
```bash
python verify_sms.py
```
