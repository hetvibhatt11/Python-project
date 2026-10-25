import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error

# Change these settings to match your local MySQL setup.
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",  # Add your MySQL password here if you have one.
    "database": "student_result_db",
}

SUBJECTS = ["Python", "Java", "DBMS", "Software Engineering", "DAA"]


def connect_db():
    return mysql.connector.connect(**DB_CONFIG)


def setup_database():
    """Create the database and table if they do not already exist."""
    server_config = {key: value for key, value in DB_CONFIG.items()
                     if key != "database"}
    conn = mysql.connector.connect(**server_config)
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS student_result_db")
    cursor.close()
    conn.close()

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id VARCHAR(30) NOT NULL UNIQUE,
            name VARCHAR(100) NOT NULL,
            roll_no VARCHAR(30) NOT NULL UNIQUE,
            python_marks DECIMAL(5,2) NOT NULL,
            java_marks DECIMAL(5,2) NOT NULL,
            dbms_marks DECIMAL(5,2) NOT NULL,
            se_marks DECIMAL(5,2) NOT NULL,
            daa_marks DECIMAL(5,2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()


def calculate_result(marks):
    total = sum(marks)
    percentage = total / len(SUBJECTS)
    if percentage >= 90:
        grade = "A+"
    elif percentage >= 80:
        grade = "A"
    elif percentage >= 70:
        grade = "B"
    elif percentage >= 60:
        grade = "C"
    elif percentage >= 50:
        grade = "D"
    else:
        grade = "F"
    return total, percentage, grade


def validate_student(student_id, name, roll_no, mark_values):
    if not student_id.strip() or not name.strip() or not roll_no.strip():
        raise ValueError("Student ID, name, and roll number are required.")
    if not all(ch.isalpha() or ch.isspace() or ch in "-'." for ch in name.strip()):
        raise ValueError("Name can contain letters, spaces, hyphens, apostrophes, and periods.")
    marks = []
    for subject, value in zip(SUBJECTS, mark_values):
        try:
            mark = float(value)
        except ValueError:
            raise ValueError(f"Enter a valid number for {subject} marks.")
        if not 0 <= mark <= 100:
            raise ValueError(f"{subject} marks must be between 0 and 100.")
        marks.append(mark)
    return marks


class StudentResultApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Result Management System")
        self.root.geometry("1120x700")
        self.root.minsize(980, 620)
        self.selected_db_id = None

        self.build_ui()
        self.load_students()

    def build_ui(self):
        title = ttk.Label(self.root, text="STUDENT RESULT MANAGEMENT SYSTEM",
                          font=("Segoe UI", 18, "bold"))
        title.pack(pady=(14, 8))

        form = ttk.LabelFrame(self.root, text="Student Details and Marks", padding=12)
        form.pack(fill="x", padx=16, pady=6)

        ttk.Label(form, text="Student ID").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.student_id_entry = ttk.Entry(form, width=22)
        self.student_id_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Student Name").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.name_entry = ttk.Entry(form, width=28)
        self.name_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Roll Number").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.roll_entry = ttk.Entry(form, width=18)
        self.roll_entry.grid(row=0, column=5, padx=5, pady=5)

        self.mark_entries = {}
        for index, subject in enumerate(SUBJECTS):
            ttk.Label(form, text=f"{subject} (0-100)").grid(
                row=1, column=index, sticky="w", padx=5, pady=(12, 3))
            entry = ttk.Entry(form, width=17)
            entry.grid(row=2, column=index, padx=5, pady=4, sticky="ew")
            self.mark_entries[subject] = entry

        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

        buttons = ttk.Frame(self.root, padding=(16, 6))
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Add Student", command=self.add_student).pack(side="left", padx=4)
        ttk.Button(buttons, text="Update Selected", command=self.update_student).pack(side="left", padx=4)
        ttk.Button(buttons, text="Delete Selected", command=self.delete_student).pack(side="left", padx=4)
        ttk.Button(buttons, text="Clear Form", command=self.clear_form).pack(side="left", padx=4)
        ttk.Button(buttons, text="Show Result Summary", command=self.show_summary).pack(side="left", padx=4)

        search_frame = ttk.Frame(self.root, padding=(16, 5))
        search_frame.pack(fill="x")
        ttk.Label(search_frame, text="Search by ID, name, or roll number:").pack(side="left", padx=(0, 8))
        self.search_entry = ttk.Entry(search_frame, width=35)
        self.search_entry.pack(side="left", padx=4)
        self.search_entry.bind("<Return>", lambda _event: self.search_students())
        ttk.Button(search_frame, text="Search", command=self.search_students).pack(side="left", padx=4)
        ttk.Button(search_frame, text="Show All", command=self.load_students).pack(side="left", padx=4)

        columns = ("id", "student_id", "name", "roll_no", "python", "java",
                   "dbms", "se", "daa", "total", "percentage", "grade")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=13)
        headings = {
            "id": "DB ID", "student_id": "Student ID", "name": "Name",
            "roll_no": "Roll No.", "python": "Python", "java": "Java",
            "dbms": "DBMS", "se": "SE", "daa": "DAA",
            "total": "Total / 500", "percentage": "Percentage", "grade": "Grade"
        }
        widths = {"id": 55, "student_id": 85, "name": 145, "roll_no": 80,
                  "python": 65, "java": 60, "dbms": 60, "se": 60, "daa": 60,
                  "total": 85, "percentage": 90, "grade": 60}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")
        self.tree.column("name", anchor="w")
        self.tree.pack(fill="both", expand=True, padx=16, pady=(4, 8))
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w").pack(
            fill="x", side="bottom")

    def get_form_data(self):
        student_id = self.student_id_entry.get().strip()
        name = self.name_entry.get().strip()
        roll_no = self.roll_entry.get().strip()
        raw_marks = [self.mark_entries[subject].get().strip() for subject in SUBJECTS]
        marks = validate_student(student_id, name, roll_no, raw_marks)
        return student_id, name, roll_no, marks

    def add_student(self):
        try:
            student_id, name, roll_no, marks = self.get_form_data()
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO students
                (student_id, name, roll_no, python_marks, java_marks, dbms_marks, se_marks, daa_marks)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (student_id, name, roll_no, *marks))
            conn.commit()
            cursor.close()
            conn.close()
            self.load_students()
            self.clear_form()
            messagebox.showinfo("Success", "Student result added successfully.")
        except ValueError as exc:
            messagebox.showerror("Invalid input", str(exc))
        except Error as exc:
            messagebox.showerror("Database error", f"{exc}\n\nCheck MySQL is running and DB_CONFIG is correct.")

    def update_student(self):
        if self.selected_db_id is None:
            messagebox.showwarning("Select student", "Select a student row first, then edit the form.")
            return
        try:
            student_id, name, roll_no, marks = self.get_form_data()
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE students SET student_id=%s, name=%s, roll_no=%s,
                python_marks=%s, java_marks=%s, dbms_marks=%s, se_marks=%s, daa_marks=%s
                WHERE id=%s
            """, (student_id, name, roll_no, *marks, self.selected_db_id))
            conn.commit()
            cursor.close()
            conn.close()
            self.load_students()
            self.clear_form()
            messagebox.showinfo("Success", "Student result updated successfully.")
        except ValueError as exc:
            messagebox.showerror("Invalid input", str(exc))
        except Error as exc:
            messagebox.showerror("Database error", f"{exc}\n\nCheck for duplicate Student ID or Roll Number.")

    def delete_student(self):
        if self.selected_db_id is None:
            messagebox.showwarning("Select student", "Select a student row first.")
            return
        if not messagebox.askyesno("Confirm delete", "Delete the selected student's record?"):
            return
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE id=%s", (self.selected_db_id,))
            conn.commit()
            cursor.close()
            conn.close()
            self.load_students()
            self.clear_form()
            messagebox.showinfo("Success", "Student record deleted.")
        except Error as exc:
            messagebox.showerror("Database error", str(exc))

    def load_students(self):
        self.display_query("""
            SELECT id, student_id, name, roll_no, python_marks, java_marks,
                   dbms_marks, se_marks, daa_marks
            FROM students ORDER BY name
        """)
        self.status_var.set("Showing all student records")

    def search_students(self):
        term = self.search_entry.get().strip()
        if not term:
            self.load_students()
            return
        self.display_query("""
            SELECT id, student_id, name, roll_no, python_marks, java_marks,
                   dbms_marks, se_marks, daa_marks
            FROM students
            WHERE student_id LIKE %s OR name LIKE %s OR roll_no LIKE %s
            ORDER BY name
        """, (f"%{term}%", f"%{term}%", f"%{term}%"))
        self.status_var.set(f"Search results for: {term}")

    def display_query(self, query, params=()):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            for item in self.tree.get_children():
                self.tree.delete(item)
            for row in rows:
                db_id, student_id, name, roll_no, *marks = row
                marks = [float(mark) for mark in marks]
                total, percentage, grade = calculate_result(marks)
                self.tree.insert("", "end", values=(
                    db_id, student_id, name, roll_no,
                    *[f"{mark:g}" for mark in marks],
                    f"{total:g}", f"{percentage:.2f}%", grade
                ))
            self.status_var.set(f"{len(rows)} student record(s) displayed")
        except Error as exc:
            messagebox.showerror("Database error", f"{exc}\n\nStart MySQL and check DB_CONFIG.")

    def on_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        self.selected_db_id = int(values[0])
        self.clear_entries_only()
        self.student_id_entry.insert(0, values[1])
        self.name_entry.insert(0, values[2])
        self.roll_entry.insert(0, values[3])
        for subject, value in zip(SUBJECTS, values[4:9]):
            self.mark_entries[subject].insert(0, value)

    def clear_entries_only(self):
        for entry in (self.student_id_entry, self.name_entry, self.roll_entry):
            entry.delete(0, tk.END)
        for entry in self.mark_entries.values():
            entry.delete(0, tk.END)

    def clear_form(self):
        self.selected_db_id = None
        self.clear_entries_only()
        for item in self.tree.selection():
            self.tree.selection_remove(item)
        self.status_var.set("Form cleared")

    def show_summary(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT python_marks, java_marks, dbms_marks, se_marks, daa_marks
                FROM students
            """)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            if not rows:
                messagebox.showinfo("Result summary", "No student records available yet.")
                return
            averages = [sum(float(row[i]) for row in rows) / len(rows) for i in range(len(SUBJECTS))]
            lines = [f"Total students: {len(rows)}", ""]
            lines += [f"{subject} average: {averages[i]:.2f}" for i, subject in enumerate(SUBJECTS)]
            messagebox.showinfo("Result Summary", "\n".join(lines))
        except Error as exc:
            messagebox.showerror("Database error", str(exc))


def main():
    try:
        setup_database()
    except Error as exc:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Cannot connect to MySQL",
            f"{exc}\n\n1. Start MySQL in XAMPP or your MySQL service.\n"
            "2. Edit DB_CONFIG in app.py with your username/password.\n"
            "3. Install mysql-connector-python."
        )
        root.destroy()
        return

    root = tk.Tk()
    app = StudentResultApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
