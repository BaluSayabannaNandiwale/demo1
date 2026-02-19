"""
URL configuration for accounts app.
All account-related routes: auth, registration, verification, contact, FAQ, password, reports.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Public
    path("", views.index, name="index"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("verifyEmail/", views.verify_email_view, name="verify_email"),
    path("contact/", views.contact_view, name="contact"),
    path("faq/", views.faq_view, name="faq"),
    # Lost password
    path("lostpassword/", views.lostpassword_view, name="lostpassword"),
    path("verifyOTPfp/", views.verify_otp_fp_view, name="verify_otp_fp"),
    path("lpnewpwd/", views.lp_new_pwd_view, name="lp_new_pwd"),
    # Authenticated
    path("logout/", views.logout_view, name="logout"),
    path("changepassword/", views.change_password_view, name="change_password"),
    path("changepassword_student/", views.change_password_student_view, name="change_password_student"),
    path("changepassword_professor/", views.change_password_professor_view, name="change_password_professor"),
    path("student_index", views.student_index, name="student_index"),
    path("student_test_history/", views.student_test_history_view, name="student_test_history"),
    path("tests-given/", views.tests_given_view, name="tests_given"),
    path("professor_index", views.professor_index, name="professor_index"),
    # Report problem
    path("report_professor", views.report_professor_view, name="report_professor"),
    path("report_professor_email", views.report_professor_email_view, name="report_professor_email"),
    path("report_student", views.report_student_view, name="report_student"),
    path("report_student_email", views.report_student_email_view, name="report_student_email"),
]
