from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import sqlite3
import os
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def get_db():
    """Get database connection."""
    conn = sqlite3.connect('placement.db', timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database and create tables."""
    db = get_db()
    db.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        branch TEXT NOT NULL,
        year TEXT NOT NULL,
        skills TEXT,
        resume_path TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        company TEXT NOT NULL,
        requirements TEXT NOT NULL,
        location TEXT,
        salary TEXT,
        job_type TEXT,
        posted_date TEXT NOT NULL,
        deadline TEXT
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        website TEXT,
        industry TEXT
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY,
        student_id INTEGER NOT NULL,
        job_id INTEGER NOT NULL,
        applied_date TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY(student_id) REFERENCES students(id),
        FOREIGN KEY(job_id) REFERENCES jobs(id)
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY,
        application_id INTEGER NOT NULL,
        result TEXT NOT NULL,
        updated_date TEXT NOT NULL,
        FOREIGN KEY(application_id) REFERENCES applications(id)
    )''')
    
    # Check if database is already populated
    user_count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if user_count == 0:
        # Insert sample data ONLY if the database is empty
        db.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('admin', 'admin123', 'admin'))
        db.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('student1', 'pass1', 'student'))
        db.execute("INSERT INTO students (user_id, name, email, phone, branch, year) VALUES (?, ?, ?, ?, ?, ?)", (2, 'John Doe', 'john@example.com', '1234567890', 'Computer Science', 'TY'))
        db.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('student2', 'pass2', 'student'))
        db.execute("INSERT INTO students (user_id, name, email, phone, branch, year) VALUES (?, ?, ?, ?, ?, ?)", (3, 'Jane Smith', 'jane@example.com', '0987654321', 'Information Technology', 'TY'))
        
        today = datetime.now().strftime('%Y-%m-%d')
        deadline = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        db.execute("INSERT INTO jobs (title, description, company, requirements, location, salary, job_type, posted_date, deadline) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
            ('Software Engineer', 'Develop software applications', 'Tech Corp', 'BSc CS, Python knowledge', 'Remote', '5-8 LPA', 'Full-time', today, deadline))
        db.execute("INSERT INTO jobs (title, description, company, requirements, location, salary, job_type, posted_date, deadline) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
            ('Data Analyst', 'Analyze data', 'Data Inc', 'BSc CS, SQL knowledge', 'Mumbai', '3-5 LPA', 'Full-time', today, deadline))
        db.execute("INSERT INTO jobs (title, description, company, requirements, location, salary, job_type, posted_date, deadline) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
            ('Web Developer', 'Build websites', 'Web Solutions', 'HTML, CSS, JavaScript', 'Pune', '4-6 LPA', 'Full-time', today, deadline))
    
    db.commit()
    db.close()

def cleanup_expired_jobs():
    """Delete jobs past their deadline."""
    db = get_db()
    today = datetime.now().strftime('%Y-%m-%d')
    # Only delete if deadline is set and not empty
    db.execute("DELETE FROM jobs WHERE deadline IS NOT NULL AND deadline != '' AND deadline < ?", (today,))
    db.commit()
    db.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    cleanup_expired_jobs()
    return render_template('index.html')

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please enter username and password', 'error')
            return render_template('student_login.html')
            
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ? AND role = ?', (username, password, 'student')).fetchone()
        
        if user:
            session['user_id'] = user['id']
            session['role'] = 'student'
            session['username'] = user['username']
            db.close()
            return redirect(url_for('student_dashboard'))
        else:
            db.close()
            flash('Invalid username or password', 'error')
            return render_template('student_login.html')
    return render_template('student_login.html')

@app.route('/student/register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        branch = request.form['branch']
        year = request.form['year']
        db = get_db()
        try:
            db.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, password, 'student'))
            user_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
            db.execute('INSERT INTO students (user_id, name, email, phone, branch, year) VALUES (?, ?, ?, ?, ?, ?)', (user_id, name, email, phone, branch, year))
            db.commit()
            db.close()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('student_login'))
        except sqlite3.IntegrityError:
            flash('Username already exists', 'error')
            db.close()
    return render_template('student_register.html')

@app.route('/student/dashboard')
def student_dashboard():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('student_login'))
    db = get_db()
    student = db.execute('SELECT * FROM students WHERE user_id = ?', (session['user_id'],)).fetchone()
    
    if not student:
        db.close()
        session.clear()
        flash('Student profile not found. Please register again.', 'error')
        return redirect(url_for('student_login'))
    
    jobs_count = db.execute('SELECT COUNT(*) as count FROM jobs').fetchone()['count']
    applied_count = db.execute('SELECT COUNT(*) as count FROM applications WHERE student_id = ?', (student['id'],)).fetchone()['count']
    shortlisted_count = db.execute("SELECT COUNT(*) as count FROM applications WHERE student_id = ? AND status = 'shortlisted'", (student['id'],)).fetchone()['count']
    placed_count = db.execute("SELECT COUNT(*) as count FROM applications WHERE student_id = ? AND status = 'placed'", (student['id'],)).fetchone()['count']
    db.close()
    
    return render_template('student_dashboard.html', student=student, jobs_count=jobs_count, applied_count=applied_count, shortlisted_count=shortlisted_count, placed_count=placed_count)

@app.route('/student/profile', methods=['GET', 'POST'])
def student_profile():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('student_login'))
    db = get_db()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        branch = request.form['branch']
        year = request.form['year']
        skills = request.form.get('skills', '')
        db.execute('UPDATE students SET name = ?, email = ?, phone = ?, branch = ?, year = ?, skills = ? WHERE user_id = ?', (name, email, phone, branch, year, skills, session['user_id']))
        db.commit()
        db.close()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student_dashboard'))
    student = db.execute('SELECT * FROM students WHERE user_id = ?', (session['user_id'],)).fetchone()
    db.close()
    return render_template('student_profile.html', student=student)

@app.route('/student/upload_resume', methods=['GET', 'POST'])
def student_upload_resume():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('student_login'))
    if request.method == 'POST':
        file = request.files['resume']
        if file and allowed_file(file.filename):
            filename = f"{session['user_id']}_{secure_filename(file.filename)}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            db = get_db()
            db.execute('UPDATE students SET resume_path = ? WHERE user_id = ?', (filepath, session['user_id']))
            db.commit()
            db.close()
            flash('Resume uploaded successfully!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid file type. Only PDF allowed.', 'error')
    return render_template('student_upload_resume.html')

@app.route('/student/notices')
def student_notices():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('student_login'))
    cleanup_expired_jobs()
    db = get_db()
    jobs = db.execute('SELECT * FROM jobs ORDER BY posted_date DESC').fetchall()
    
    student = db.execute('SELECT id FROM students WHERE user_id = ?', (session['user_id'],)).fetchone()
    applied_jobs = [app['job_id'] for app in db.execute('SELECT job_id FROM applications WHERE student_id = ?', (student['id'],)).fetchall()]
    
    companies = list(set([job['company'] for job in jobs]))
    db.close()
    
    return render_template('student_view_notices.html', jobs=jobs, applied_jobs=applied_jobs, companies=companies)

@app.route('/student/apply/<int:job_id>', methods=['POST'])
def student_apply(job_id):
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('student_login'))
    db = get_db()
    student = db.execute('SELECT id FROM students WHERE user_id = ?', (session['user_id'],)).fetchone()
    
    existing = db.execute('SELECT * FROM applications WHERE student_id = ? AND job_id = ?', (student['id'], job_id)).fetchone()
    if existing:
        flash('You have already applied for this job!', 'warning')
    else:
        db.execute('INSERT INTO applications (student_id, job_id, applied_date, status) VALUES (?, ?, ?, ?)', (student['id'], job_id, datetime.now().strftime('%Y-%m-%d'), 'applied'))
        db.commit()
        flash('Application submitted successfully!', 'success')
    db.close()
    return redirect(url_for('student_notices'))

@app.route('/student/status')
def student_status():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('student_login'))
    db = get_db()
    student = db.execute('SELECT id FROM students WHERE user_id = ?', (session['user_id'],)).fetchone()
    applications = db.execute('''
        SELECT a.id, a.applied_date, j.title, a.status, r.result
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        LEFT JOIN results r ON a.id = r.application_id
        WHERE a.student_id = ?
        ORDER BY a.applied_date DESC
    ''', (student['id'],)).fetchall()
    db.close()
    return render_template('student_status.html', applications=applications)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please enter username and password', 'error')
            return render_template('admin_login.html')
            
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ? AND role = ?', (username, password, 'admin')).fetchone()
        
        if user:
            session['user_id'] = user['id']
            session['role'] = 'admin'
            session['username'] = user['username']
            db.close()
            return redirect(url_for('admin_dashboard'))
        else:
            db.close()
            flash('Invalid username or password', 'error')
            return render_template('admin_login.html')
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    cleanup_expired_jobs()
    db = get_db()
    
    students_count = db.execute('SELECT COUNT(*) as count FROM students').fetchone()['count']
    jobs_count = db.execute('SELECT COUNT(*) as count FROM jobs').fetchone()['count']
    applications_count = db.execute('SELECT COUNT(*) as count FROM applications').fetchone()['count']
    placed_count = db.execute("SELECT COUNT(*) as count FROM applications WHERE status = 'placed'").fetchone()['count']
    db.close()
    
    return render_template('admin_dashboard.html', students_count=students_count, jobs_count=jobs_count, applications_count=applications_count, placed_count=placed_count)

@app.route('/admin/students')
def admin_students():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('admin_login'))
    db = get_db()
    students = db.execute('SELECT * FROM students').fetchall()
    db.close()
    return render_template('admin_students.html', students=students)

@app.route('/admin/delete_student/<int:student_id>', methods=['POST'])
def admin_delete_student(student_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('admin_login'))
    db = get_db()
    student = db.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    if student:
        user_id = student['user_id']
        db.execute('DELETE FROM applications WHERE student_id = ?', (student_id,))
        db.execute('DELETE FROM students WHERE id = ?', (student_id,))
        db.execute('DELETE FROM users WHERE id = ?', (user_id,))
        db.commit()
        flash('Student deleted successfully!', 'success')
    db.close()
    return redirect(url_for('admin_students'))

@app.route('/admin/view_student/<int:student_id>')
def view_student(student_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('admin_login'))
    db = get_db()
    student = db.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    applications = db.execute('''
        SELECT a.*, j.title, j.company
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        WHERE a.student_id = ?
    ''', (student_id,)).fetchall()
    db.close()
    return render_template('admin_view_student.html', student=student, applications=applications)

@app.route('/admin/notices', methods=['GET', 'POST'])
def admin_notices():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('admin_login'))
    cleanup_expired_jobs()
    db = get_db()
    if request.method == 'POST':
        if 'add' in request.form:
            title = request.form['title']
            description = request.form['description']
            company = request.form['company']
            requirements = request.form['requirements']
            location = request.form.get('location', '')
            salary = request.form.get('salary', '')
            job_type = request.form.get('job_type', 'Full-time')
            deadline = request.form.get('deadline', '')
            db.execute('INSERT INTO jobs (title, description, company, requirements, location, salary, job_type, posted_date, deadline) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                (title, description, company, requirements, location, salary, job_type, datetime.now().strftime('%Y-%m-%d'), deadline))
            db.commit()
            flash('Job posted successfully!', 'success')
        elif 'delete' in request.form:
            job_id = request.form['job_id']
            db.execute('DELETE FROM applications WHERE job_id = ?', (job_id,))
            db.execute('DELETE FROM jobs WHERE id = ?', (job_id,))
            db.commit()
            flash('Job deleted successfully!', 'success')
    jobs = db.execute('SELECT * FROM jobs ORDER BY posted_date DESC').fetchall()
    db.close()
    return render_template('admin_notices.html', jobs=jobs)

@app.route('/admin/applications')
def admin_applications():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('admin_login'))
    cleanup_expired_jobs()
    db = get_db()
    applications = db.execute('''
        SELECT a.id, a.applied_date, s.name, s.id as student_id, j.title, a.status
        FROM applications a
        JOIN students s ON a.student_id = s.id
        JOIN jobs j ON a.job_id = j.id
        ORDER BY a.applied_date DESC
    ''').fetchall()
    db.close()
    return render_template('admin_applications.html', applications=applications)

@app.route('/admin/view_application/<int:app_id>')
def admin_view_application(app_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('admin_login'))
    db = get_db()
    application = db.execute('''
        SELECT a.*, s.name, s.email, s.phone, s.branch, s.year, s.skills, s.resume_path, s.id as student_id,
               j.title, j.company, j.description, j.requirements
        FROM applications a
        JOIN students s ON a.student_id = s.id
        JOIN jobs j ON a.job_id = j.id
        WHERE a.id = ?
    ''', (app_id,)).fetchone()
    db.close()
    if not application:
        flash('Application not found', 'error')
        return redirect(url_for('admin_applications'))
    return render_template('admin_view_application.html', application=application)

@app.route('/admin/shortlist/<int:app_id>', methods=['POST'])
def admin_shortlist(app_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('admin_login'))
    db = get_db()
    db.execute('UPDATE applications SET status = ? WHERE id = ?', ('shortlisted', app_id))
    db.commit()
    db.close()
    flash('Student shortlisted successfully!', 'success')
    return redirect(url_for('admin_applications'))

@app.route('/admin/results', methods=['GET', 'POST'])
def admin_results():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('admin_login'))
    db = get_db()
    if request.method == 'POST':
        app_id = request.form['app_id']
        result = request.form['result']
        existing = db.execute('SELECT * FROM results WHERE application_id = ?', (app_id,)).fetchone()
        if existing:
            db.execute('UPDATE results SET result = ?, updated_date = ? WHERE application_id = ?', (result, datetime.now().strftime('%Y-%m-%d'), app_id))
        else:
            db.execute('INSERT INTO results (application_id, result, updated_date) VALUES (?, ?, ?)', (app_id, result, datetime.now().strftime('%Y-%m-%d')))
        db.execute('UPDATE applications SET status = ? WHERE id = ?', ('placed' if result == 'placed' else 'rejected', app_id))
        db.commit()
        flash('Result updated successfully!', 'success')
    applications = db.execute('''
        SELECT a.id, s.name, j.title, a.status
        FROM applications a
        JOIN students s ON a.student_id = s.id
        JOIN jobs j ON a.job_id = j.id
        WHERE a.status IN ('shortlisted', 'placed', 'rejected')
    ''').fetchall()
    db.close()
    return render_template('admin_results.html', applications=applications)

@app.route('/download_resume/<int:student_id>')
def download_resume(student_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('admin_login'))
    db = get_db()
    student = db.execute('SELECT resume_path FROM students WHERE id = ?', (student_id,)).fetchone()
    db.close()
    if student and student['resume_path']:
        resume_path = student['resume_path']
        # Normalize path for the current OS
        abs_path = os.path.abspath(resume_path)
        if os.path.exists(abs_path):
            directory = os.path.dirname(abs_path)
            filename = os.path.basename(abs_path)
            return send_from_directory(directory, filename, as_attachment=False)
        else:
            flash(f'Resume file not found at {resume_path}', 'error')
    else:
        flash('No resume found for this student', 'error')
    return redirect(url_for('admin_students'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
