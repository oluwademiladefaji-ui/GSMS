# GSMS Quick Reference Guide

## 🚀 Quick Start

### Start Server
```bash
python manage.py runserver
```

### Access System
```
Landing Page: http://127.0.0.1:8000/accounts/welcome/
Admin Login: http://127.0.0.1:8000/accounts/login/?role=admin
```

### Default Admin Credentials
```
Username: BUAdmin
Password: Admin
```

---

## 📋 Common Tasks

### 1. Approve a New User
```
1. Login as admin
2. Go to Dashboard → Pending Approvals
3. Click "Approve" on user
4. Copy the generated passcode
5. Share passcode with user via email
```

### 2. Add a Student (Direct)
```
1. Login as admin
2. Go to Students → Add Student
3. Fill form and submit
4. Student is immediately active
```

### 3. Allocate Course to Lecturer
```
1. Login as admin
2. Go to Programs → Course Allocation
3. Select lecturer
4. Select courses
5. Submit
```

### 4. Create Session/Semester
```
1. Login as admin
2. Go to Sessions → Add Session
3. Mark as current if needed
4. Go to Semesters → Add Semester
5. Link to session and mark as current
```

### 5. Upload Course Material (Lecturer)
```
1. Login as lecturer
2. Go to My Courses
3. Click on course
4. Click "Upload Material"
5. Select file and submit
```

### 6. Enter Student Scores (Lecturer)
```
1. Login as lecturer
2. Go to Dashboard → Enter Scores
3. Select course
4. Enter scores for each student
5. Submit
```

### 7. Register for Courses (Student)
```
1. Login as student
2. Go to Dashboard → Register Courses
3. Select courses
4. Submit registration
```

### 8. View Results (Student)
```
1. Login as student
2. Go to Dashboard → My Results
3. View GPA/CGPA and course grades
```

---

## 🔑 User Roles

### Admin
- **Login**: Username + Password
- **Access**: Full system control
- **Dashboard**: `/accounts/dashboard/admin/`

### Lecturer
- **Login**: Full Name + Passcode
- **Access**: Teaching functions
- **Dashboard**: `/accounts/dashboard/lecturer/`

### Student
- **Login**: Full Name + Passcode
- **Access**: Learning functions
- **Dashboard**: `/accounts/dashboard/student/`

---

## 🔗 Key URLs

### Public
- `/accounts/welcome/` - Landing page
- `/accounts/role-selection/` - Choose role
- `/accounts/login/` - Login page
- `/accounts/register/` - Signup page

### Admin
- `/accounts/dashboard/admin/` - Admin dashboard
- `/accounts/approvals/` - Pending approvals
- `/accounts/students/` - Student list
- `/accounts/lecturers/` - Lecturer list
- `/programs/` - Programs list
- `/programs/course/assign/` - Course allocation

### Lecturer
- `/accounts/dashboard/lecturer/` - Lecturer dashboard
- `/result/manage-score/` - Enter scores
- `/quiz/marking_list/` - Grade quizzes

### Student
- `/accounts/dashboard/student/` - Student dashboard
- `/programs/course/registration/` - Register courses
- `/result/grade/` - View results
- `/quiz/progress/` - Quiz progress

---

## 🛠️ Troubleshooting

### Issue: Can't login
**Solution**: 
- Admin: Use username "BUAdmin" and password "Admin"
- Others: Use EXACT full name (case-sensitive) and passcode

### Issue: No pending approvals showing
**Solution**: 
- Check if users have registered
- Verify approval_status is 'pending' in database

### Issue: Dashboard not loading
**Solution**:
- Check if user is approved (is_active=True)
- Verify role (is_student, is_lecturer, is_superuser)

### Issue: Static files not loading
**Solution**:
```bash
python manage.py collectstatic
```

### Issue: Database error
**Solution**:
```bash
python manage.py migrate
```

---

## 📞 Support

### Documentation
1. **TRANSFORMATION_COMPLETE.md** - Full completion report
2. **TRANSFORMATION_GUIDE.md** - Technical guide
3. **QUICK_START.md** - Setup instructions

### Commands
```bash
# Check system
python manage.py check

# Create admin
python manage.py createsuperuser

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Run server
python manage.py runserver
```

---

## ✅ Quick Checklist

### Before First Use
- [ ] Run migrations
- [ ] Create superuser (BUAdmin/Admin)
- [ ] Create at least one session
- [ ] Create at least one semester
- [ ] Create at least one program
- [ ] Create at least one course

### For Testing
- [ ] Register a test student
- [ ] Register a test lecturer
- [ ] Approve both users
- [ ] Allocate course to lecturer
- [ ] Student registers for course
- [ ] Lecturer uploads material
- [ ] Student accesses material
- [ ] Lecturer enters scores
- [ ] Student views results

---

**Quick Reference Version**: 1.0
**Last Updated**: 2026-03-25
