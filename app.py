from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, 'static'),
    template_folder=os.path.join(BASE_DIR, 'templates')
)

app.secret_key = 'ccs_secret_key_2026'

# ─── Database Setup ───────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(os.path.join(BASE_DIR, 'database.db'))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()

    # Users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            idnum       TEXT    NOT NULL UNIQUE,
            lastname    TEXT    NOT NULL,
            firstname   TEXT    NOT NULL,
            midname     TEXT,
            email       TEXT    NOT NULL UNIQUE,
            course      TEXT    NOT NULL,
            level       TEXT    NOT NULL,
            address     TEXT    NOT NULL,
            password    TEXT    NOT NULL,
            sessions    INTEGER NOT NULL DEFAULT 30
        )
    ''')

    # Active sit-in sessions (current)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS sitin (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            idnum       TEXT    NOT NULL,
            name        TEXT    NOT NULL,
            purpose     TEXT    NOT NULL,
            lab         TEXT    NOT NULL,
            session     INTEGER NOT NULL,
            date        TEXT    NOT NULL DEFAULT (DATE('now'))
        )
    ''')

    # Completed sit-in records (reports)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS sitin_reports (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            idnum       TEXT    NOT NULL,
            name        TEXT    NOT NULL,
            purpose     TEXT    NOT NULL,
            lab         TEXT    NOT NULL,
            session     INTEGER NOT NULL,
            date        TEXT    NOT NULL
        )
    ''')

    # Announcements table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS announcements (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT    NOT NULL,
            date    TEXT    NOT NULL DEFAULT (DATE('now'))
        )
    ''')

    # Reservations table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            idnum       TEXT    NOT NULL,
            name        TEXT    NOT NULL,
            lab         TEXT    NOT NULL,
            date        TEXT    NOT NULL,
            time        TEXT    NOT NULL,
            status      TEXT    NOT NULL DEFAULT 'Pending'
        )
    ''')

    # Create default admin account if it doesn't exist
    existing = conn.execute("SELECT * FROM users WHERE email = 'admin@ccs.com'").fetchone()
    if not existing:
        conn.execute('''
            INSERT INTO users (idnum, lastname, firstname, midname, email, course, level, address, password, sessions)
            VALUES ('0000', 'Admin', 'CCS', '', 'admin@ccs.com', 'N/A', 'N/A', 'N/A', 'admin123', 0)
        ''')

    conn.commit()
    conn.close()


# ─── Public Routes ────────────────────────────────────────────────────────────

@app.route('/')
def home():
    return render_template('landing.html')

@app.route('/community')
def community():
    return render_template('community.html')

@app.route('/about')
def about():
    return render_template('about.html')


# ─── Login ────────────────────────────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_home'))
        return redirect(url_for('student_dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        error    = None

        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        else:
            conn = get_db()
            user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
            conn.close()

            if user is None:
                error = 'No account found with that email.'
            elif user['password'] != password:
                error = 'Incorrect password.'
            else:
                session['user_id']    = user['id']
                session['user_name']  = user['firstname'] + ' ' + user['lastname']
                session['user_idnum'] = user['idnum']

                if email == 'admin@ccs.com':
                    session['role'] = 'admin'
                    return redirect(url_for('admin_home'))
                else:
                    session['role'] = 'student'
                    return redirect(url_for('student_dashboard'))

        return render_template('login.html', error=error)

    return render_template('login.html')


# ─── Register ─────────────────────────────────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('student_dashboard'))

    if request.method == 'POST':
        idnum     = request.form.get('idnum', '').strip()
        lastname  = request.form.get('lastname', '').strip()
        firstname = request.form.get('firstname', '').strip()
        midname   = request.form.get('midname', '').strip()
        email     = request.form.get('email', '').strip()
        course    = request.form.get('course', '').strip()
        level     = request.form.get('level', '').strip()
        address   = request.form.get('address', '').strip()
        password  = request.form.get('password', '').strip()
        confirm   = request.form.get('confirm', '').strip()
        error     = None

        if not idnum:
            error = 'ID Number is required.'
        elif not lastname:
            error = 'Last name is required.'
        elif not firstname:
            error = 'First name is required.'
        elif not email:
            error = 'Email is required.'
        elif not course:
            error = 'Please select a course.'
        elif not level:
            error = 'Please select a year level.'
        elif not address:
            error = 'Address is required.'
        elif not password:
            error = 'Password is required.'
        elif len(password) < 8:
            error = 'Password must be at least 8 characters.'
        elif password != confirm:
            error = 'Passwords do not match.'
        else:
            try:
                conn = get_db()
                conn.execute('''
                    INSERT INTO users (idnum, lastname, firstname, midname, email, course, level, address, password)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (idnum, lastname, firstname, midname, email, course, level, address, password))
                conn.commit()
                conn.close()
                return redirect(url_for('login') + '?registered=1')
            except sqlite3.IntegrityError:
                error = 'An account with that email or ID number already exists.'

        return render_template('register.html', error=error,
                               idnum=idnum, lastname=lastname, firstname=firstname,
                               midname=midname, email=email, course=course,
                               level=level, address=address)

    return render_template('register.html')


# ─── Student Dashboard ────────────────────────────────────────────────────────

@app.route('/dashboard')
def student_dashboard():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    return render_template('dashboard.html', name=session['user_name'])


# ─── Logout ───────────────────────────────────────────────────────────────────

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ─── ADMIN ROUTES ─────────────────────────────────────────────────────────────

def admin_required():
    return 'user_id' in session and session.get('role') == 'admin'


# Admin Home
@app.route('/admin')
def admin_home():
    if not admin_required():
        return redirect(url_for('login'))

    conn = get_db()
    total_students = conn.execute("SELECT COUNT(*) FROM users WHERE email != 'admin@ccs.com'").fetchone()[0]
    current_sitin  = conn.execute("SELECT COUNT(*) FROM sitin").fetchone()[0]
    total_sitin    = conn.execute("SELECT COUNT(*) FROM sitin_reports").fetchone()[0]
    course_counts  = conn.execute('''
        SELECT course, COUNT(*) as count FROM users
        WHERE email != 'admin@ccs.com' GROUP BY course
    ''').fetchall()
    announcements  = conn.execute('SELECT * FROM announcements ORDER BY id DESC').fetchall()
    conn.close()

    return render_template('admin/home.html',
                           total_students=total_students,
                           current_sitin=current_sitin,
                           total_sitin=total_sitin,
                           course_counts=course_counts,
                           announcements=announcements)


# Post Announcement
@app.route('/admin/announcement', methods=['POST'])
def post_announcement():
    if not admin_required():
        return redirect(url_for('login'))
    content = request.form.get('content', '').strip()
    if content:
        conn = get_db()
        conn.execute('INSERT INTO announcements (content) VALUES (?)', (content,))
        conn.commit()
        conn.close()
    return redirect(url_for('admin_home'))


# Admin Students
@app.route('/admin/students')
def admin_students():
    if not admin_required():
        return redirect(url_for('login'))
    conn = get_db()
    students = conn.execute("SELECT * FROM users WHERE email != 'admin@ccs.com'").fetchall()
    conn.close()
    return render_template('admin/students.html', students=students)


# Edit Student
@app.route('/admin/students/edit/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    if not admin_required():
        return redirect(url_for('login'))
    conn = get_db()
    student = conn.execute('SELECT * FROM users WHERE id = ?', (student_id,)).fetchone()

    if request.method == 'POST':
        idnum     = request.form.get('idnum', '').strip()
        lastname  = request.form.get('lastname', '').strip()
        firstname = request.form.get('firstname', '').strip()
        midname   = request.form.get('midname', '').strip()
        email     = request.form.get('email', '').strip()
        course    = request.form.get('course', '').strip()
        level     = request.form.get('level', '').strip()
        address   = request.form.get('address', '').strip()
        sessions  = request.form.get('sessions', 30)

        conn.execute('''
            UPDATE users SET idnum=?, lastname=?, firstname=?, midname=?,
            email=?, course=?, level=?, address=?, sessions=? WHERE id=?
        ''', (idnum, lastname, firstname, midname, email, course, level, address, sessions, student_id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_students'))

    conn.close()
    return render_template('admin/edit_student.html', student=student)


# Delete Student
@app.route('/admin/students/delete/<int:student_id>')
def delete_student(student_id):
    if not admin_required():
        return redirect(url_for('login'))
    conn = get_db()
    conn.execute('DELETE FROM users WHERE id = ?', (student_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_students'))


# Reset All Sessions
@app.route('/admin/students/reset_sessions')
def reset_sessions():
    if not admin_required():
        return redirect(url_for('login'))
    conn = get_db()
    conn.execute("UPDATE users SET sessions = 30 WHERE email != 'admin@ccs.com'")
    conn.commit()
    conn.close()
    return redirect(url_for('admin_students'))


# Admin Search
@app.route('/admin/search')
def admin_search():
    if not admin_required():
        return redirect(url_for('login'))
    query = request.args.get('q', '').strip()
    students = []
    if query:
        conn = get_db()
        students = conn.execute('''
            SELECT * FROM users WHERE
            idnum LIKE ? OR lastname LIKE ? OR firstname LIKE ?
        ''', (f'%{query}%', f'%{query}%', f'%{query}%')).fetchall()
        conn.close()
    return render_template('admin/search.html', students=students, query=query)


# Admin Sit-in
@app.route('/admin/sitin', methods=['GET', 'POST'])
def admin_sitin():
    if not admin_required():
        return redirect(url_for('login'))

    error = None
    success = None

    if request.method == 'POST':
        idnum   = request.form.get('idnum', '').strip()
        purpose = request.form.get('purpose', '').strip()
        lab     = request.form.get('lab', '').strip()

        conn = get_db()
        student = conn.execute('SELECT * FROM users WHERE idnum = ?', (idnum,)).fetchone()

        if not student:
            error = 'Student ID not found.'
        elif student['sessions'] <= 0:
            error = 'Student has no remaining sessions.'
        else:
            name = student['firstname'] + ' ' + student['lastname']
            conn.execute('''
                INSERT INTO sitin (idnum, name, purpose, lab, session)
                VALUES (?, ?, ?, ?, ?)
            ''', (idnum, name, purpose, lab, student['sessions']))
            conn.execute('UPDATE users SET sessions = sessions - 1 WHERE idnum = ?', (idnum,))
            conn.commit()
            success = f'{name} has been sat in successfully.'

        conn.close()

    return render_template('admin/sitin.html', error=error, success=success)


# Admin View Sit-in Records (active only)
@app.route('/admin/sitin/records')
def admin_sitin_records():
    if not admin_required():
        return redirect(url_for('login'))
    conn = get_db()
    records = conn.execute('SELECT * FROM sitin ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('admin/sitin_records.html', records=records)


# End Sit-in Session - moves to reports and deletes from sitin
@app.route('/admin/sitin/end/<int:record_id>')
def end_sitin(record_id):
    if not admin_required():
        return redirect(url_for('login'))

    conn = get_db()

    # Get the active sit-in record
    record = conn.execute('SELECT * FROM sitin WHERE id = ?', (record_id,)).fetchone()

    if record:
        # Copy it to sitin_reports
        conn.execute('''
            INSERT INTO sitin_reports (idnum, name, purpose, lab, session, date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (record['idnum'], record['name'], record['purpose'],
              record['lab'], record['session'], record['date']))

        # Delete from active sitin
        conn.execute('DELETE FROM sitin WHERE id = ?', (record_id,))
        conn.commit()

    conn.close()
    return redirect(url_for('admin_sitin_records'))


# Admin Sit-in Reports (completed only)
@app.route('/admin/reports')
def admin_reports():
    if not admin_required():
        return redirect(url_for('login'))
    conn = get_db()
    records = conn.execute('SELECT * FROM sitin_reports ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('admin/reports.html', records=records)


# Admin Feedback Reports
@app.route('/admin/feedback')
def admin_feedback():
    if not admin_required():
        return redirect(url_for('login'))
    return render_template('admin/feedback.html')


# Admin Reservation
@app.route('/admin/reservation')
def admin_reservation():
    if not admin_required():
        return redirect(url_for('login'))
    conn = get_db()
    reservations = conn.execute('SELECT * FROM reservations ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('admin/reservation.html', reservations=reservations)


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    app.run(debug=True)