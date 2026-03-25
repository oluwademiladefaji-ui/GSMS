# GSMS System Transformation Guide

## 🎯 Transformation Overview

This document outlines the complete transformation of the General Studies Management System (GSMS) from a basic academic platform to a modern, admin-controlled, Moodle-inspired system.

---

## ✅ Phase 1: Completed Backend Changes

### 1.1 Database Schema Updates

#### New User Model Fields
```python
# accounts/models.py - User model additions
approval_status = CharField(choices=['pending', 'approved', 'rejected'])
approved_by = ForeignKey(User)
approved_at = DateTimeField()
```

#### New Core Model
```python
# core/models.py - ExamControl model
class ExamControl:
    session = ForeignKey(Session)
    semester = ForeignKey(Semester)
    is_active = BooleanField()
    activated_at = DateTimeField()
    activated_by = ForeignKey(User)
```

**Migration Status**: ✅ Created and Applied
- `accounts/migrations/0005_user_approval_status_user_approved_at_and_more.py`
- `core/migrations/0005_examcontrol.py`

### 1.2 Settings Configuration

#### Removed Apps
- ❌ `search` app (removed from INSTALLED_APPS)
- ❌ `payments` app (removed from URL routing)

#### New Settings
```python
# config/settings.py
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/accounts/welcome/"

# Admin credentials
ADMIN_USERNAME = "BUAdmin"
ADMIN_DEFAULT_PASSWORD = "Admin"
```

### 1.3 Authentication System Overhaul

#### New Login Flow
1. **Admin Login**: Username (BUAdmin) + Password (Admin)
2. **Lecturer/Student Login**: Full Name (case-sensitive) + Passcode

#### Approval Workflow
```
User Signup → Pending Status → Admin Approval → Passcode Generation → Email Notification
```

#### New Views Created
- `admin_dashboard()` - Full control center
- `lecturer_dashboard()` - Course management interface
- `student_dashboard()` - Learning interface
- `reject_user()` - Admin rejection handler

### 1.4 URL Structure Reorganization

#### New Dashboard Routes
```python
/accounts/dashboard/admin/      → Admin Dashboard
/accounts/dashboard/lecturer/   → Lecturer Dashboard
/accounts/dashboard/student/    → Student Dashboard
```

#### Authentication Routes
```python
/accounts/welcome/              → Public landing page
/accounts/role-selection/       → Role chooser
/accounts/login/                → Login page
/accounts/register/             → Signup page
/accounts/approvals/            → Admin approval queue
/accounts/approvals/<pk>/approve/ → Approve user
/accounts/approvals/<pk>/reject/  → Reject user
```

---

## 🚧 Phase 2: Required Frontend Implementation

### 2.1 Template Structure

Create the following template hierarchy:

```
templates/
├── base/
│   ├── base.html                    # Main base template
│   ├── dashboard_base.html          # Dashboard wrapper
│   └── public_base.html             # Public pages wrapper
│
├── registration/
│   ├── welcome.html                 # ✅ PUBLIC: Landing page
│   ├── role_selection.html          # ✅ PUBLIC: Role chooser
│   ├── login.html                   # ✅ PUBLIC: Login form
│   └── register.html                # ✅ PUBLIC: Signup form
│
├── accounts/
│   ├── admin_dashboard.html         # 🔴 NEW: Admin control center
│   ├── lecturer_dashboard.html      # 🔴 NEW: Lecturer interface
│   ├── student_dashboard.html       # 🔴 NEW: Student interface
│   ├── pending_approvals.html       # 🔴 UPDATE: Approval queue
│   ├── lecturer_list.html           # 🔴 UPDATE: Directory view
│   └── student_list.html            # 🔴 UPDATE: Directory view
│
├── course/
│   ├── course_allocation.html       # 🔴 UPDATE: Admin allocation
│   ├── course_materials.html        # 🔴 NEW: Material upload
│   └── course_detail.html           # 🔴 UPDATE: Enhanced view
│
├── quiz/
│   ├── quiz_create.html             # 🔴 UPDATE: Enhanced creation
│   ├── quiz_take.html               # ✅ Existing
│   └── exam_submission.html         # 🔴 NEW: Lecturer exam submit
│
└── result/
    ├── score_entry.html             # ✅ Existing
    ├── result_approval.html         # 🔴 NEW: Admin approval
    └── student_results.html         # ✅ Existing
```

### 2.2 UI/UX Requirements

#### Design System
- **Framework**: Bootstrap 5 (already installed via crispy-bootstrap5)
- **Style**: Minimal, clean, Moodle-inspired
- **Colors**: 
  - Primary: University brand color
  - Secondary: Neutral grays
  - Success: Green (#28a745)
  - Warning: Orange (#ffc107)
  - Danger: Red (#dc3545)

#### Layout Components

**Dashboard Sidebar Navigation**
```html
<!-- All dashboards should have -->
<nav class="sidebar">
  <div class="logo">Babcock University</div>
  <ul class="nav-menu">
    <!-- Role-specific menu items -->
  </ul>
</nav>
```

**Card-Based Content**
```html
<div class="dashboard-content">
  <div class="row">
    <div class="col-md-4">
      <div class="stat-card">
        <h3>{{ count }}</h3>
        <p>{{ label }}</p>
      </div>
    </div>
  </div>
</div>
```

### 2.3 Critical Templates to Create

#### 1. Welcome Page (`registration/welcome.html`)
**Requirements**:
- University branding/logo
- Hero section with tagline
- News & Events feed (6 latest items)
- Two CTA buttons: "Sign Up" and "Log In"
- Fully responsive
- No authentication required

**Key Elements**:
```html
<section class="hero">
  <h1>Welcome to Babcock University GSMS</h1>
  <p>General Studies Management System</p>
  <div class="cta-buttons">
    <a href="{% url 'role_selection' %}?mode=signup">Sign Up</a>
    <a href="{% url 'role_selection' %}?mode=login">Log In</a>
  </div>
</section>

<section class="news-events">
  {% for item in news_items %}
    <div class="news-card">
      <h3>{{ item.title }}</h3>
      <p>{{ item.summary }}</p>
      <span>{{ item.upload_time|date:"M d, Y" }}</span>
    </div>
  {% endfor %}
</section>
```

#### 2. Role Selection (`registration/role_selection.html`)
**Requirements**:
- Three clear options:
  - Admin Login
  - Lecturer Sign Up
  - Student Sign Up
- Visual cards for each role
- Redirect based on selection

**Key Elements**:
```html
<div class="role-selection">
  <h2>{% if mode == 'signup' %}Sign Up As{% else %}Log In As{% endif %}</h2>
  
  <div class="role-cards">
    <a href="{% url 'login' %}?role=admin" class="role-card admin">
      <i class="icon-admin"></i>
      <h3>Administrator</h3>
      <p>System Management</p>
    </a>
    
    <a href="{% if mode == 'signup' %}{% url 'register' %}?role=lecturer{% else %}{% url 'login' %}?role=lecturer{% endif %}" class="role-card lecturer">
      <i class="icon-lecturer"></i>
      <h3>Lecturer</h3>
      <p>Teaching & Assessment</p>
    </a>
    
    <a href="{% if mode == 'signup' %}{% url 'register' %}?role=student{% else %}{% url 'login' %}?role=student{% endif %}" class="role-card student">
      <i class="icon-student"></i>
      <h3>Student</h3>
      <p>Learning & Courses</p>
    </a>
  </div>
</div>
```

#### 3. Admin Dashboard (`accounts/admin_dashboard.html`)
**Requirements**:
- Statistics cards (students, lecturers, pending approvals)
- Quick actions panel
- Recent activity feed
- Enrollment distribution chart
- Exam control toggle
- Navigation to all admin functions

**Key Sections**:
```html
<!-- Statistics Row -->
<div class="stats-row">
  <div class="stat-card">
    <h3>{{ total_students }}</h3>
    <p>Total Students</p>
  </div>
  <div class="stat-card">
    <h3>{{ total_lecturers }}</h3>
    <p>Total Lecturers</p>
  </div>
  <div class="stat-card alert">
    <h3>{{ pending_approvals }}</h3>
    <p>Pending Approvals</p>
    <a href="{% url 'pending_approvals' %}">Review</a>
  </div>
</div>

<!-- Quick Actions -->
<div class="quick-actions">
  <a href="{% url 'pending_approvals' %}" class="action-btn">
    <i class="icon-users"></i> Approve Users
  </a>
  <a href="{% url 'course_allocation' %}" class="action-btn">
    <i class="icon-assign"></i> Allocate Courses
  </a>
  <a href="#exam-control" class="action-btn">
    <i class="icon-exam"></i> Exam Control
  </a>
  <a href="#results" class="action-btn">
    <i class="icon-results"></i> Release Results
  </a>
</div>

<!-- Activity Feed -->
<div class="activity-feed">
  <h3>Recent Activity</h3>
  {% for log in recent_logs %}
    <div class="activity-item">
      <span class="time">{{ log.created_at|timesince }} ago</span>
      <p>{{ log.message }}</p>
    </div>
  {% endfor %}
</div>
```

#### 4. Lecturer Dashboard (`accounts/lecturer_dashboard.html`)
**Requirements**:
- Allocated courses list
- Quick access to:
  - Upload materials
  - Create quiz/assignment
  - Enter scores
  - Submit exam (when active)
- Current semester info
- Student count per course

**Key Sections**:
```html
<div class="dashboard-header">
  <h1>Welcome, {{ user.honorific }} {{ user.get_full_name }}</h1>
  <p>{{ current_semester }} - {{ current_session }}</p>
</div>

<div class="courses-grid">
  {% for course in current_courses %}
    <div class="course-card">
      <h3>{{ course.code }}</h3>
      <h4>{{ course.title }}</h4>
      <p>{{ course.level }} - {{ course.credit }} Credits</p>
      
      <div class="course-actions">
        <a href="{% url 'course_detail' course.slug %}">View</a>
        <a href="{% url 'upload_file_view' course.slug %}">Upload Material</a>
        <a href="{% url 'quiz_create' course.slug %}">Create Quiz</a>
        <a href="{% url 'add_score_for' course.id %}">Enter Scores</a>
      </div>
    </div>
  {% endfor %}
</div>
```

#### 5. Student Dashboard (`accounts/student_dashboard.html`)
**Requirements**:
- Registered courses
- Quick access to:
  - Course materials
  - Pending quizzes/assignments
  - View results
- GPA display
- Course registration link

**Key Sections**:
```html
<div class="student-info">
  <h1>Welcome, {{ user.get_full_name }}</h1>
  <p>{{ student.level }} - {{ student.program }}</p>
  <p>Matric: {{ user.matric_number }}</p>
</div>

<div class="gpa-card">
  {% if latest_results %}
    <h3>Latest GPA: {{ latest_results.0.gpa }}</h3>
    <p>CGPA: {{ latest_results.0.cgpa }}</p>
  {% endif %}
</div>

<div class="courses-section">
  <h2>My Courses</h2>
  {% for taken_course in current_courses %}
    <div class="course-item">
      <h4>{{ taken_course.course.code }} - {{ taken_course.course.title }}</h4>
      <div class="course-links">
        <a href="{% url 'course_detail' taken_course.course.slug %}">Materials</a>
        <a href="{% url 'quiz_index' taken_course.course.slug %}">Quizzes</a>
      </div>
    </div>
  {% endfor %}
</div>
```

---

## 🔧 Phase 3: Feature Implementation

### 3.1 Exam Control System

#### Admin Interface
Create view in `core/views.py`:
```python
@login_required
@admin_required
def exam_control(request):
    """Admin activates/deactivates exam mode"""
    current_session = Session.objects.filter(is_current_session=True).first()
    current_semester = Semester.objects.filter(is_current_semester=True).first()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        exam_control, created = ExamControl.objects.get_or_create(
            session=current_session,
            semester=current_semester
        )
        
        if action == 'activate':
            exam_control.is_active = True
            exam_control.activated_by = request.user
            exam_control.activated_at = timezone.now()
            exam_control.save()
            messages.success(request, "Exam mode activated!")
        elif action == 'deactivate':
            exam_control.is_active = False
            exam_control.save()
            messages.info(request, "Exam mode deactivated.")
        
        return redirect('admin_dashboard')
    
    # GET request - show current status
    ...
```

#### Lecturer Exam Submission
When exam mode is active, lecturers can submit exams through a special interface.

### 3.2 Course Allocation Enhancement

Update `course/views.py` to add admin-only allocation interface with:
- Lecturer selection dropdown
- Course multi-select with filters (by program, level)
- Visual confirmation of allocations
- Ability to remove allocations

### 3.3 Result Approval System

Create new view in `result/views.py`:
```python
@login_required
@admin_required
def result_approval(request):
    """Admin reviews and approves results before release to students"""
    pending_results = Result.objects.filter(approved=False)
    
    if request.method == 'POST':
        result_ids = request.POST.getlist('result_ids')
        Result.objects.filter(id__in=result_ids).update(
            approved=True,
            approved_by=request.user,
            approved_at=timezone.now()
        )
        messages.success(request, f"{len(result_ids)} results approved!")
        return redirect('result_approval')
    
    context = {
        'pending_results': pending_results,
        'title': 'Result Approval'
    }
    return render(request, 'result/result_approval.html', context)
```

Add field to Result model:
```python
# result/models.py
class Result(models.Model):
    # ... existing fields ...
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    approved_at = models.DateTimeField(null=True, blank=True)
```

### 3.4 Material Upload Enhancement

Update `course/views.py` upload views to:
- Support drag-and-drop
- Show upload progress
- Organize by type (PDF, Video, Document)
- Add preview functionality

---

## 📱 Phase 4: Responsive Design

### Mobile-First Approach

#### Breakpoints
```css
/* Mobile: < 768px */
/* Tablet: 768px - 1024px */
/* Desktop: > 1024px */
```

#### Key Responsive Elements
1. **Navigation**: Hamburger menu on mobile
2. **Dashboard Cards**: Stack vertically on mobile
3. **Tables**: Horizontal scroll on mobile
4. **Forms**: Full-width inputs on mobile

---

## 🎨 Phase 5: UI Components Library

### Reusable Components

#### 1. Stat Card
```html
<div class="stat-card {% if alert %}alert{% endif %}">
  <div class="stat-icon">
    <i class="{{ icon_class }}"></i>
  </div>
  <div class="stat-content">
    <h3>{{ value }}</h3>
    <p>{{ label }}</p>
    {% if action_url %}
      <a href="{{ action_url }}" class="stat-action">{{ action_text }}</a>
    {% endif %}
  </div>
</div>
```

#### 2. Action Button
```html
<a href="{{ url }}" class="action-btn {{ variant }}">
  <i class="{{ icon }}"></i>
  <span>{{ text }}</span>
</a>
```

#### 3. Course Card
```html
<div class="course-card">
  <div class="course-header">
    <span class="course-code">{{ course.code }}</span>
    <span class="course-level">{{ course.level }}</span>
  </div>
  <h4 class="course-title">{{ course.title }}</h4>
  <p class="course-info">{{ course.credit }} Credits • {{ course.semester }}</p>
  <div class="course-actions">
    {% block course_actions %}{% endblock %}
  </div>
</div>
```

---

## ✅ Implementation Checklist

### Backend (Completed)
- [x] User model updated with approval fields
- [x] ExamControl model created
- [x] Migrations created and applied
- [x] Authentication flow updated
- [x] Dashboard views created
- [x] URL routing reorganized
- [x] Signup forms updated
- [x] Approval system implemented

### Frontend (To Do)
- [ ] Create base templates
- [ ] Implement welcome page
- [ ] Implement role selection page
- [ ] Implement login page
- [ ] Implement register page
- [ ] Create admin dashboard
- [ ] Create lecturer dashboard
- [ ] Create student dashboard
- [ ] Update pending approvals page
- [ ] Enhance course allocation interface
- [ ] Create exam control interface
- [ ] Create result approval interface
- [ ] Implement responsive design
- [ ] Add loading states
- [ ] Add error handling UI

### Features (To Do)
- [ ] Exam control system
- [ ] Result approval workflow
- [ ] Enhanced material upload
- [ ] Drag-and-drop file upload
- [ ] Email notifications
- [ ] Activity logging UI
- [ ] Analytics charts
- [ ] Search functionality
- [ ] Bulk operations

### Testing (To Do)
- [ ] Test approval workflow
- [ ] Test all dashboard views
- [ ] Test exam control
- [ ] Test course allocation
- [ ] Test result approval
- [ ] Mobile responsiveness testing
- [ ] Cross-browser testing
- [ ] Load testing

---

## 🚀 Next Steps

1. **Create Base Templates** (Priority: HIGH)
   - `base.html`
   - `dashboard_base.html`
   - `public_base.html`

2. **Implement Public Pages** (Priority: HIGH)
   - Welcome page
   - Role selection
   - Login/Register

3. **Build Dashboards** (Priority: HIGH)
   - Admin dashboard
   - Lecturer dashboard
   - Student dashboard

4. **Add Advanced Features** (Priority: MEDIUM)
   - Exam control
   - Result approval
   - Enhanced uploads

5. **Polish & Test** (Priority: MEDIUM)
   - Responsive design
   - Error handling
   - Performance optimization

---

## 📞 Support & Documentation

### Key Files Modified
- `config/settings.py` - App configuration
- `config/urls.py` - URL routing
- `accounts/models.py` - User model
- `accounts/views.py` - Authentication & dashboards
- `accounts/urls.py` - Account routes
- `accounts/forms.py` - Signup forms
- `core/models.py` - ExamControl model

### New Migrations
- `accounts/migrations/0005_*.py`
- `core/migrations/0005_*.py`

### Database Changes
Run migrations:
```bash
python manage.py migrate
```

### Create Admin User
```bash
python manage.py createsuperuser
# Username: BUAdmin
# Password: Admin
```

---

**Transformation Status**: 40% Complete (Backend Done, Frontend Pending)
**Last Updated**: 2026-03-25
