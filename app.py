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

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ─── Database Setup ───────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(os.path.join(BASE_DIR, 'database.db'))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()

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
            sessions    INTEGER NOT NULL DEFAULT 30,
            photo       TEXT    DEFAULT NULL
        )
    ''')

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

    conn.execute('''
        CREATE TABLE IF NOT EXISTS announcements (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT    NOT NULL,
            date    TEXT    NOT NULL DEFAULT (DATE('now'))
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            idnum       TEXT    NOT NULL,
            name        TEXT    NOT NULL,
            lab         TEXT    NOT NULL,
            purpose     TEXT    NOT NULL DEFAULT '',
            date        TEXT    NOT NULL,
            time        TEXT    NOT NULL,
            status      TEXT    NOT NULL DEFAULT 'Pending'
        )
    ''')

    # Add columns for existing databases
    try:
        conn.execute('ALTER TABLE users ADD COLUMN photo TEXT DEFAULT NULL')
    except:
        pass

    try:
        conn.execute('ALTER TABLE reservations ADD COLUMN purpose TEXT DEFAULT ""')
    except:
        pass

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
        return redirect(url_for('student_home'))

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
                    return redirect(url_for('student_home'))

        return render_template('login.html', error=error)

    return render_template('login.html')


# ─── Register ─────────────────────────────────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('student_home'))

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


# ─── Logout ───────────────────────────────────────────────────────────────────

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ─── STUDENT ROUTES ───────────────────────────────────────────────────────────

def student_required():
    return 'user_id' in session and session.get('role') == 'student'


@app.route('/student')
def student_home():
    if not student_required():
        return redirect(url_for('login'))
    conn          = get_db()
    student       = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    announcements = conn.execute('SELECT * FROM announcements ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('student/home.html', student=student, announcements=announcements)


@app.route('/student/reservation', methods=['GET', 'POST'])
def student_reservation():
    if not student_required():
        return redirect(url_for('login'))

    error   = None
    success = None

    if request.method == 'POST':
        lab     = request.form.get('lab', '').strip()
        purpose = request.form.get('purpose', '').strip()
        date    = request.form.get('date', '').strip()
        time    = request.form.get('time', '').strip()

        if not lab:
            error = 'Please select a laboratory.'
        elif not purpose:
            error = 'Please select a purpose.'
        elif not date:
            error = 'Please select a date.'
        elif not time:
            error = 'Please select a time.'
        else:
            conn = get_db()
            conn.execute('''
                INSERT INTO reservations (idnum, name, lab, purpose, date, time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (session['user_idnum'], session['user_name'], lab, purpose, date, time))
            conn.commit()
            conn.close()
            success = 'Reservation submitted successfully!'

    conn         = get_db()
    reservations = conn.execute(
        'SELECT * FROM reservations WHERE idnum = ? ORDER BY id DESC',
        (session['user_idnum'],)
    ).fetchall()
    conn.close()

    return render_template('student/reservationStudent.html',
                           error=error, success=success,
                           reservations=reservations)


@app.route('/student/profile', methods=['GET', 'POST'])
def student_profile():
    if not student_required():
        return redirect(url_for('login'))

    conn    = get_db()
    student = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()

    error   = None
    success = None

    if request.method == 'POST':
        lastname         = request.form.get('lastname', '').strip()
        firstname        = request.form.get('firstname', '').strip()
        midname          = request.form.get('midname', '').strip()
        email            = request.form.get('email', '').strip()
        course           = request.form.get('course', '').strip()
        level            = request.form.get('level', '').strip()
        address          = request.form.get('address', '').strip()
        new_password     = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not lastname or not firstname or not email or not address:
            error = 'Please fill in all required fields.'
        elif new_password and len(new_password) < 8:
            error = 'New password must be at least 8 characters.'
        elif new_password and new_password != confirm_password:
            error = 'Passwords do not match.'
        else:
            password = new_password if new_password else student['password']
            photo    = student['photo']

            if 'photo' in request.files:
                file = request.files['photo']
                if file and file.filename != '' and allowed_file(file.filename):
                    ext      = file.filename.rsplit('.', 1)[1].lower()
                    filename = f'profile_{session["user_id"]}.{ext}'
                    file.save(os.path.join(UPLOAD_FOLDER, filename))
                    photo = filename

            try:
                conn = get_db()
                conn.execute('''
                    UPDATE users SET lastname=?, firstname=?, midname=?,
                    email=?, course=?, level=?, address=?, password=?, photo=?
                    WHERE id=?
                ''', (lastname, firstname, midname, email, course, level,
                      address, password, photo, session['user_id']))
                conn.commit()
                conn.close()
                session['user_name'] = firstname + ' ' + lastname
                success = 'Profile updated successfully!'
                conn    = get_db()
                student = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
                conn.close()
            except sqlite3.IntegrityError:
                error = 'That email is already used by another account.'

    return render_template('student/profile.html',
                           student=student, error=error, success=success)


# ─── ADMIN ROUTES ─────────────────────────────────────────────────────────────

def admin_required():
    return 'user_id' in session and session.get('role') == 'admin'


@app.route('/admin')
def admin_home():
    if not admin_required():
        return redirect(url_for('login'))
    conn           = get_db()
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


@app.route('/admin/announcement/delete/<int:announcement_id>')
def delete_announcement(announcement_id):
    if not admin_required():
        return redirect(url_for('login'))
    conn = get_db()
    conn.execute('DELETE FROM announcements WHERE id = ?', (announcement_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_home'))


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


@app.route('/admin/students')
def admin_students():
    if not admin_required():
        return redirect(url_for('login'))
    conn     = get_db()
    students = conn.execute("SELECT * FROM users WHERE email != 'admin@ccs.com'").fetchall()
    conn.close()
    return render_template('admin/students.html', students=students)


@app.route('/admin/students/edit/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    if not admin_required():
        return redirect(url_for('login'))
    conn    = get_db()
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


@app.route('/admin/students/delete/<int:student_id>')
def delete_student(student_id):
    if not admin_required():
        return redirect(url_for('login'))
    conn = get_db()
    conn.execute('DELETE FROM users WHERE id = ?', (student_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_students'))


@app.route('/admin/students/reset_sessions')
def reset_sessions():
    if not admin_required():
        return redirect(url_for('login'))
    conn = get_db()
    conn.execute("UPDATE users SET sessions = 30 WHERE email != 'admin@ccs.com'")
    conn.commit()
    conn.close()
    return redirect(url_for('admin_students'))


@app.route('/admin/search')
def admin_search():
    if not admin_required():
        return redirect(url_for('login'))
    query    = request.args.get('q', '').strip()
    students = []
    if query:
        conn     = get_db()
        students = conn.execute('''
            SELECT * FROM users WHERE
            idnum LIKE ? OR lastname LIKE ? OR firstname LIKE ?
        ''', (f'%{query}%', f'%{query}%', f'%{query}%')).fetchall()
        conn.close()
    return render_template('admin/search.html', students=students, query=query)


@app.route('/admin/sitin', methods=['GET', 'POST'])
def admin_sitin():
    if not admin_required():
        return redirect(url_for('login'))

    error   = None
    success = None

    if request.method == 'POST':
        idnum   = request.form.get('idnum', '').strip()
        purpose = request.form.get('purpose', '').strip()
        lab     = request.form.get('lab', '').strip()

        conn    = get_db()
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


@app.route('/admin/sitin/records')
def admin_sitin_records():
    if not admin_required():
        return redirect(url_for('login'))
    conn    = get_db()
    records = conn.execute('SELECT * FROM sitin ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('admin/sitin_records.html', records=records)


@app.route('/admin/sitin/end/<int:record_id>')
def end_sitin(record_id):
    if not admin_required():
        return redirect(url_for('login'))
    conn   = get_db()
    record = conn.execute('SELECT * FROM sitin WHERE id = ?', (record_id,)).fetchone()
    if record:
        conn.execute('''
            INSERT INTO sitin_reports (idnum, name, purpose, lab, session, date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (record['idnum'], record['name'], record['purpose'],
              record['lab'], record['session'], record['date']))
        conn.execute('DELETE FROM sitin WHERE id = ?', (record_id,))
        conn.commit()
    conn.close()
    return redirect(url_for('admin_sitin_records'))


@app.route('/admin/reports')
def admin_reports():
    if not admin_required():
        return redirect(url_for('login'))
    conn    = get_db()
    records = conn.execute('SELECT * FROM sitin_reports ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('admin/reports.html', records=records)


# Delete single sit-in report
@app.route('/admin/reports/delete/<int:record_id>')
def delete_sitin_report(record_id):
    if not admin_required():
        return redirect(url_for('login'))
    conn = get_db()
    conn.execute('DELETE FROM sitin_reports WHERE id = ?', (record_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_reports'))


# Clear all sit-in reports
@app.route('/admin/reports/clear')
def clear_sitin_reports():
    if not admin_required():
        return redirect(url_for('login'))
    conn = get_db()
    conn.execute('DELETE FROM sitin_reports')
    conn.commit()
    conn.close()
    return redirect(url_for('admin_reports'))


@app.route('/admin/feedback')
def admin_feedback():
    if not admin_required():
        return redirect(url_for('login'))
    return render_template('admin/feedback.html')


@app.route('/admin/reservation')
def admin_reservation():
    if not admin_required():
        return redirect(url_for('login'))
    conn         = get_db()
    reservations = conn.execute('SELECT * FROM reservations ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('admin/reservation.html', reservations=reservations)


# Approve reservation - also creates a sit-in record
@app.route('/admin/reservation/approve/<int:reservation_id>')
def approve_reservation(reservation_id):
    if not admin_required():
        return redirect(url_for('login'))

    conn        = get_db()
    reservation = conn.execute('SELECT * FROM reservations WHERE id = ?', (reservation_id,)).fetchone()

    if reservation:
        # Update reservation status
        conn.execute("UPDATE reservations SET status = 'Approved' WHERE id = ?", (reservation_id,))

        # Find the student to get their remaining sessions
        student = conn.execute('SELECT * FROM users WHERE idnum = ?', (reservation['idnum'],)).fetchone()

        if student and student['sessions'] > 0:
            # Create a sit-in record automatically
            conn.execute('''
                INSERT INTO sitin (idnum, name, purpose, lab, session, date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (reservation['idnum'], reservation['name'],
                  reservation['purpose'], reservation['lab'],
                  student['sessions'], reservation['date']))

            # Deduct one session from the student
            conn.execute('UPDATE users SET sessions = sessions - 1 WHERE idnum = ?',
                         (reservation['idnum'],))

        conn.commit()

    conn.close()
    return redirect(url_for('admin_reservation'))


# Reject reservation
@app.route('/admin/reservation/reject/<int:reservation_id>')
def reject_reservation(reservation_id):
    if not admin_required():
        return redirect(url_for('login'))
    conn = get_db()
    conn.execute("UPDATE reservations SET status = 'Rejected' WHERE id = ?", (reservation_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_reservation'))


# Delete single reservation
@app.route('/admin/reservation/delete/<int:reservation_id>')
def delete_reservation(reservation_id):
    if not admin_required():
        return redirect(url_for('login'))
    conn = get_db()
    conn.execute('DELETE FROM reservations WHERE id = ?', (reservation_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_reservation'))


# Clear all reservations
@app.route('/admin/reservation/clear')
def clear_reservations():
    if not admin_required():
        return redirect(url_for('login'))
    conn = get_db()
    conn.execute('DELETE FROM reservations')
    conn.commit()
    conn.close()
    return redirect(url_for('admin_reservation'))


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    app.run(debug=True)