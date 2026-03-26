from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template, render_to_string
from django.utils.decorators import method_decorator
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.views.generic import CreateView
from django_filters.views import FilterView
from xhtml2pdf import pisa

from accounts.decorators import admin_required
from accounts.filters import LecturerFilter, StudentFilter
from accounts.forms import (
    ParentAddForm,
    ProfileUpdateForm,
    ProgramUpdateForm,
    StaffAddForm,
    StaffSignupForm,
    StudentAddForm,
    StudentSignupForm,
)
from django.contrib.auth import authenticate, login as auth_login

from accounts.models import Parent, Student, User
from core.models import Semester, Session, NewsAndEvents, ActivityLog
from course.models import Course, Program
from result.models import TakenCourse

# ########################################################
# Utility Functions
# ########################################################


def render_to_pdf(template_name, context):
    """Render a given template to PDF format."""
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'filename="profile.pdf"'
    template = render_to_string(template_name, context)
    pdf = pisa.CreatePDF(template, dest=response)
    if pdf.err:
        return HttpResponse("We had some problems generating the PDF")
    return response


# ########################################################
# Authentication and Registration
# ########################################################


def welcome(request):
    """Universal landing page with branding and News/Events - PUBLIC ACCESS."""
    # Redirect authenticated users to their dashboard
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect("admin_dashboard")
        elif request.user.is_lecturer:
            return redirect("lecturer_dashboard")
        elif request.user.is_student:
            return redirect("student_dashboard")
        return redirect("home")
    
    news_items = NewsAndEvents.objects.all().order_by("-updated_date")[:6]
    context = {
        "news_items": news_items,
        "title": "Welcome to Babcock University GSMS",
    }
    return render(request, "registration/welcome_apple.html", context)


def role_selection(request):
    """Role selection page - choose between Admin Login, Lecturer Signup, Student Signup."""
    if request.user.is_authenticated:
        return redirect("welcome")
    
    mode = request.GET.get("mode", "signup")  # signup or login
    context = {
        "mode": mode,
        "title": "Select Your Role",
    }
    return render(request, "registration/role_selection.html", context)


def login_view(request):
    """Dedicated login page — infers role from the URL path."""
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect("admin_dashboard")
        elif request.user.is_lecturer:
            return redirect("lecturer_dashboard")
        elif request.user.is_student:
            return redirect("student_dashboard")
        return redirect("welcome")

    # Infer role from URL path (admin-login / student-login / lecturer-login)
    path = request.path
    if "admin" in path:
        role = "admin"
    elif "lecturer" in path:
        role = "lecturer"
    else:
        role = "student"

    context = {
        "role": role,
        "login_error": request.session.pop("login_error", None),
    }
    return render(request, "registration/login_apple.html", context)


def custom_login(request):
    """
    Unified POST login handler:
    - Admin: Username + Password (direct DB check)
    - Student/Lecturer: Full Name (case-sensitive) + Passcode
    """
    from django.urls import reverse

    if request.method != "POST":
        return redirect("welcome")

    role = request.POST.get("role", "").strip()

    # ── ADMIN LOGIN ──────────────────────────────────────────────
    if role == "admin":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        # Try Django's authenticate first (handles hashed passwords)
        user = authenticate(request, username=username, password=password)
        if user is None:
            # Fallback: direct DB check (handles edge-cases with auth backends)
            try:
                candidate = User.objects.get(username=username, is_superuser=True)
                if candidate.check_password(password):
                    user = candidate
            except User.DoesNotExist:
                pass

        if user and user.is_superuser and user.is_active:
            auth_login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(request, f"Welcome back, {user.first_name or user.username}! You are logged in as Administrator.")
            return redirect("admin_dashboard")

        messages.error(request, "❌ Invalid admin credentials. Check your username and password.")
        return redirect(reverse("admin_login"))

    # ── STUDENT / LECTURER LOGIN ──────────────────────────────────
    full_name = request.POST.get("full_name", "").strip()
    passcode  = request.POST.get("passcode", "").strip()

    if not full_name or not passcode:
        messages.error(request, "Please fill in both your Full Name and Passcode.")
        login_url = reverse("student_login") if role == "student" else reverse("lecturer_login")
        return redirect(login_url)

    if role == "student":
        qs = User.objects.filter(is_student=True, is_active=True, approval_status="approved")
        fail_url = reverse("student_login")
    elif role == "lecturer":
        qs = User.objects.filter(is_lecturer=True, is_active=True, approval_status="approved")
        fail_url = reverse("lecturer_login")
    else:
        messages.error(request, "Invalid role. Please start again.")
        return redirect("welcome")

    user = None
    for u in qs:
        if u.get_full_name == full_name and u.passcode == passcode:
            user = u
            break

    if user:
        auth_login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(request, f"🎉 Welcome, {user.get_full_name}!")
        if user.is_student:
            return redirect("student_dashboard")
        elif user.is_lecturer:
            return redirect("lecturer_dashboard")
        return redirect("welcome")

    messages.error(
        request,
        "❌ Login failed. Your Full Name and Passcode are both case-sensitive. "
        "Check the email you received from GSMS Admin."
    )
    return redirect(fail_url)


def validate_username(request):
    username = request.GET.get("username", None)
    data = {"is_taken": User.objects.filter(username__iexact=username).exists()}
    return JsonResponse(data)


def register(request):
    """Registration view for Lecturer and Student signup with approval workflow."""
    if request.user.is_authenticated:
        return redirect("welcome")
    
    if request.method == "POST":
        role = request.POST.get("role", "student")
        
        if role == "student":
            form = StudentSignupForm(request.POST)
            staff_form = StaffSignupForm()
            student_form = form
        else:
            form = StaffSignupForm(request.POST)
            student_form = StudentSignupForm()
            staff_form = form
        
        if form.is_valid():
            user = form.save()
            messages.success(
                request, 
                f"Registration successful! Your account is pending admin approval. "
                f"You will receive a passcode via email once approved."
            )
            return redirect("welcome")
        else:
            messages.error(request, "Please correct the errors below.")
            return render(request, "registration/register.html", {
                "student_form": student_form,
                "staff_form": staff_form,
                "active_tab": role,
                "title": "Sign Up",
            })
    else:
        role = request.GET.get("role", "student")
        student_form = StudentSignupForm()
        staff_form = StaffSignupForm()
    
    return render(request, "registration/register_apple.html", {
        "student_form": student_form,
        "staff_form": staff_form,
        "active_tab": role,
        "title": "Sign Up",
    })

@login_required
@admin_required
def pending_approvals(request):
    """Admin view to see all pending user registrations."""
    pending_users = User.objects.filter(
        approval_status='pending',
        is_superuser=False
    ).order_by('-date_joined')
    
    context = {
        "pending_users": pending_users,
        "title": "Pending Approvals",
        "total_pending": pending_users.count(),
    }
    return render(request, "accounts/pending_approvals.html", context)


@login_required
@admin_required
def approve_user(request, pk):
    """Admin approves a pending user and generates & emails their passcode."""
    user = get_object_or_404(User, pk=pk)

    if user.approval_status != 'pending':
        messages.warning(request, f"User {user.get_full_name} has already been processed.")
        return redirect("pending_approvals")

    # Generate unique 8-character passcode (mixed case + digits)
    from django.utils.crypto import get_random_string
    passcode = get_random_string(8, allowed_chars='ABCDEFGHJKLMNPQRSTUVWXYZ23456789')

    user.passcode        = passcode
    user.approval_status = 'approved'
    user.is_active       = True
    user.approved_by     = request.user
    user.approved_at     = timezone.now()
    user.save()

    # Send passcode via email
    role_label = "Student" if user.is_student else "Lecturer"
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        subject = "GSMS Account Approved – Your Login Passcode"
        body = (
            f"Dear {user.get_full_name},\n\n"
            f"Your {role_label} account on the Babcock University General Studies Management System "
            f"(GSMS) has been approved.\n\n"
            f"Your Login Details:\n"
            f"  Full Name  : {user.get_full_name}\n"
            f"  Passcode   : {passcode}\n\n"
            f"To log in:\n"
            f"1. Visit the GSMS portal and click 'Log In to Dashboard'.\n"
            f"2. Select your role ({role_label}).\n"
            f"3. Enter your Full Name exactly as registered and your Passcode.\n\n"
            f"Note: Both your name and passcode are CASE-SENSITIVE.\n\n"
            f"If you have questions, contact the GSMS admin.\n\n"
            f"Babcock University – General Studies Office"
        )
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)
        email_note = f"Passcode generated: <strong>{passcode}</strong> (Emailed to {user.email})."
    except Exception:
        email_note = f"Email could not be sent. Passcode: <strong>{passcode}</strong> — share manually."

    messages.success(
        request,
        f"✅ {user.get_full_name} approved! {email_note}"
    )
    return redirect("pending_approvals")


@login_required
@admin_required
def reject_user(request, pk):
    """Admin rejects a pending user registration."""
    user = get_object_or_404(User, pk=pk)
    
    if user.approval_status != 'pending':
        messages.warning(request, f"User {user.get_full_name} has already been processed.")
        return redirect("pending_approvals")
    
    user.approval_status = 'rejected'
    user.is_active = False
    user.save()
    
    # TODO: Send rejection email
    # send_rejection_email(user)
    
    messages.info(request, f"User {user.get_full_name} has been rejected.")
    return redirect("pending_approvals")


# ########################################################
# Profile Views
# ########################################################


@login_required
def profile(request):
    """Show profile of the current user."""
    current_session = Session.objects.filter(is_current_session=True).first()
    current_semester = Semester.objects.filter(
        is_current_semester=True, session=current_session
    ).first()

    context = {
        "title": request.user.get_full_name,
        "current_session": current_session,
        "current_semester": current_semester,
    }

    if request.user.is_lecturer:
        courses = Course.objects.filter(
            allocated_course__lecturer__pk=request.user.id, semester=current_semester
        )
        context["courses"] = courses
        return render(request, "accounts/profile.html", context)

    if request.user.is_student:
        student = get_object_or_404(Student, student__pk=request.user.id)
        parent = Parent.objects.filter(student=student).first()
        courses = TakenCourse.objects.filter(
            student__student__id=request.user.id, course__level=student.level
        )
        context.update(
            {
                "parent": parent,
                "courses": courses,
                "level": student.level,
            }
        )
        return render(request, "accounts/profile.html", context)

    # For superuser or other staff
    staff = User.objects.filter(is_lecturer=True)
    context["staff"] = staff
    return render(request, "accounts/profile.html", context)


@login_required
@admin_required
def profile_single(request, user_id):
    """Show profile of any selected user."""
    if request.user.id == user_id:
        return redirect("profile")

    current_session = Session.objects.filter(is_current_session=True).first()
    current_semester = Semester.objects.filter(
        is_current_semester=True, session=current_session
    ).first()
    user = get_object_or_404(User, pk=user_id)

    context = {
        "title": user.get_full_name,
        "user": user,
        "current_session": current_session,
        "current_semester": current_semester,
    }

    if user.is_lecturer:
        courses = Course.objects.filter(
            allocated_course__lecturer__pk=user_id, semester=current_semester
        )
        context.update(
            {
                "user_type": "Lecturer",
                "courses": courses,
            }
        )
    elif user.is_student:
        student = get_object_or_404(Student, student__pk=user_id)
        courses = TakenCourse.objects.filter(
            student__student__id=user_id, course__level=student.level
        )
        context.update(
            {
                "user_type": "Student",
                "courses": courses,
                "student": student,
            }
        )
    else:
        context["user_type"] = "Superuser"

    if request.GET.get("download_pdf"):
        return render_to_pdf("pdf/profile_single.html", context)

    return render(request, "accounts/profile_single.html", context)


@login_required
@admin_required
def admin_panel(request):
    """Legacy admin panel - redirect to new dashboard."""
    return redirect("admin_dashboard")


# ########################################################
# Dashboard Views (NEW)
# ########################################################


@login_required
@admin_required
def admin_dashboard(request):
    """Main Admin Dashboard – Full Control Center."""
    from django.db.models import Count

    total_students = User.objects.filter(is_student=True, is_active=True).count()
    total_lecturers = User.objects.filter(is_lecturer=True, is_active=True).count()
    pending_count = User.objects.filter(approval_status='pending').count()

    current_session = Session.objects.filter(is_current_session=True).first()
    current_semester = Semester.objects.filter(is_current_semester=True).first()

    recent_logs = ActivityLog.objects.all().order_by("-created_at")[:10]

    enrollment_data = Course.objects.annotate(
        student_count=Count('taken_courses')
    ).order_by('-student_count')[:5]

    context = {
        "title": "Admin Dashboard",
        "total_students": total_students,
        "total_lecturers": total_lecturers,
        "pending_count": pending_count,
        "current_session": current_session,
        "current_semester": current_semester,
        "recent_logs": recent_logs,
        "enrollment_data": enrollment_data,
    }

    return render(request, "accounts/admin_dashboard_apple.html", context)


@login_required
def lecturer_dashboard(request):
    """
    Lecturer Dashboard
    - View allocated courses
    - Upload materials
    - Create assessments
    - Enter scores
    """
    if not request.user.is_lecturer and not request.user.is_superuser:
        messages.error(request, "Access denied. Lecturers only.")
        return redirect("home")
    
    from course.models import Course, CourseAllocation
    from core.models import Semester, Session
    
    current_session = Session.objects.filter(is_current_session=True).first()
    current_semester = Semester.objects.filter(is_current_semester=True).first()
    
    # Get allocated courses
    allocated_courses = Course.objects.filter(
        allocated_course__lecturer=request.user
    ).distinct()
    
    if current_semester:
        current_courses = allocated_courses.filter(semester=current_semester.semester)
    else:
        current_courses = allocated_courses
    
    context = {
        "title": "Lecturer Dashboard",
        "current_session": current_session,
        "current_semester": current_semester,
        "allocated_courses": allocated_courses,
        "current_courses": current_courses,
        "total_courses": allocated_courses.count(),
    }
    
    return render(request, "accounts/lecturer_dashboard.html", context)


@login_required
def student_dashboard(request):
    """
    Student Dashboard
    - View registered courses
    - Access materials
    - Take assessments
    - View results
    """
    if not request.user.is_student and not request.user.is_superuser:
        messages.error(request, "Access denied. Students only.")
        return redirect("home")
    
    from accounts.models import Student
    from result.models import TakenCourse, Result
    from core.models import Semester, Session
    
    current_session = Session.objects.filter(is_current_session=True).first()
    current_semester = Semester.objects.filter(is_current_semester=True).first()
    
    try:
        student = Student.objects.get(student=request.user)
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found. Please contact admin.")
        return redirect("home")
    
    # Get registered courses
    registered_courses = TakenCourse.objects.filter(student=student)
    
    if current_semester:
        current_courses = registered_courses.filter(
            course__semester=current_semester.semester
        )
    else:
        current_courses = registered_courses
    
    # Get latest results
    latest_results = Result.objects.filter(student=student).order_by('-id')[:3]
    
    context = {
        "title": "Student Dashboard",
        "student": student,
        "current_session": current_session,
        "current_semester": current_semester,
        "registered_courses": registered_courses,
        "current_courses": current_courses,
        "latest_results": latest_results,
        "total_courses": registered_courses.count(),
    }
    
    return render(request, "accounts/student_dashboard.html", context)


# ########################################################
# Settings Views
# ########################################################


@login_required
def profile_update(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect("profile")
        messages.error(request, "Please correct the error(s) below.")
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, "setting/profile_info_change.html", {"form": form})


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect("profile")
        messages.error(request, "Please correct the error(s) below.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "setting/password_change.html", {"form": form})


# ########################################################
# Staff (Lecturer) Views
# ########################################################


@login_required
@admin_required
def staff_add_view(request):
    if request.method == "POST":
        form = StaffAddForm(request.POST)
        if form.is_valid():
            lecturer = form.save()
            full_name = lecturer.get_full_name
            email = lecturer.email
            messages.success(
                request,
                f"Account for lecturer {full_name} has been created. "
                f"An email with account credentials will be sent to {email} within a minute.",
            )
            return redirect("lecturer_list")
    else:
        form = StaffAddForm()
    return render(
        request, "accounts/add_staff.html", {"title": "Add Lecturer", "form": form}
    )


@login_required
@admin_required
def edit_staff(request, pk):
    lecturer = get_object_or_404(User, is_lecturer=True, pk=pk)
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=lecturer)
        if form.is_valid():
            form.save()
            full_name = lecturer.get_full_name
            messages.success(request, f"Lecturer {full_name} has been updated.")
            return redirect("lecturer_list")
        messages.error(request, "Please correct the error below.")
    else:
        form = ProfileUpdateForm(instance=lecturer)
    return render(
        request, "accounts/edit_lecturer.html", {"title": "Edit Lecturer", "form": form}
    )


@method_decorator([login_required, admin_required], name="dispatch")
class LecturerFilterView(FilterView):
    filterset_class = LecturerFilter
    queryset = User.objects.filter(is_lecturer=True)
    template_name = "accounts/lecturer_list.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Lecturers"
        return context


@login_required
@admin_required
def render_lecturer_pdf_list(request):
    lecturers = User.objects.filter(is_lecturer=True)
    template_path = "pdf/lecturer_list.html"
    context = {"lecturers": lecturers}
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'filename="lecturers_list.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse(f"We had some errors <pre>{html}</pre>")
    return response


@login_required
@admin_required
def delete_staff(request, pk):
    lecturer = get_object_or_404(User, is_lecturer=True, pk=pk)
    full_name = lecturer.get_full_name
    lecturer.delete()
    messages.success(request, f"Lecturer {full_name} has been deleted.")
    return redirect("lecturer_list")


# ########################################################
# Student Views
# ########################################################


@login_required
@admin_required
def student_add_view(request):
    if request.method == "POST":
        form = StudentAddForm(request.POST)
        if form.is_valid():
            student = form.save()
            full_name = student.get_full_name
            email = student.email
            messages.success(
                request,
                f"Account for {full_name} has been created. "
                f"An email with account credentials will be sent to {email} within a minute.",
            )
            return redirect("student_list")
        messages.error(request, "Correct the error(s) below.")
    else:
        form = StudentAddForm()
    return render(
        request, "accounts/add_student.html", {"title": "Add Student", "form": form}
    )


@login_required
@admin_required
def edit_student(request, pk):
    student_user = get_object_or_404(User, is_student=True, pk=pk)
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=student_user)
        if form.is_valid():
            form.save()
            full_name = student_user.get_full_name
            messages.success(request, f"Student {full_name} has been updated.")
            return redirect("student_list")
        messages.error(request, "Please correct the error below.")
    else:
        form = ProfileUpdateForm(instance=student_user)
    return render(
        request, "accounts/edit_student.html", {"title": "Edit Student", "form": form}
    )


@method_decorator([login_required, admin_required], name="dispatch")
class StudentListView(FilterView):
    queryset = Student.objects.all()
    filterset_class = StudentFilter
    template_name = "accounts/student_list.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Students"
        return context


@login_required
@admin_required
def render_student_pdf_list(request):
    students = Student.objects.all()
    template_path = "pdf/student_list.html"
    context = {"students": students}
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'filename="students_list.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse(f"We had some errors <pre>{html}</pre>")
    return response


@login_required
@admin_required
def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    full_name = student.student.get_full_name
    student.delete()
    messages.success(request, f"Student {full_name} has been deleted.")
    return redirect("student_list")


@login_required
@admin_required
def edit_student_program(request, pk):
    student = get_object_or_404(Student, student_id=pk)
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = ProgramUpdateForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            full_name = user.get_full_name
            messages.success(request, f"{full_name}'s program has been updated.")
            return redirect("profile_single", user_id=pk)
        messages.error(request, "Please correct the error(s) below.")
    else:
        form = ProgramUpdateForm(instance=student)
    return render(
        request,
        "accounts/edit_student_program.html",
        {"title": "Edit Program", "form": form, "student": student},
    )


# ########################################################
# Parent Views
# ########################################################


@method_decorator([login_required, admin_required], name="dispatch")
class ParentAdd(CreateView):
    model = Parent
    form_class = ParentAddForm
    template_name = "accounts/parent_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Parent added successfully.")
        return super().form_valid(form)
