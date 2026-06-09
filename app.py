import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import re
import os
from datetime import datetime



app = Flask(__name__)
app.secret_key = 'resume_screening_2026_mysql'

# MySQL Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'mysql80'
app.config['MYSQL_DB'] = 'resume_screening'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

def validate_candidate(form_data):
    """Enhanced validation for registration"""
    errors = []
    name = form_data.get('name', '').strip()
    email = form_data.get('email', '').strip().lower()
    phone = form_data.get('phone', '').strip()
    age = form_data.get('age', '')
    education = form_data.get('education', '').strip()
    password = form_data.get('password', '')

    # Name validation
    if not name or len(name) < 2 or len(name) > 50:
        errors.append('Name must be 2-50 characters')

    # Email validation
    if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
        errors.append('Invalid email format')

    # Phone validation
    if not re.match(r'^\d{10}$', phone):
        errors.append('Phone must be 10 digits only')

    # Age validation
    try:
        age_int = int(age)
        if age_int < 18 or age_int > 65:
            errors.append('Age must be 18-65')
    except:
        errors.append('Invalid age')

    # Education validation
    if not education or len(education) < 2:
        errors.append('Education required')

    # Password validation
    if len(password) < 8:
        errors.append('Password must be 8+ characters')
    elif not re.search(r'[A-Z]', password):
        errors.append('Password needs 1 uppercase letter')
    elif not re.search(r'\d', password):
        errors.append('Password needs 1 number')
    elif not re.search(r'[!@#$%^&*]', password):
        errors.append('Password needs 1 special character')

    return errors

@app.route('/')
def index():
    """HOME PAGE"""

    try:
        cur = mysql.connection.cursor()

        # ✅ Get latest active jobs
        cur.execute("""
            SELECT j.*, 
                   DATE_FORMAT(j.created_at, '%d %b %Y') as formatted_date
            FROM jobs j
            WHERE j.is_active = 1
            ORDER BY j.created_at DESC
        """)
        jobs = cur.fetchall()

        # ✅ Total candidates
        cur.execute("SELECT COUNT(*) as total FROM candidates")
        total = cur.fetchone()['total']

        candidate = None

        # ✅ If logged in
        if 'candidate_id' in session:
            cur.execute(
                "SELECT * FROM candidates WHERE id = %s LIMIT 1",
                (session['candidate_id'],)
            )
            candidate = cur.fetchone()

        cur.close()

        return render_template(
            'index.html',
            jobs=jobs,                 # ✅ SEND JOBS
            candidate=candidate,
            is_logged_in='candidate_id' in session,
            total_candidates=total
        )

    except Exception as e:
        print(f"❌ Home Error: {e}")

        return render_template(
            'index.html',
            jobs=[],
            is_logged_in=False,
            total_candidates=0
        )
    
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print("📋 FORM:", dict(request.form))
        errors = validate_candidate(request.form)
        if errors:
            for error in errors:
                flash(error, 'error')
        else:
            try:
                cur = mysql.connection.cursor()
                email = request.form['email'].lower().strip()
                
                # Check duplicate
                cur.execute("SELECT id FROM candidates WHERE email = %s", (email,))
                existing = cur.fetchone()
                if existing:
                    flash('❌ Email already registered!', 'error')
                    cur.close()
                else:
                    # Register
                    cur.execute(""" 
                        INSERT INTO candidates (name, email, phone, age, education, password_hash) 
                        VALUES (%s, %s, %s, %s, %s, %s) 
                    """, (
                        request.form['name'].strip(), 
                        email, 
                        request.form['phone'].strip(), 
                        int(request.form['age']), 
                        request.form['education'].strip(), 
                        generate_password_hash(request.form['password'])
                    ))
                    mysql.connection.commit()
                    candidate_id = cur.lastrowid
                    
                    # ✅ AUTO-LOGIN & REDIRECT TO HOME
                    session['candidate_id'] = candidate_id
                    session['candidate_name'] = request.form['name'].strip()
                    session['candidate_email'] = email
                    cur.close()
                    flash(f'✅ Welcome {request.form["name"]}! Account created!', 'success')
                    return redirect(url_for('index'))  # 👈 HOME PAGE
            except Exception as e:
                print(f"❌ Error: {e}")
                flash(f'❌ Registration failed: {str(e)}', 'error')
                if 'cur' in locals():
                    cur.close()
    
    # Total users
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) as total FROM candidates")
        total = cur.fetchone()['total']
        cur.close()
    except:
        total = 0
    else:
        total = 0
        
    return render_template('register.html', total_users=total)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].lower().strip()
        password = request.form['password']
        print(f"🔍 Login: {email}")
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id, name, email, password_hash FROM candidates WHERE email = %s LIMIT 1", (email,))
            candidate = cur.fetchone()
            cur.close()
            print(f"📊 Found: {candidate}")
            
            if candidate and check_password_hash(candidate['password_hash'], password):
                # ✅ LOGIN SUCCESS → HOME PAGE
                session['candidate_id'] = candidate['id']
                session['candidate_name'] = candidate['name']
                session['candidate_email'] = candidate['email']
                flash('✅ Welcome back!', 'success')
                return redirect(url_for('index'))  # 👈 HOME PAGE
            else:
                flash('❌ Invalid email/password!', 'error')
        except Exception as e:
            print(f"❌ Login Error: {e}")
            flash('❌ Login failed!', 'error')
    return render_template('login.html')

@app.route('/jobs')
def jobs():
    """Jobs page - accessible to everyone"""
    try:
        cur = mysql.connection.cursor()
        
        # ✅ Get ALL active jobs for the jobs page
        cur.execute("""
            SELECT j.*, 
                   DATE_FORMAT(j.created_at, '%d %b %Y') as formatted_date
            FROM jobs j
            WHERE j.is_active = 1
            ORDER BY j.created_at DESC
        """)
        jobs_list = cur.fetchall()
        cur.close()
        
        if 'candidate_id' in session:  # Logged in user
            return render_template('jobs.html', 
                                 is_logged_in=True, 
                                 jobs=jobs_list)  # ✅ PASS JOBS
        else:  # Guest user
            return render_template('jobs.html', 
                                 is_logged_in=False, 
                                 jobs=jobs_list)  # ✅ PASS JOBS
    except Exception as e:
        print(f"❌ Jobs Page Error: {e}")
        if 'candidate_id' in session:
            return render_template('jobs.html', is_logged_in=True, jobs=[])
        else:
            return render_template('jobs.html', is_logged_in=False, jobs=[])

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin_email = request.form['admin_email'].lower().strip()
        admin_password = request.form['admin_password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM admin_users WHERE admin_email = %s AND admin_password = %s", (admin_email, admin_password))
        admin = cur.fetchone()
        cur.close()
        
        if admin:
            session['is_admin'] = True
            session['admin_id'] = admin['id']
            session['admin_name'] = admin['admin_name']
            flash(f'✅ Welcome Admin {admin["admin_name"]}!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('❌ Invalid admin credentials!', 'error')
    return render_template('admin_login.html')

@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        flash('Admin access required!', 'error')
        return redirect(url_for('admin_login'))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) as total FROM candidates")
    stats = cur.fetchone()
    cur.execute("SELECT * FROM candidates ORDER BY id DESC LIMIT 10")
    recent_candidates = cur.fetchall()
    cur.close()
    
    return render_template('admin_dashboard.html', total_candidates=stats['total'], recent_candidates=recent_candidates)

@app.route('/admin-logout')
def admin_logout():
    session.clear()
    flash('👋 Admin logged out!', 'success')
    return redirect(url_for('index'))

@app.route('/admin-candidates')
def admin_candidates():
    """Admin view - ALL candidates"""
    if not session.get('is_admin'):
        flash('Admin access required!', 'error')
        return redirect(url_for('admin_login'))
    
    try:
        cur = mysql.connection.cursor()
        cur.execute(""" 
            SELECT c.*, DATE_FORMAT(c.created_at, '%d %b %Y %H:%i') as formatted_date 
            FROM candidates c ORDER BY c.id DESC 
        """)
        all_candidates = cur.fetchall()
        total = len(all_candidates)
        cur.close()
        return render_template('admin_candidates.html', candidates=all_candidates, total=total)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/post-job', methods=['GET', 'POST'])
def post_job():
    if not session.get('is_admin'):
        flash('Admin access required!', 'error')
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        print(f"📋 FORM DATA: {dict(request.form)}")
        company_name = request.form['company_name'].strip()
        job_title = request.form['job_title'].strip()
        skills = request.form['skills'].strip()
        experience = request.form['experience']
        description = request.form['job_description'].strip()
        
        try:
            cur = mysql.connection.cursor()
            cur.execute(""" 
                INSERT INTO jobs (company_name, job_title, skills_required, experience_required, job_description, created_by, is_active, created_at) 
                VALUES (%s, %s, %s, %s, %s, %s, 1, NOW()) 
            """, (
                company_name, 
                job_title, 
                skills, 
                experience, 
                description, 
                session['admin_id']
            ))
            mysql.connection.commit()
            job_id = cur.lastrowid
            cur.close()
            print(f"✅ JOB CREATED: ID {job_id}")
            flash(f'✅ Job "{job_title}" posted! ID: {job_id}', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            mysql.connection.rollback()
            print(f"❌ ERROR: {e}")
            flash(f'❌ Error: {str(e)}', 'error')
            if 'cur' in locals():
                cur.close()
    
    return render_template('post_job.html')

@app.route('/admin/jobs')
def admin_jobs():
    """✅ FIXED - View ALL Jobs/Posts"""
    if not session.get('is_admin'):
        flash('Admin access required!', 'error')
        return redirect(url_for('admin_login'))
    
    try:
        cur = mysql.connection.cursor()
        
        # ✅ Get ALL jobs (even if no jobs exist)
        cur.execute(""" 
            SELECT j.*, 
                   COALESCE(a.admin_name, 'Unknown') as created_by_name,
                   DATE_FORMAT(COALESCE(j.created_at, NOW()), '%d %b %Y %H:%i') as formatted_date,
                   DATE_FORMAT(COALESCE(j.created_at, NOW()), '%d/%m/%Y') as short_date
            FROM jobs j 
            LEFT JOIN admin_users a ON j.created_by = a.id 
            ORDER BY j.id DESC 
        """)
        all_jobs = cur.fetchall()
        
        # ✅ Total count (including inactive)
        cur.execute("SELECT COUNT(*) as total_jobs FROM jobs")
        total_jobs_result = cur.fetchone()
        total_jobs = total_jobs_result['total_jobs'] if total_jobs_result else 0
        
        # ✅ Active jobs count
        cur.execute("SELECT COUNT(*) as active_jobs FROM jobs WHERE is_active = 1")
        active_jobs_result = cur.fetchone()
        active_jobs = active_jobs_result['active_jobs'] if active_jobs_result else 0
        
        cur.close()
        
        print(f"✅ LOADED: {len(all_jobs)} total jobs | {active_jobs} active")
        return render_template('admin_jobs.html', 
                             jobs=all_jobs, 
                             total_jobs=total_jobs,
                             active_jobs=active_jobs)
    except Exception as e:
        print(f"❌ JOBS ERROR: {e}")
        flash(f'Error: {str(e)}', 'error')
        return render_template('admin_jobs.html', jobs=[], total_jobs=0, active_jobs=0)
    
@app.route('/apply/<int:job_id>', methods=['GET', 'POST'])
def apply_job(job_id):
    """Job Application Page"""
    
    # Check if candidate is logged in
    if 'candidate_id' not in session:
        flash('❌ Please login to apply for jobs!', 'error')
        return redirect(url_for('login'))
    
    # Get job details
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT * FROM jobs
            WHERE id = %s AND is_active = 1
        """, (job_id,))
        job = cur.fetchone()
        cur.close()
        
        if not job:
            flash('❌ Job not found or not active!', 'error')
            return redirect(url_for('jobs'))
            
    except Exception as e:
        print(f"❌ Job Details Error: {e}")
        flash('❌ Error loading job details!', 'error')
        return redirect(url_for('jobs'))
    
    # Handle POST request (form submission)
    if request.method == 'POST':
        print("📋 Application Form:", dict(request.form))
        
        # Get form data
        applicant_name = request.form.get('name', '').strip()
        applicant_email = request.form.get('email', '').strip().lower()
        applicant_phone = request.form.get('phone', '').strip()
        applicant_resume = request.files.get('resume', None)
        
        # Validation
        errors = []
        if not applicant_name or len(applicant_name) < 2:
            errors.append('Name is required (2+ characters)')
        
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', applicant_email):
            errors.append('Invalid email format')
        
        if not re.match(r'^\d{10}$', applicant_phone):
            errors.append('Phone must be 10 digits')
        
        if not applicant_resume or applicant_resume.filename == '':
            errors.append('Resume file is required')
        else:
            # Validate file type
            allowed_extensions = {'pdf', 'doc', 'docx'}
            ext = applicant_resume.filename.rsplit('.', 1)[-1].lower()
            if ext not in allowed_extensions:
                errors.append('Only PDF, DOC, DOCX files allowed')
        
        if errors:
            for error in errors:
                flash(error, 'error')
        else:
            try:
                # Save resume to server
                resume_filename = None
                if applicant_resume:
                    ext = applicant_resume.filename.rsplit('.', 1)[-1].lower()
                    resume_filename = f"resume_{session['candidate_id']}_{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
                    
                    # Create uploads directory if not exists
                    upload_folder = 'uploads'
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder)
                    
                    resume_path = os.path.join(upload_folder, resume_filename)
                    applicant_resume.save(resume_path)
                    print(f"✅ Resume saved: {resume_path}")
                
                # Insert application into database
                cur = mysql.connection.cursor()
                cur.execute("""
                    INSERT INTO applications (candidate_id, job_id, name, email, phone, resume_filename, applied_at)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """, (
                    session['candidate_id'],
                    job_id,
                    applicant_name,
                    applicant_email,
                    applicant_phone,
                    resume_filename
                ))
                mysql.connection.commit()
                application_id = cur.lastrowid
                cur.close()
                
                flash(f'✅ Application submitted successfully! Application ID: {application_id}', 'success')
                return redirect(url_for('index'))
                
            except Exception as e:
                print(f"❌ Application Error: {e}")
                import traceback
                traceback.print_exc()
                mysql.connection.rollback()
                flash(f'❌ Failed to submit application: {str(e)}', 'error')
                if 'cur' in locals():
                    cur.close()
    
    # ✅ GET request - Render the form (THIS WAS MISSING!)
    candidate = session.get('candidate_name', '')
    candidate_email = session.get('candidate_email', '')
    
    return render_template(
        'apply_job.html',
        job=job,
        candidate_name=candidate,
        candidate_email=candidate_email,
        is_logged_in=True
    )
    
if __name__ == '__main__':
    print("🚀 ResumeScreen AI - Home Page After Login!")
    print("🏠 Home: http://localhost:5000/")
    print("📝 Register: http://localhost:5000/register")
    print("🔐 Login: http://localhost:5000/login")
    print("👨‍💼 Admin Jobs: http://localhost:5000/admin/jobs")
    app.run(debug=True, port=5000)