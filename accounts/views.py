"""
Django views for accounts app.
Backend redesigned for Django: auth, registration, verification, contact, FAQ, password, reports.
"""
import random
import base64
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from .models import User
from exams.models import StudentTestInfo, Teacher
from .forms import (
    RegisterForm,
    LoginForm,
    ChangePasswordForm,
    LostPasswordForm,
    NewPasswordForm,
    ContactForm,
)

try:
    from deepface import DeepFace
except ImportError:
    DeepFace = None

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None
    np = None

# Placeholder base64 image when user does not capture photo
PLACEHOLDER_IMAGE_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


def generate_otp(length=5):
    """Generate numeric OTP."""
    return "".join(str(random.randint(0, 9)) for _ in range(length))


# ---------------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------------

@require_GET
def index(request):
    """Home page."""
    return render(request, "index.html")


@require_http_methods(["GET", "POST"])
def register_view(request):
    """User registration: form -> OTP email -> verify_email page."""
    if request.user.is_authenticated:
        if request.user.user_type == "student":
            return redirect("student_index")
        return redirect("professor_index")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            imgdata = (data.get("image_hidden") or "").strip()
            if not imgdata or len(imgdata) < 100:
                imgdata = ""

            # Store in session for OTP step
            request.session["tempName"] = data["name"]
            request.session["tempEmail"] = data["email"]
            request.session["tempPassword"] = data["password"]
            request.session["tempUT"] = data["user_type"]
            request.session["tempImage"] = imgdata
            sesOTP = generate_otp()
            request.session["tempOTP"] = sesOTP

            try:
                send_mail(
                    "MyProctor.ai - OTP Verification",
                    f"Your OTP verification code is {sesOTP}.",
                    settings.DEFAULT_FROM_EMAIL,
                    [data["email"]],
                    fail_silently=False,
                )
                request.session["show_temp_otp"] = False
                messages.info(request, "OTP sent to your email. Enter it below to complete registration.")
            except Exception as e:
                request.session["show_temp_otp"] = True
                messages.warning(request, "Could not send email. Use the OTP shown on the next page.")

            request.session.modified = True
            request.session.save()
            return redirect("verify_email")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


@require_http_methods(["GET", "POST"])
def verify_email_view(request):
    """OTP verification after registration; create user and log in on success."""
    if "tempOTP" not in request.session:
        messages.warning(request, "Registration session expired. Please register again.")
        return redirect("register")

    reg_email = request.session.get("tempEmail", "")
    show_otp = request.session.get("show_temp_otp", False)
    otp_to_show = request.session.get("tempOTP") if show_otp else None
    context = {"registration_email": reg_email, "otp": otp_to_show}

    if request.method == "POST":
        theOTP = (request.POST.get("eotp") or "").strip()
        if theOTP != request.session.get("tempOTP"):
            context["error"] = "OTP is incorrect."
            return render(request, "verifyEmail.html", context)

        dbImgdata = (request.session.get("tempImage") or "").strip()
        if not dbImgdata or len(dbImgdata) < 100:
            dbImgdata = PLACEHOLDER_IMAGE_B64

        try:
            user = User.objects.create_user(
                email=request.session["tempEmail"],
                password=request.session["tempPassword"],
                name=request.session["tempName"],
                user_type=request.session["tempUT"],
                user_image=dbImgdata,
                user_login=0,
            )
        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}. Please try again.")
            return redirect("register")

        for key in ["tempName", "tempEmail", "tempPassword", "tempUT", "tempImage", "tempOTP", "show_temp_otp"]:
            request.session.pop(key, None)

        login(request, user)
        messages.success(request, "Registration complete. You are logged in.")

        if user.user_type == "student":
            return redirect("student_index")
        return redirect("professor_index")

    return render(request, "verifyEmail.html", context)


@require_http_methods(["GET", "POST"])
def login_view(request):
    """Login with email, password, user type; optional face verification."""
    if request.user.is_authenticated:
        if request.user.user_type == "student":
            return redirect("student_index")
        return redirect("professor_index")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            email = data["email"]
            password = data["password"]
            user_type = data["user_type"]
            imgdata1 = (data.get("image_hidden") or "").strip()

            try:
                user = User.objects.get(email=email, user_type=user_type)
            except User.DoesNotExist:
                messages.error(request, "Invalid email, user type, or password.")
                return render(request, "login.html", {"form": form})

            if not user.check_password(password):
                messages.error(request, "Password is incorrect.")
                return render(request, "login.html", {"form": form})

            verified = True
            if DeepFace and user.user_image and imgdata1 and cv2 is not None and np is not None:
                try:
                    nparr1 = np.frombuffer(base64.b64decode(imgdata1), np.uint8)
                    nparr2 = np.frombuffer(base64.b64decode(user.user_image), np.uint8)
                    im1 = cv2.imdecode(nparr1, cv2.IMREAD_COLOR)
                    im2 = cv2.imdecode(nparr2, cv2.IMREAD_COLOR)
                    if im1 is not None and im2 is not None:
                        result = DeepFace.verify(im1, im2, enforce_detection=False)
                        verified = bool(result.get("verified", False))
                except Exception:
                    pass

            if not verified:
                messages.error(request, "Face verification failed. Please try again.")
                return render(request, "login.html", {"form": form})

            user.user_login = 1
            user.save()
            login(request, user)

            if user_type == "student":
                return redirect("student_index")
            return redirect("professor_index")
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


@require_http_methods(["GET", "POST"])
def contact_view(request):
    """Contact page: GET show form, POST process and thank user."""
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            messages.success(request, "Thank you. We will get back to you soon.")
            return redirect("contact")
    else:
        form = ContactForm()
    return render(request, "contact.html", {"form": form})


@require_GET
def faq_view(request):
    """FAQ static page."""
    return render(request, "faq.html")


# ---------------------------------------------------------------------------
# Lost password flow
# ---------------------------------------------------------------------------

@require_http_methods(["GET", "POST"])
def lostpassword_view(request):
    """Request OTP for password reset; store in session and show message or verify page."""
    if request.method == "POST":
        email = (request.POST.get("lpemail") or "").strip()
        if not email:
            messages.error(request, "Please enter your email.")
            return render(request, "lostpassword.html")

        user = User.objects.filter(email=email).first()
        if not user:
            messages.error(request, "No account found with this email.")
            return render(request, "lostpassword.html")

        otp = generate_otp()
        request.session["lp_email"] = email
        request.session["lp_otp"] = otp
        request.session.modified = True
        request.session.save()

        try:
            send_mail(
                "MyProctor.ai - Password Reset OTP",
                f"Your password reset OTP is {otp}.",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.info(request, "OTP sent to your email.")
        except Exception:
            request.session["lp_show_otp"] = True
            messages.warning(request, "Email failed. Use the OTP shown on the next page.")

        return redirect("verify_otp_fp")
    return render(request, "lostpassword.html")


@require_http_methods(["GET", "POST"])
def verify_otp_fp_view(request):
    """Verify OTP for forgot password; then redirect to set new password."""
    if "lp_otp" not in request.session:
        messages.warning(request, "Session expired. Please request a new OTP.")
        return redirect("lostpassword")

    lp_email = request.session.get("lp_email", "")
    show_otp = request.session.get("lp_show_otp", False)
    otp_display = request.session.get("lp_otp") if show_otp else None
    context = {"registration_email": lp_email, "otp": otp_display}

    if request.method == "POST":
        entered = (request.POST.get("fpotp") or "").strip()
        if entered != request.session.get("lp_otp"):
            context["error"] = "OTP is incorrect."
            return render(request, "verifyOTPfp.html", context)
        request.session["lp_verified"] = True
        request.session.save()
        return redirect("lp_new_pwd")

    return render(request, "verifyOTPfp.html", context)


@require_http_methods(["GET", "POST"])
def lp_new_pwd_view(request):
    """Set new password after OTP verification for forgot password."""
    if "lp_verified" not in request.session or "lp_email" not in request.session:
        messages.warning(request, "Please complete OTP verification first.")
        return redirect("lostpassword")

    if request.method == "POST":
        form = NewPasswordForm(request.POST)
        if form.is_valid():
            email = request.session["lp_email"]
            user = User.objects.get(email=email)
            user.set_password(form.cleaned_data["npwd"])
            user.save()
            for key in ["lp_email", "lp_otp", "lp_show_otp", "lp_verified"]:
                request.session.pop(key, None)
            messages.success(request, "Password updated. You can log in now.")
            return redirect("login")
    else:
        form = NewPasswordForm()
    return render(request, "lpnewpwd.html", {"form": form})


# ---------------------------------------------------------------------------
# Authenticated: dashboards and password change
# ---------------------------------------------------------------------------

@login_required
@require_GET
def student_index(request):
    """Student dashboard; redirect professor to professor_index."""
    if request.user.user_type != "student":
        return redirect("professor_index")
    return render(request, "student_index.html")


@login_required
@require_GET
def student_test_history_redirect_view(request, email):
    """Redirect old URL /<email>/student_test_history to /student_test_history/."""
    return redirect("student_test_history")


@login_required
@require_GET
def student_test_history_view(request):
    """Student exam history: list of tests the student has taken (from StudentTestInfo + Teacher)."""
    if request.user.user_type != "student":
        return redirect("professor_index")
    sti_list = StudentTestInfo.objects.filter(email=request.user.email).order_by("-stiid")
    tests = []
    for sti in sti_list:
        teacher = Teacher.objects.filter(test_id=sti.test_id).first()
        if teacher:
            tests.append({
                "test_id": sti.test_id,
                "subject": teacher.subject,
                "topic": teacher.topic,
            })
    return render(request, "student_test_history.html", {"tests": tests})


def _student_tests_list(request):
    """Shared: list of tests (test_id, subject, topic) for current student from StudentTestInfo + Teacher."""
    sti_list = StudentTestInfo.objects.filter(email=request.user.email).order_by("-stiid")
    results = []
    for sti in sti_list:
        teacher = Teacher.objects.filter(test_id=sti.test_id).first()
        if teacher:
            results.append({
                "test_id": sti.test_id,
                "subject": teacher.subject,
                "topic": teacher.topic,
            })
    return results


@login_required
@require_http_methods(["GET", "POST"])
def tests_given_view(request):
    """Tests given by student: dropdown to choose exam and view result."""
    if request.user.user_type != "student":
        return redirect("professor_index")
    cresults = _student_tests_list(request)
    if request.method == "POST":
        choosetid = (request.POST.get("choosetid") or "").strip()
        if choosetid:
            # Redirect to result page when implemented; for now stay and show message
            messages.info(request, f"Result for exam {choosetid} will be shown here when available.")
        return redirect("tests_given")
    return render(request, "tests_given.html", {"cresults": cresults})


@login_required
@require_GET
def professor_index(request):
    """Professor dashboard; redirect student to student_index."""
    if request.user.user_type != "teacher":
        return redirect("student_index")
    return render(request, "professor_index.html")


def logout_view(request):
    """Log out and clear user_login flag; always redirect to home (303 so browser does fresh GET)."""
    if request.user.is_authenticated:
        request.user.user_login = 0
        request.user.save()
    logout(request)
    # 303 See Other: browser will GET the home page fresh (no cached dashboard)
    return HttpResponseRedirect(reverse("index"), status=303)


def _change_password_view(request, template_name):
    """Shared logic for change password; template_name = changepassword_student.html or changepassword_professor.html."""
    if request.method == "POST":
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            if not request.user.check_password(form.cleaned_data["oldpassword"]):
                messages.error(request, "Old password is incorrect.")
            else:
                request.user.set_password(form.cleaned_data["newpassword"])
                request.user.save()
                messages.success(request, "Password changed successfully.")
                return redirect("login")
    else:
        form = ChangePasswordForm()
    return render(request, template_name, {"form": form})


@login_required
@require_http_methods(["GET", "POST"])
def change_password_view(request):
    """Change password (generic); redirect to role-specific page or render correct template."""
    if request.user.user_type == "student":
        return _change_password_view(request, "changepassword_student.html")
    return _change_password_view(request, "changepassword_professor.html")


@login_required
@require_http_methods(["GET", "POST"])
def change_password_student_view(request):
    """Change password page for student dashboard."""
    if request.user.user_type != "student":
        return redirect("professor_index")
    return _change_password_view(request, "changepassword_student.html")


@login_required
@require_http_methods(["GET", "POST"])
def change_password_professor_view(request):
    """Change password page for professor dashboard."""
    if request.user.user_type != "teacher":
        return redirect("student_index")
    return _change_password_view(request, "changepassword_professor.html")


# ---------------------------------------------------------------------------
# Report problem (professor / student)
# ---------------------------------------------------------------------------

@login_required
@require_GET
def report_professor_view(request):
    if request.user.user_type != "teacher":
        return redirect("student_index")
    return render(request, "report_professor.html")


@login_required
@require_GET
def report_student_view(request):
    if request.user.user_type != "student":
        return redirect("professor_index")
    return render(request, "report_student.html")


@login_required
@require_POST
def report_professor_email_view(request):
    """Accept report form POST from professor (save or email); redirect back."""
    if request.user.user_type != "teacher":
        return redirect("student_index")
    # Optional: persist to DB or send email; for now just success message
    messages.success(request, "Your report has been submitted. We will look into it.")
    return redirect("report_professor")


@login_required
@require_POST
def report_student_email_view(request):
    """Accept report form POST from student."""
    if request.user.user_type != "student":
        return redirect("professor_index")
    messages.success(request, "Your report has been submitted. We will look into it.")
    return redirect("report_student")


