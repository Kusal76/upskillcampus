/**
 * EduCore Premium Dashboard Controller
 * Integrates Chart.js data analytics, dynamically updates KPI statistics,
 * renders custom confirmation modals, and calculates animated SVG gauge rings.
 *
 * Security: All user-supplied data is HTML-escaped before rendering to prevent XSS.
 */

// Application State
let studentsState = [];
let editingStudentId = null;
let currentSortBy = "name"; // "name" or "marks"
let searchQuery = "";
let courseFilter = "all";
let gradeChartInstance = null;
let genderChartInstance = null;

// DOM Elements
const studentForm = document.getElementById("student-form");
const formTitle = document.getElementById("form-title");
const formSubtitle = document.getElementById("form-subtitle");
const submitText = document.getElementById("submit-text");
const btnReset = document.getElementById("btn-reset");

const studentIdInput = document.getElementById("student_id");
const nameInput = document.getElementById("name");
const ageInput = document.getElementById("age");
const genderInput = document.getElementById("gender");
const courseInput = document.getElementById("course");
const marksInput = document.getElementById("marks");
const emailInput = document.getElementById("email");

const searchInput = document.getElementById("search-input");
const searchClearBtn = document.getElementById("search-clear-btn");
const courseFilterSelect = document.getElementById("filter-course");
const sortByNameBtn = document.getElementById("sort-name");
const sortByMarksBtn = document.getElementById("sort-marks");
const studentsContainer = document.getElementById("students-container");
const exportCsvBtn = document.getElementById("export-csv-btn");
const themeToggleBtn = document.getElementById("theme-toggle-btn");

// KPI Display elements
const statTotal = document.getElementById("stat-total");
const statAvg = document.getElementById("stat-avg");
const statPassing = document.getElementById("stat-passing");
const statTopper = document.getElementById("stat-topper");
const courseStatsList = document.getElementById("course-stats-list");

// Toast Notification Container
const toastContainer = document.getElementById("toast-container");

// Custom Modal elements
const confirmModal = document.getElementById("confirm-modal");
const deleteStudentNameSpan = document.getElementById("delete-student-name");
const modalCancelBtn = document.getElementById("modal-cancel-btn");
const modalConfirmBtn = document.getElementById("modal-confirm-btn");
let deleteCallback = null;

// ─── Security Helper ─────────────────────────────────────────────────────────
/**
 * Escapes a string so it is safe to insert into HTML contexts.
 * Uses the browser DOM text node trick to guarantee correct escaping.
 */
function escapeHtml(value) {
    const div = document.createElement("div");
    div.appendChild(document.createTextNode(String(value ?? "")));
    return div.innerHTML;
}

// ─── Initialize Dashboard ────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    fetchStudents();
    setupEventListeners();
});

// ─── Event Bindings ──────────────────────────────────────────────────────────
function setupEventListeners() {
    studentForm.addEventListener("submit", handleFormSubmit);
    btnReset.addEventListener("click", resetFormState);

    searchInput.addEventListener("input", (e) => {
        searchQuery = e.target.value.trim().toLowerCase();
        searchClearBtn.style.display = searchQuery ? "block" : "none";
        renderStudentsGrid();
    });

    searchClearBtn.addEventListener("click", () => {
        searchInput.value = "";
        searchQuery = "";
        searchClearBtn.style.display = "none";
        renderStudentsGrid();
    });

    courseFilterSelect.addEventListener("change", (e) => {
        courseFilter = e.target.value;
        renderStudentsGrid();
    });

    sortByNameBtn.addEventListener("click", () => {
        if (currentSortBy !== "name") {
            currentSortBy = "name";
            sortByNameBtn.classList.add("active");
            sortByMarksBtn.classList.remove("active");
            fetchStudents();
        }
    });

    sortByMarksBtn.addEventListener("click", () => {
        if (currentSortBy !== "marks") {
            currentSortBy = "marks";
            sortByMarksBtn.classList.add("active");
            sortByNameBtn.classList.remove("active");
            fetchStudents();
        }
    });

    modalCancelBtn.addEventListener("click", hideDeleteModal);
    confirmModal.addEventListener("click", (e) => {
        if (e.target === confirmModal) hideDeleteModal();
    });

    exportCsvBtn.addEventListener("click", exportToCSV);
    themeToggleBtn.addEventListener("click", toggleTheme);
}

// ─── Toast Notifier ──────────────────────────────────────────────────────────
function showToast(message, type = "success") {
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;

    const content = document.createElement("span");
    content.className = "toast-content";
    content.textContent = message; // textContent — safe

    const closeBtn = document.createElement("button");
    closeBtn.className = "toast-close";
    closeBtn.textContent = "×";
    closeBtn.addEventListener("click", () => {
        toast.classList.add("hide");
        setTimeout(() => toast.remove(), 250);
    });

    toast.appendChild(content);
    toast.appendChild(closeBtn);
    toastContainer.appendChild(toast);

    setTimeout(() => {
        if (toast.parentNode) {
            toast.classList.add("hide");
            setTimeout(() => toast.remove(), 250);
        }
    }, 4000);
}

// ─── Confirmation Modal ──────────────────────────────────────────────────────
function showDeleteModal(studentName, onConfirm) {
    // Use textContent — never innerHTML — for user data
    deleteStudentNameSpan.textContent = studentName;
    confirmModal.classList.add("active");
    deleteCallback = onConfirm;

    function handleConfirm() {
        if (deleteCallback) deleteCallback();
        hideDeleteModal();
        modalConfirmBtn.removeEventListener("click", handleConfirm);
    }
    modalConfirmBtn.addEventListener("click", handleConfirm);
}

function hideDeleteModal() {
    confirmModal.classList.remove("active");
    deleteCallback = null;
}

// ─── Fetch Students ──────────────────────────────────────────────────────────
async function fetchStudents() {
    try {
        const response = await fetch(`/api/students?sort_by=${currentSortBy}`);
        if (!response.ok) throw new Error("Failed to load student profiles from database.");
        studentsState = await response.json();
        populateCourseFilter();
        renderStudentsGrid();
    } catch (error) {
        console.error(error);
        showToast(error.message, "error");
        studentsContainer.innerHTML = "";

        // Build error state without innerHTML interpolation
        const emptyDiv = document.createElement("div");
        emptyDiv.className = "empty-state";
        emptyDiv.innerHTML = `
            <svg class="empty-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>`;
        const errMsg = document.createElement("p");
        errMsg.textContent = "Failed to connect to backend server.";
        emptyDiv.appendChild(errMsg);
        studentsContainer.appendChild(emptyDiv);
    }
}

// ─── Populate Course Filter Dropdown ─────────────────────────────────────────
function populateCourseFilter() {
    const previousSelection = courseFilterSelect.value;
    const uniqueCourses = [...new Set(studentsState.map(s => s.course))].sort();

    courseFilterSelect.innerHTML = `<option value="all">All Courses</option>`;

    uniqueCourses.forEach(course => {
        const opt = document.createElement("option");
        opt.value = course;
        opt.textContent = course; // safe — textContent
        courseFilterSelect.appendChild(opt);
    });

    if (uniqueCourses.includes(previousSelection)) {
        courseFilterSelect.value = previousSelection;
        courseFilter = previousSelection;
    } else {
        courseFilterSelect.value = "all";
        courseFilter = "all";
    }
}

// ─── Render Student Cards ─────────────────────────────────────────────────────
function renderStudentsGrid() {
    studentsContainer.innerHTML = "";

    const filtered = studentsState.filter(student => {
        const matchesSearch = (
            student.student_id.toLowerCase().includes(searchQuery) ||
            student.name.toLowerCase().includes(searchQuery) ||
            student.course.toLowerCase().includes(searchQuery)
        );
        const matchesCourse = (courseFilter === "all" || student.course === courseFilter);
        return matchesSearch && matchesCourse;
    });

    updateKPINumbers(filtered);
    renderGradeDistributionChart(filtered);
    renderGenderDistributionChart(filtered);
    renderCourseStats(filtered);

    if (filtered.length === 0) {
        const emptyDiv = document.createElement("div");
        emptyDiv.className = "empty-state";
        emptyDiv.innerHTML = `
            <svg class="empty-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M8 14s1.5 2 4 2 4-2 4-2"/>
                <line x1="9" y1="9" x2="9.01" y2="9"/>
                <line x1="15" y1="9" x2="15.01" y2="9"/>
            </svg>`;
        const msg = document.createElement("p");
        msg.textContent = (searchQuery || courseFilter !== "all")
            ? "No students match the current filter criteria."
            : "Database empty. Create a student to get started.";
        emptyDiv.appendChild(msg);
        studentsContainer.appendChild(emptyDiv);
        return;
    }

    filtered.forEach((student, index) => {
        const circ = 175.93;
        const offset = circ - (student.marks / 100) * circ;

        let strokeColor = "var(--danger)";
        if (student.marks >= 75) strokeColor = "var(--success)";
        else if (student.marks >= 50) strokeColor = "var(--color-purple)";
        else if (student.marks >= 40) strokeColor = "var(--warning)";

        // ── Build card using safe DOM methods ──
        const card = document.createElement("div");
        card.className = "student-card";
        card.style.animationDelay = `${index * 0.05}s`;

        // Use escapeHtml only for values placed into HTML attribute strings
        const eName   = escapeHtml(student.name);
        const eSid    = escapeHtml(student.student_id);
        const eCourse = escapeHtml(student.course);
        const eGender = escapeHtml(student.gender);
        const eEmail  = escapeHtml(student.email);
        const eMarks  = Math.round(student.marks);

        card.innerHTML = `
            <div class="student-card-main">
                <div class="info-side">
                    <h3 title="${eName}">${eName}</h3>
                    <span class="sid">ID: ${eSid}</span>
                    <div class="badge-row">
                        <span class="badge course">${eCourse}</span>
                        <span class="badge gender">${eGender}</span>
                    </div>
                </div>
                <div class="progress-ring">
                    <svg>
                        <circle class="progress-ring-bg" cx="33" cy="33" r="28" />
                        <circle class="progress-ring-fill" cx="33" cy="33" r="28"
                                stroke="${strokeColor}"
                                stroke-dasharray="${circ}"
                                stroke-dashoffset="${offset}" />
                    </svg>
                    <span class="progress-value">${eMarks}%</span>
                </div>
            </div>

            <div class="student-meta">
                <div class="meta-row">
                    <span class="meta-label">Age</span>
                    <span class="meta-val">${escapeHtml(student.age)} years</span>
                </div>
                <div class="meta-row">
                    <span class="meta-label">Email</span>
                    <span class="meta-val email-val" title="${eEmail}">${eEmail}</span>
                </div>
            </div>

            <div class="card-footer-actions">
                <button class="card-btn edit" type="button">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                    </svg>
                    Edit
                </button>
                <button class="card-btn delete" type="button">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3 6 5 6 21 6"/>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                        <line x1="10" y1="11" x2="10" y2="17"/>
                        <line x1="14" y1="11" x2="14" y2="17"/>
                    </svg>
                    Delete
                </button>
            </div>
        `;

        // Attach event listeners using the raw student_id (not embedded in HTML)
        card.querySelector(".card-btn.edit").addEventListener("click", () => {
            startEditStudent(student.student_id);
        });
        card.querySelector(".card-btn.delete").addEventListener("click", () => {
            triggerDeleteStudent(student.student_id, student.name);
        });

        studentsContainer.appendChild(card);
    });
}

// ─── KPI Ribbon Numbers ───────────────────────────────────────────────────────
function updateKPINumbers(studentList) {
    statTotal.textContent = studentList.length;

    if (studentList.length === 0) {
        statAvg.textContent = "0.0%";
        statPassing.textContent = "0%";
        statTopper.textContent = "N/A";
        return;
    }

    const sumMarks = studentList.reduce((acc, s) => acc + s.marks, 0);
    const avg = sumMarks / studentList.length;
    statAvg.textContent = `${avg.toFixed(1)}%`;

    const passingCount = studentList.filter(s => s.marks >= 40).length;
    statPassing.textContent = `${Math.round((passingCount / studentList.length) * 100)}%`;

    const topper = studentList.reduce((best, s) => s.marks > best.marks ? s : best, studentList[0]);
    // Use textContent to safely display topper name
    statTopper.textContent = `${topper.name} (${Math.round(topper.marks)}%)`;
}

// ─── Grade Distribution Chart ─────────────────────────────────────────────────
function renderGradeDistributionChart(studentList) {
    const isLight = document.body.classList.contains("light-theme");
    const grades = { Outstanding: 0, Excellent: 0, Good: 0, Pass: 0, Fail: 0 };

    studentList.forEach(s => {
        if (s.marks >= 90) grades.Outstanding++;
        else if (s.marks >= 75) grades.Excellent++;
        else if (s.marks >= 50) grades.Good++;
        else if (s.marks >= 40) grades.Pass++;
        else grades.Fail++;
    });

    const dataValues = [grades.Outstanding, grades.Excellent, grades.Good, grades.Pass, grades.Fail];

    if (gradeChartInstance) {
        gradeChartInstance.data.datasets[0].data = dataValues;
        gradeChartInstance.update();
        return;
    }

    const ctx = document.getElementById("gradeChart").getContext("2d");
    gradeChartInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["Outstanding", "Excellent", "Good", "Pass", "Fail"],
            datasets: [{
                label: "Students",
                data: dataValues,
                backgroundColor: [
                    "rgba(16, 185, 129, 0.45)",
                    "rgba(139, 92, 246, 0.45)",
                    "rgba(59, 130, 246, 0.45)",
                    "rgba(245, 158, 11, 0.45)",
                    "rgba(244, 63, 94, 0.45)"
                ],
                borderColor: ["#10b981", "#8b5cf6", "#3b82f6", "#f59e0b", "#f43f5e"],
                borderWidth: 1.5,
                borderRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1, color: isLight ? "#475569" : "#94a3b8" },
                    grid: { color: isLight ? "rgba(15,23,42,0.08)" : "rgba(255,255,255,0.04)" }
                },
                x: {
                    ticks: { color: isLight ? "#475569" : "#94a3b8", font: { size: 10 } },
                    grid: { display: false }
                }
            }
        }
    });
}

// ─── Gender Distribution Chart ────────────────────────────────────────────────
function renderGenderDistributionChart(studentList) {
    const genders = { Male: 0, Female: 0, Other: 0 };
    studentList.forEach(s => {
        const g = String(s.gender).trim();
        if (g === "Male") genders.Male++;
        else if (g === "Female") genders.Female++;
        else genders.Other++;
    });

    const dataValues = [genders.Male, genders.Female, genders.Other];

    if (genderChartInstance) {
        genderChartInstance.data.datasets[0].data = dataValues;
        genderChartInstance.update();
        return;
    }

    const isLight = document.body.classList.contains("light-theme");
    const tickColor = isLight ? "#475569" : "#94a3b8";

    const ctx = document.getElementById("genderChart").getContext("2d");
    genderChartInstance = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Male", "Female", "Other"],
            datasets: [{
                data: dataValues,
                backgroundColor: [
                    "rgba(59, 130, 246, 0.5)",
                    "rgba(236, 72, 153, 0.5)",
                    "rgba(139, 92, 246, 0.5)"
                ],
                borderColor: ["#3b82f6", "#ec4899", "#8b5cf6"],
                borderWidth: 1.5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: "bottom",
                    labels: { color: tickColor, boxWidth: 12, font: { size: 10, weight: "600" } }
                }
            },
            cutout: "70%"
        }
    });
}

// ─── Course Performance List ──────────────────────────────────────────────────
function renderCourseStats(studentList) {
    if (!courseStatsList) return;

    if (studentList.length === 0) {
        courseStatsList.innerHTML = `<div class="loading-state-mini">No course metrics available.</div>`;
        return;
    }

    const courseGroups = {};
    studentList.forEach(s => {
        if (!courseGroups[s.course]) courseGroups[s.course] = [];
        courseGroups[s.course].push(s);
    });

    const courseSummaries = Object.keys(courseGroups).map(course => {
        const list = courseGroups[course];
        const avg = list.reduce((acc, curr) => acc + curr.marks, 0) / list.length;
        return { name: course, count: list.length, avg };
    });

    courseSummaries.sort((a, b) => a.name.localeCompare(b.name));

    courseStatsList.innerHTML = "";
    courseSummaries.forEach(summary => {
        let avgClass = "";
        if (summary.avg >= 75) avgClass = "excellent";
        else if (summary.avg >= 50) avgClass = "";
        else if (summary.avg >= 40) avgClass = "pass";
        else avgClass = "fail";

        const row = document.createElement("div");
        row.className = "course-stat-item";

        // Safe rendering — all user content goes through textContent
        const nameSpan = document.createElement("span");
        nameSpan.className = "course-stat-name";
        nameSpan.title = summary.name;
        nameSpan.textContent = summary.name;

        const badgesDiv = document.createElement("div");
        badgesDiv.className = "course-stat-badges";

        const countBadge = document.createElement("span");
        countBadge.className = "stat-badge count";
        countBadge.textContent = `${summary.count} ${summary.count === 1 ? "Student" : "Students"}`;

        const marksBadge = document.createElement("span");
        marksBadge.className = `stat-badge marks ${avgClass}`;
        marksBadge.textContent = `${summary.avg.toFixed(1)}% Avg`;

        badgesDiv.appendChild(countBadge);
        badgesDiv.appendChild(marksBadge);
        row.appendChild(nameSpan);
        row.appendChild(badgesDiv);
        courseStatsList.appendChild(row);
    });
}

// ─── Form Validation ──────────────────────────────────────────────────────────
function validateForm() {
    let isValid = true;
    document.querySelectorAll(".error-msg").forEach(el => el.textContent = "");

    const studentId = studentIdInput.value.trim();
    if (!studentId) {
        document.getElementById("err-student_id").textContent = "Student ID cannot be empty.";
        isValid = false;
    } else if (!editingStudentId) {
        const isDuplicate = studentsState.some(s => s.student_id.toLowerCase() === studentId.toLowerCase());
        if (isDuplicate) {
            document.getElementById("err-student_id").textContent = "Duplicate Student ID found.";
            isValid = false;
        }
    }

    if (!nameInput.value.trim()) {
        document.getElementById("err-name").textContent = "Name cannot be empty.";
        isValid = false;
    }

    const age = parseInt(ageInput.value);
    if (isNaN(age) || age <= 0) {
        document.getElementById("err-age").textContent = "Age must be greater than 0.";
        isValid = false;
    }

    if (!genderInput.value) {
        document.getElementById("err-gender").textContent = "Please select a gender option.";
        isValid = false;
    }

    if (!courseInput.value.trim()) {
        document.getElementById("err-course").textContent = "Course field is required.";
        isValid = false;
    }

    const marks = parseFloat(marksInput.value);
    if (isNaN(marks) || marks < 0 || marks > 100) {
        document.getElementById("err-marks").textContent = "Marks must range from 0 to 100.";
        isValid = false;
    }

    const email = emailInput.value.trim();
    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!email) {
        document.getElementById("err-email").textContent = "Email is required.";
        isValid = false;
    } else if (!emailPattern.test(email)) {
        document.getElementById("err-email").textContent = "Invalid email formatting.";
        isValid = false;
    }

    return isValid;
}

// ─── Form Submit ──────────────────────────────────────────────────────────────
async function handleFormSubmit(e) {
    e.preventDefault();
    if (!validateForm()) return;

    const payload = {
        student_id: studentIdInput.value.trim(),
        name: nameInput.value.trim(),
        age: parseInt(ageInput.value),
        gender: genderInput.value,
        course: courseInput.value.trim(),
        marks: parseFloat(marksInput.value),
        email: emailInput.value.trim()
    };

    try {
        let response;
        if (editingStudentId) {
            response = await fetch(`/api/students/${editingStudentId}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
        } else {
            response = await fetch("/api/students", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
        }

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Server transaction error.");

        showToast(data.message, "success");
        resetFormState();
        fetchStudents();
    } catch (error) {
        console.error(error);
        showToast(error.message, "error");
    }
}

// ─── Edit Mode ────────────────────────────────────────────────────────────────
function startEditStudent(studentId) {
    const student = studentsState.find(s => s.student_id === studentId);
    if (!student) return;

    editingStudentId = studentId;

    studentIdInput.value = student.student_id;
    studentIdInput.readOnly = true;
    studentIdInput.classList.add("readonly-field");

    nameInput.value = student.name;
    ageInput.value = student.age;
    genderInput.value = student.gender;
    courseInput.value = student.course;
    marksInput.value = student.marks;
    emailInput.value = student.email;

    formTitle.textContent = "Edit Student Profile";
    formSubtitle.textContent = `Updating Profile ID: ${studentId}`;
    submitText.textContent = "Update Student";
    btnReset.style.display = "block";

    document.querySelector(".form-container").scrollIntoView({ behavior: "smooth" });
}

// ─── Form Reset ───────────────────────────────────────────────────────────────
function resetFormState() {
    editingStudentId = null;
    studentForm.reset();

    studentIdInput.readOnly = false;
    studentIdInput.classList.remove("readonly-field");

    formTitle.textContent = "Add Student Record";
    formSubtitle.textContent = "Enter credentials to register a student";
    submitText.textContent = "Register Student";
    btnReset.style.display = "none";

    document.querySelectorAll(".error-msg").forEach(el => el.textContent = "");
}

// ─── Delete Student ────────────────────────────────────────────────────────────
function triggerDeleteStudent(studentId, studentName) {
    showDeleteModal(studentName, async () => {
        try {
            const response = await fetch(`/api/students/${studentId}`, { method: "DELETE" });
            const data = await response.json();

            if (!response.ok) throw new Error(data.error || "Failed to delete student record.");

            showToast(data.message, "success");
            if (editingStudentId === studentId) resetFormState();
            fetchStudents();
        } catch (error) {
            console.error(error);
            showToast(error.message, "error");
        }
    });
}

// ─── CSV Export ───────────────────────────────────────────────────────────────
function exportToCSV() {
    if (studentsState.length === 0) {
        showToast("No student records available to export.", "error");
        return;
    }

    const headers = ["Student ID", "Name", "Age", "Gender", "Course", "Marks (%)", "Email"];
    const rows = studentsState.map(s => [
        s.student_id, s.name, s.age, s.gender, s.course, s.marks, s.email
    ]);

    const csvContent = [headers, ...rows]
        .map(row => row.map(val => `"${String(val).replace(/"/g, '""')}"`).join(","))
        .join("\n");

    try {
        const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", "student_records.csv");
        link.style.visibility = "hidden";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url); // Free memory
        showToast("Student database exported to CSV successfully!", "success");
    } catch (error) {
        console.error(error);
        showToast("Failed to generate CSV export file.", "error");
    }
}

// ─── Theme Management ─────────────────────────────────────────────────────────
function initTheme() {
    const savedTheme = localStorage.getItem("theme");
    setTheme(savedTheme === "light" ? "light" : "dark");
}

function toggleTheme() {
    const isLight = document.body.classList.contains("light-theme");
    setTheme(isLight ? "dark" : "light");
    showToast(isLight ? "Switched to Cosmic Dark mode" : "Switched to Premium Light mode", "success");
}

function setTheme(themeName) {
    const sunIcon = themeToggleBtn.querySelector(".sun");
    const moonIcon = themeToggleBtn.querySelector(".moon");

    if (themeName === "light") {
        document.body.classList.add("light-theme");
        sunIcon.style.display = "none";
        moonIcon.style.display = "block";
    } else {
        document.body.classList.remove("light-theme");
        sunIcon.style.display = "block";
        moonIcon.style.display = "none";
    }

    localStorage.setItem("theme", themeName);
    updateChartTheme();
}

function updateChartTheme() {
    const isLight = document.body.classList.contains("light-theme");
    const tickColor = isLight ? "#475569" : "#94a3b8";
    const gridColor = isLight ? "rgba(15,23,42,0.08)" : "rgba(255,255,255,0.04)";

    if (gradeChartInstance) {
        gradeChartInstance.options.scales.y.ticks.color = tickColor;
        gradeChartInstance.options.scales.y.grid.color = gridColor;
        gradeChartInstance.options.scales.x.ticks.color = tickColor;
        gradeChartInstance.update();
    }

    if (genderChartInstance) {
        genderChartInstance.options.plugins.legend.labels.color = tickColor;
        genderChartInstance.update();
    }
}
