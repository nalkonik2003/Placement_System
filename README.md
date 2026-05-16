# Student Placement System

A browser-based Student Placement Management System for T.Y. B.Sc Computer Science final-year project.

## Project Description

This system allows students to register, login, manage profiles, upload resumes, view job notices, apply for jobs, and check application status. Administrators can manage students, post job notices, review applications, shortlist students, and update placement results.

## Technology Stack

- **Frontend:** HTML, CSS, JavaScript (pure, no frameworks)
- **Backend:** Python Flask
- **Database:** SQLite

## Features

### Student Module
- Registration and login
- Profile management
- Resume upload (PDF only)
- View job notices
- Apply for jobs
- Check application status

### Admin Module
- Secure login
- View and manage students
- Add, update, delete job notices
- Review applications
- Shortlist students
- Update placement results

## Folder Structure

```
student-placement-system/
├── app.py                 # Main Flask application
├── placement.db           # SQLite database (created automatically)
├── uploads/               # Directory for uploaded resumes
├── static/
│   ├── css/
│   │   └── style.css      # Stylesheet
│   └── js/
│       └── script.js      # JavaScript for validation
└── templates/             # HTML templates
    ├── index.html
    ├── student_login.html
    ├── student_register.html
    ├── student_dashboard.html
    ├── student_profile.html
    ├── student_upload_resume.html
    ├── student_view_notices.html
    ├── student_status.html
    ├── admin_login.html
    ├── admin_dashboard.html
    ├── admin_students.html
    ├── admin_notices.html
    ├── admin_applications.html
    └── admin_results.html
```

## Database Schema

### Tables

1. **users** (id, username, password, role)
2. **students** (id, user_id, name, email, phone, branch, year, resume_path)
3. **jobs** (id, title, description, company, requirements, posted_date)
4. **applications** (id, student_id, job_id, applied_date, status)
5. **results** (id, application_id, result, updated_date)

## Setup and Installation

### Prerequisites
- Python 3.x installed
- pip (Python package manager)

### Installation Steps

1. **Navigate to the project directory:**
   ```
   cd student-placement-system
   ```

2. **Install Flask:**
   ```
   pip install flask
   ```

3. **Run the application:**
   ```
   python app.py
   ```

4. **Access the application:**
   - Open a web browser
   - Go to `http://127.0.0.1:5000/`

## Sample Data

The application includes sample data:
- Admin: username `admin`, password `admin123`
- Students: `student1` (pass1), `student2` (pass2)
- Jobs: Software Engineer, Data Analyst

## Usage

1. **Home Page:** Choose Student or Admin login/register
2. **Student Registration:** Create account with details
3. **Student Login:** Access dashboard, update profile, upload resume, view/apply for jobs
4. **Admin Login:** Manage students, jobs, applications, results
5. **Logout:** Securely end session

## Security Features

- Session-based authentication
- Role-based access control
- PDF validation for resume uploads
- Input validation on frontend and backend

## Browser Compatibility

- Tested on modern browsers (Chrome, Firefox, Edge)
- Responsive design for mobile and desktop

## Academic Notes

- Beginner-friendly code with comments
- Follows Flask best practices
- Suitable for viva examination
- No external dependencies except Flask

## Viewing the Database

The application uses SQLite database (`placement.db`). To view or inspect the database:

### Option 1: Using DB Browser for SQLite (Recommended)
1. Download and install [DB Browser for SQLite](https://sqlitebrowser.org/)
2. Open `placement.db` in the application
3. Browse tables, view data, run queries

### Option 2: Using Command Line
1. Open command prompt/terminal in the project directory
2. Run: `sqlite3 placement.db`
3. Use SQL commands like:
   - `.tables` - List all tables
   - `SELECT * FROM users;` - View users table
   - `SELECT * FROM students;` - View students table
   - `.exit` - Exit SQLite shell

### Option 3: Using Python Script
Create a simple script to view data:
```python
import sqlite3

conn = sqlite3.connect('placement.db')
cursor = conn.cursor()

# View all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# Example: View users
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()
print("Users:", users)

conn.close()
```

## Troubleshooting

- If port 5000 is busy, change `app.run(debug=True)` to `app.run(debug=True, port=5001)`
- Ensure uploads folder has write permissions
- Check console for error messages

## Future Enhancements

- Email notifications
- Advanced search and filters
- Bulk operations for admin
- Reporting and analytics

---

**Note:** This project is for educational purposes and demonstrates basic web development concepts using Flask and SQLite.
