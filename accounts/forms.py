from django import forms
from django.db import transaction
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm
from django.utils.translation import gettext_lazy as _
from course.models import Program
from .models import User, Student, Parent, RELATION_SHIP, LEVEL, GENDERS


def fc(widget_type="text", extra=None):
    """Helper to build standard form-control attrs."""
    attrs = {"type": widget_type, "class": "form-control"}
    if extra:
        attrs.update(extra)
    return attrs


NIGERIAN_STATES = [
    ('', '-- Select State --'),
    ('Abia', 'Abia'), ('Adamawa', 'Adamawa'), ('Akwa Ibom', 'Akwa Ibom'),
    ('Anambra', 'Anambra'), ('Bauchi', 'Bauchi'), ('Bayelsa', 'Bayelsa'),
    ('Benue', 'Benue'), ('Borno', 'Borno'), ('Cross River', 'Cross River'),
    ('Delta', 'Delta'), ('Ebonyi', 'Ebonyi'), ('Edo', 'Edo'),
    ('Ekiti', 'Ekiti'), ('Enugu', 'Enugu'), ('FCT', 'FCT - Abuja'),
    ('Gombe', 'Gombe'), ('Imo', 'Imo'), ('Jigawa', 'Jigawa'),
    ('Kaduna', 'Kaduna'), ('Kano', 'Kano'), ('Katsina', 'Katsina'),
    ('Kebbi', 'Kebbi'), ('Kogi', 'Kogi'), ('Kwara', 'Kwara'),
    ('Lagos', 'Lagos'), ('Nasarawa', 'Nasarawa'), ('Niger', 'Niger'),
    ('Ogun', 'Ogun'), ('Ondo', 'Ondo'), ('Osun', 'Osun'),
    ('Oyo', 'Oyo'), ('Plateau', 'Plateau'), ('Rivers', 'Rivers'),
    ('Sokoto', 'Sokoto'), ('Taraba', 'Taraba'), ('Yobe', 'Yobe'),
    ('Zamfara', 'Zamfara'),
]

RELIGIONS = [
    ('', '-- Select --'),
    ('Christianity', 'Christianity'),
    ('Islam', 'Islam'),
    ('Others', 'Others'),
]


# ─── Signup Forms (no password, inactive until admin approves) ─────────────────

class StaffSignupForm(forms.Form):
    honorific = forms.ChoiceField(
        choices=[
            ('', '-- Select --'), ('Dr.', 'Dr.'), ('Prof.', 'Prof.'),
            ('Mr.', 'Mr.'), ('Mrs.', 'Mrs.'), ('Ms.', 'Ms.'),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Title / Honorific"), required=False,
    )
    first_name  = forms.CharField(max_length=50, widget=forms.TextInput(attrs=fc()), label=_("First Name"))
    last_name   = forms.CharField(max_length=50, widget=forms.TextInput(attrs=fc()), label=_("Last Name"))
    email       = forms.EmailField(widget=forms.TextInput(attrs=fc("email")), label=_("Email Address"))
    phone       = forms.CharField(max_length=30, widget=forms.TextInput(attrs=fc("tel")), label=_("Phone Number"))
    gender      = forms.ChoiceField(choices=GENDERS, widget=forms.Select(attrs={"class": "form-select"}), label=_("Gender"))
    department  = forms.CharField(max_length=100, widget=forms.TextInput(attrs=fc()), label=_("Department"), required=False)
    state_of_origin = forms.ChoiceField(
        choices=NIGERIAN_STATES,
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("State of Origin"), required=False,
    )

    @transaction.atomic()
    def save(self):
        data  = self.cleaned_data
        email = data["email"]
        # Use email as username to keep it unique
        user  = User(
            username        = email,
            email           = email,
            first_name      = data["first_name"],
            last_name       = data["last_name"],
            phone           = data["phone"],
            address         = data.get("state_of_origin", ""),
            gender          = data["gender"],
            honorific       = data.get("honorific", ""),
            is_lecturer     = True,
            is_active       = False,
            approval_status = 'pending',
        )
        user.set_unusable_password()
        user.save()
        return user


class StudentSignupForm(forms.Form):
    first_name      = forms.CharField(max_length=50, widget=forms.TextInput(attrs=fc()), label=_("First Name"))
    last_name       = forms.CharField(max_length=50, widget=forms.TextInput(attrs=fc()), label=_("Last Name"))
    email           = forms.EmailField(widget=forms.TextInput(attrs=fc("email")), label=_("Email Address"))
    matric_number   = forms.CharField(max_length=30, widget=forms.TextInput(attrs=fc()), label=_("Matriculation Number"))
    phone           = forms.CharField(max_length=30, widget=forms.TextInput(attrs=fc("tel")), label=_("Phone Number"))
    gender          = forms.ChoiceField(choices=GENDERS, widget=forms.Select(attrs={"class": "form-select"}), label=_("Gender"))
    level           = forms.ChoiceField(choices=LEVEL, widget=forms.Select(attrs={"class": "form-select"}), label=_("Current Level"))
    program         = forms.ModelChoiceField(
        queryset=Program.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Program / Department"),
    )
    state_of_origin = forms.ChoiceField(
        choices=NIGERIAN_STATES,
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("State of Origin"),
    )
    religion        = forms.ChoiceField(
        choices=RELIGIONS,
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Religion"), required=False,
    )

    @transaction.atomic()
    def save(self):
        data  = self.cleaned_data
        email = data["email"]
        user  = User(
            username        = email,
            email           = email,
            first_name      = data["first_name"],
            last_name       = data["last_name"],
            phone           = data["phone"],
            address         = data.get("state_of_origin", ""),
            gender          = data["gender"],
            matric_number   = data.get("matric_number", ""),
            is_student      = True,
            is_active       = False,
            approval_status = 'pending',
        )
        user.set_unusable_password()
        user.save()
        Student.objects.create(
            student = user,
            level   = data["level"],
            program = data["program"],
        )
        return user


# ─── Admin-added forms (still used by admin panel) ────────────────────────────

class StaffAddForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs=fc()), label=_("First Name"))
    last_name  = forms.CharField(max_length=30, widget=forms.TextInput(attrs=fc()), label=_("Last Name"))
    gender     = forms.ChoiceField(choices=GENDERS, widget=forms.Select(attrs={"class": "form-select"}))
    address    = forms.CharField(max_length=60, widget=forms.TextInput(attrs=fc()), label=_("Address"))
    phone      = forms.CharField(max_length=30, widget=forms.TextInput(attrs=fc()), label=_("Mobile No."))
    email      = forms.EmailField(widget=forms.TextInput(attrs=fc("email")), label=_("Email"))
    password1  = forms.CharField(max_length=30, widget=forms.TextInput(attrs=fc("password")), label=_("Password"))
    password2  = forms.CharField(max_length=30, widget=forms.TextInput(attrs=fc("password")), label=_("Confirm Password"))

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic()
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_lecturer = True
        user.is_active   = True
        user.first_name  = self.cleaned_data.get("first_name")
        user.last_name   = self.cleaned_data.get("last_name")
        user.phone       = self.cleaned_data.get("phone")
        user.address     = self.cleaned_data.get("address")
        user.email       = self.cleaned_data.get("email")
        if commit:
            user.save()
        return user


class StudentAddForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs=fc()), label=_("First Name"))
    last_name  = forms.CharField(max_length=30, widget=forms.TextInput(attrs=fc()), label=_("Last Name"))
    gender     = forms.ChoiceField(choices=GENDERS, widget=forms.Select(attrs={"class": "form-select"}))
    address    = forms.CharField(max_length=60, widget=forms.TextInput(attrs=fc()), label=_("Address"))
    phone      = forms.CharField(max_length=30, widget=forms.TextInput(attrs=fc()), label=_("Mobile No."))
    email      = forms.EmailField(widget=forms.TextInput(attrs=fc("email")), label=_("Email Address"))
    level      = forms.ChoiceField(choices=LEVEL, widget=forms.Select(attrs={"class": "form-select"}))
    program    = forms.ModelChoiceField(queryset=Program.objects.all(), widget=forms.Select(attrs={"class": "form-select"}), label=_("Program"))
    password1  = forms.CharField(max_length=30, widget=forms.TextInput(attrs=fc("password")), label=_("Password"))
    password2  = forms.CharField(max_length=30, widget=forms.TextInput(attrs=fc("password")), label=_("Confirm Password"))

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic()
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True
        user.is_active  = True
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name  = self.cleaned_data.get("last_name")
        user.gender     = self.cleaned_data.get("gender")
        user.address    = self.cleaned_data.get("address")
        user.phone      = self.cleaned_data.get("phone")
        user.email      = self.cleaned_data.get("email")
        if commit:
            user.save()
            Student.objects.create(
                student = user,
                level   = self.cleaned_data.get("level"),
                program = self.cleaned_data.get("program"),
            )
        return user


class ProfileUpdateForm(UserChangeForm):
    email      = forms.EmailField(widget=forms.TextInput(attrs=fc("email")), label=_("Email Address"))
    first_name = forms.CharField(widget=forms.TextInput(attrs=fc()), label=_("First Name"))
    last_name  = forms.CharField(widget=forms.TextInput(attrs=fc()), label=_("Last Name"))
    gender     = forms.ChoiceField(choices=GENDERS, widget=forms.Select(attrs={"class": "form-select"}))
    phone      = forms.CharField(widget=forms.TextInput(attrs=fc()), label=_("Phone No."))
    address    = forms.CharField(widget=forms.TextInput(attrs=fc()), label=_("Address / City"))

    class Meta:
        model  = User
        fields = ["first_name", "last_name", "gender", "email", "phone", "address", "picture"]


class ProgramUpdateForm(UserChangeForm):
    program = forms.ModelChoiceField(
        queryset=Program.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Program"),
    )

    class Meta:
        model  = Student
        fields = ["program"]


class EmailValidationOnForgotPassword(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data["email"]
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            self.add_error("email", "No user is registered with this email address.")
        return email


class ParentAddForm(UserCreationForm):
    first_name    = forms.CharField(max_length=30, widget=forms.TextInput(attrs=fc()), label=_("First Name"))
    last_name     = forms.CharField(max_length=30, widget=forms.TextInput(attrs=fc()), label=_("Last Name"))
    email         = forms.EmailField(widget=forms.TextInput(attrs=fc("email")), label=_("Email Address"))
    address       = forms.CharField(max_length=60, widget=forms.TextInput(attrs=fc()), label=_("Address"))
    phone         = forms.CharField(max_length=30, widget=forms.TextInput(attrs=fc()), label=_("Mobile No."))
    student       = forms.ModelChoiceField(queryset=Student.objects.all(), widget=forms.Select(attrs={"class": "form-select"}))
    relation_ship = forms.ChoiceField(choices=RELATION_SHIP, widget=forms.Select(attrs={"class": "form-select"}))
    password1     = forms.CharField(max_length=30, widget=forms.TextInput(attrs=fc("password")), label=_("Password"))
    password2     = forms.CharField(max_length=30, widget=forms.TextInput(attrs=fc("password")), label=_("Confirm Password"))

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic()
    def save(self):
        user = super().save(commit=False)
        user.is_parent  = True
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name  = self.cleaned_data.get("last_name")
        user.address    = self.cleaned_data.get("address")
        user.phone      = self.cleaned_data.get("phone")
        user.email      = self.cleaned_data.get("email")
        user.save()
        Parent.objects.create(
            user          = user,
            student       = self.cleaned_data.get("student"),
            relation_ship = self.cleaned_data.get("relation_ship"),
        )
        return user
