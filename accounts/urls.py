from django.urls import path, include

from .views import (
    profile,
    profile_single,
    admin_panel,
    admin_dashboard,
    lecturer_dashboard,
    student_dashboard,
    profile_update,
    change_password,
    LecturerFilterView,
    StudentListView,
    staff_add_view,
    edit_staff,
    delete_staff,
    student_add_view,
    edit_student,
    delete_student,
    edit_student_program,
    ParentAdd,
    validate_username,
    register,
    welcome,
    role_selection,
    login_view,
    custom_login,
    pending_approvals,
    approve_user,
    reject_user,
    render_lecturer_pdf_list,
    render_student_pdf_list,
)


urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    
    # Dashboard routes (NEW)
    path("dashboard/admin/", admin_dashboard, name="admin_dashboard"),
    path("dashboard/lecturer/", lecturer_dashboard, name="lecturer_dashboard"),
    path("dashboard/student/", student_dashboard, name="student_dashboard"),
    
    # Legacy admin panel (redirects to new dashboard)
    path("admin_panel/", admin_panel, name="admin_panel"),
    
    # Authentication
    path("welcome/", welcome, name="welcome"),
    path("role-selection/", role_selection, name="role_selection"),
    path("login/", login_view, name="login"),
    path("login-action/", custom_login, name="custom_login"),
    path("register/", register, name="register"),
    
    # Approval system
    path("approvals/", pending_approvals, name="pending_approvals"),
    path("approvals/<int:pk>/approve/", approve_user, name="approve_user"),
    path("approvals/<int:pk>/reject/", reject_user, name="reject_user"),
    
    # Profile
    path("profile/", profile, name="profile"),
    path("profile/<int:user_id>/detail/", profile_single, name="profile_single"),
    path("setting/", profile_update, name="edit_profile"),
    path("change_password/", change_password, name="change_password"),
    
    # Lecturers
    path("lecturers/", LecturerFilterView.as_view(), name="lecturer_list"),
    path("lecturer/add/", staff_add_view, name="add_lecturer"),
    path("staff/<int:pk>/edit/", edit_staff, name="staff_edit"),
    path("lecturers/<int:pk>/delete/", delete_staff, name="lecturer_delete"),
    path("create_lecturers_pdf_list/", render_lecturer_pdf_list, name="lecturer_list_pdf"),
    
    # Students
    path("students/", StudentListView.as_view(), name="student_list"),
    path("student/add/", student_add_view, name="add_student"),
    path("student/<int:pk>/edit/", edit_student, name="student_edit"),
    path("students/<int:pk>/delete/", delete_student, name="student_delete"),
    path("edit_student_program/<int:pk>/", edit_student_program, name="student_program_edit"),
    path("create_students_pdf_list/", render_student_pdf_list, name="student_list_pdf"),
    
    # Parents
    path("parents/add/", ParentAdd.as_view(), name="add_parent"),
    
    # AJAX
    path("ajax/validate-username/", validate_username, name="validate_username"),
]
