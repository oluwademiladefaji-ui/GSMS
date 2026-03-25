# Quick Start Guide - Django GSMS

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

---

## 📦 Installation Steps

### 1. Activate Virtual Environment (if not already active)
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Apply Migrations (if needed)
```bash
python manage.py migrate
```

### 4. Create Superuser (Admin Account)
```bash
python manage.py createsuperuser
```
Follow the prompts to create your admin account.

### 5. Compile Translation Files (Optional)
```bash
python manage.py compilemessages
```

### 6. Collect Static Files (for production)
```bash
python manage.py collectstatic --noinput
```

---

## 🏃 Running the Application

### Development Server
```bash
python manage.py runserver
```

The application will be available at: **http://127.0.0.1:8000/**

### Access Points
- **Main Site**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Welcome Page**: http://127.0.0.1:8000/accounts/welcome/

---

## 👥 User Roles and Access

### 1. **Admin/Superuser**
- Full system access
- User management and approval
- System configuration
- Access via: `/admin/` or standard login

### 2. **Lecturer/Staff**
- Course management
- Quiz creation
- Score entry
- Student results viewing
- Login: Full Name (case-sensitive) + Passcode

### 3. **Student**
- Course registration
- Quiz taking
- Results viewing
- Profile management
- Login: Full Name (case-sensitive) + Passcode

### 4. **Parent**
- View linked student information
- Login: Username + Password

---

## 🔑 Initial Setup Workflow

### Step 1: Create Admin Account
```bash
python manage.py createsuperuser
```

### Step 2: Login to Admin Panel
1. Go to http://127.0.0.1:8000/admin/
2. Login with superuser credentials

### Step 3: Create Academic Structure
1. **Create Session** (Academic Year)
   - Navigate to: Core → Sessions
   - Add new session (e.g., "2025/2026")
   - Mark as current session

2. **Create Semester**
   - Navigate to: Core → Semesters
   - Add semester (First/Second)
   - Link to session
   - Mark as current semester

3. **Create Programs** (Departments)
   - Navigate to: Course → Programs
   - Add programs (e.g., "Computer Science", "Engineering")

4. **Create Courses**
   - Navigate to: Course → Courses
   - Add courses with:
     - Code, Title, Credit
     - Program, Level, Year, Semester

### Step 4: Add Users

#### Option A: Admin Creates Users
1. **Add Lecturers**
   - Navigate to: Accounts → Add Lecturer
   - Fill in details and set password
   - User is immediately active

2. **Add Students**
   - Navigate to: Accounts → Add Student
   - Fill in details, select program and level
   - User is immediately active

#### Option B: Self-Registration (Requires Approval)
1. Users visit: http://127.0.0.1:8000/accounts/register/
2. Fill registration form
3. Account created but inactive
4. Admin approves from: http://127.0.0.1:8000/accounts/approvals/
5. System generates passcode
6. User can now login with Full Name + Passcode

### Step 5: Allocate Courses to Lecturers
1. Navigate to: Programs → Course Allocation
2. Select lecturer
3. Select courses to allocate
4. Save

### Step 6: Students Register for Courses
1. Student logs in
2. Navigate to: Course Registration
3. Select courses for current semester
4. Submit registration

---

## 📚 Common Tasks

### Add News/Events
1. Login as admin or lecturer
2. Navigate to home page
3. Click "Add Post"
4. Fill in title, summary, and type (News/Event)

### Create Quiz
1. Login as lecturer
2. Navigate to course detail page
3. Click "Add Quiz"
4. Fill quiz details
5. Add questions (Multiple Choice or Essay)

### Enter Student Scores
1. Login as lecturer
2. Navigate to: Result → Manage Score
3. Select course
4. Enter scores for each student:
   - Assignment
   - Mid Exam
   - Quiz
   - Attendance
   - Final Exam
5. System auto-calculates: Total, Grade, Point, GPA, CGPA

### View Results (Student)
1. Login as student
2. Navigate to: Result → Grade Results
3. View all semester results with GPA/CGPA

### Generate PDF Reports
- **Student List**: Accounts → Students → Create PDF
- **Lecturer List**: Accounts → Lecturers → Create PDF
- **Result Sheet**: Result → Print Result Sheet
- **Registration Form**: Result → Registration Form

---

## 🌍 Multi-Language Support

### Available Languages
- English (en)
- French (fr)
- Spanish (es)
- Russian (ru)

### Switch Language
1. Use language selector in the interface
2. Or visit: `/i18n/setlang/`

### Add/Update Translations
1. Edit translation files in `locale/[lang]/LC_MESSAGES/django.po`
2. Compile messages:
   ```bash
   python manage.py compilemessages
   ```

---

## 🔧 Troubleshooting

### Issue: "No module named 'X'"
**Solution**: Install missing package
```bash
pip install -r requirements.txt
```

### Issue: "Table doesn't exist"
**Solution**: Run migrations
```bash
python manage.py migrate
```

### Issue: Static files not loading
**Solution**: Collect static files
```bash
python manage.py collectstatic
```

### Issue: Can't login
**Solution**: 
- For Admin: Use username + password
- For Student/Lecturer: Use EXACT full name (case-sensitive) + passcode
- Ensure account is active (check admin panel)

### Issue: No current semester/session
**Solution**: 
1. Go to admin panel
2. Create session and mark as current
3. Create semester, link to session, mark as current

---

## 📊 Database Management

### View Database (SQLite)
```bash
python manage.py dbshell
```

### Create Database Backup
```bash
# SQLite
copy db.sqlite3 db_backup_YYYYMMDD.sqlite3

# PostgreSQL
pg_dump dbname > backup.sql
```

### Reset Database (Development Only)
```bash
# Delete database
del db.sqlite3

# Delete migrations (except __init__.py)
# Then recreate
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

---

## 🎯 Testing Checklist

- [ ] Admin can login
- [ ] Create session and semester
- [ ] Create program
- [ ] Create course
- [ ] Add lecturer
- [ ] Add student
- [ ] Allocate course to lecturer
- [ ] Student registers for course
- [ ] Lecturer creates quiz
- [ ] Student takes quiz
- [ ] Lecturer enters scores
- [ ] Student views results
- [ ] Generate PDF reports
- [ ] Upload course materials
- [ ] Post news/events
- [ ] Search functionality

---

## 📞 Support

### Check System Status
```bash
python manage.py check
```

### View Logs
Check console output for errors and warnings.

### Common Commands
```bash
# Check migrations
python manage.py showmigrations

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver

# Run on specific port
python manage.py runserver 8080

# Run on all interfaces
python manage.py runserver 0.0.0.0:8000
```

---

## 🎓 Next Steps

1. ✅ Complete initial setup
2. ✅ Add test data
3. ✅ Test all features
4. ✅ Customize templates (optional)
5. ✅ Configure email settings
6. ✅ Set up payment gateways (if needed)
7. ✅ Deploy to production (see FIXES_AND_IMPROVEMENTS.md)

---

**Happy Learning! 🚀**
