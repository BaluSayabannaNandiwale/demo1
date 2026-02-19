# Flask to Django Conversion Guide

## ✅ Completed

### 1. Project Structure
- ✅ Django project (`quizapp`) created
- ✅ Django apps created: `accounts`, `exams`, `proctoring`
- ✅ Settings configured (database, email, static files, sessions)
- ✅ URLs configured

### 2. Models
- ✅ All database models converted to Django ORM:
  - `User` (custom user model with PermissionsMixin)
  - `Teacher`, `Question`, `Student`, `StudentTestInfo`
  - `LongQA`, `LongTest`, `PracticalQA`, `PracticalTest`
  - `ProctoringLog`, `WindowEstimationLog`
- ✅ Migrations created successfully

### 3. Authentication
- ✅ Registration view with OTP verification
- ✅ Login view with face verification
- ✅ Logout view
- ✅ Change password view
- ✅ Custom decorators for role-based access (`user_role_professor`, `user_role_student`)

### 4. Forms
- ✅ RegisterForm
- ✅ LoginForm
- ✅ ChangePasswordForm
- ✅ LostPasswordForm
- ✅ NewPasswordForm

### 5. Admin
- ✅ Admin interfaces configured for all models

## ⏳ Remaining Work

### 1. Views (Need Conversion)
The Flask app has **73 routes** that need to be converted. Here are the main categories:

#### Accounts Views (Partially Done)
- ✅ Register, Login, Logout, Verify Email, Change Password
- ⏳ Lost Password flow
- ⏳ Professor/Student dashboards

#### Exam Views (Need Conversion)
- ⏳ Test creation (objective, subjective, practical)
- ⏳ Test taking interface
- ⏳ Question management
- ⏳ Results viewing
- ⏳ Test history

#### Proctoring Views (Need Conversion)
- ⏳ Video feed endpoint
- ⏳ Window event logging
- ⏳ Proctoring log viewing
- ⏳ Live monitoring

### 2. Templates
All templates need Django syntax conversion:
- Change `{{ }}` and `{% %}` syntax (mostly compatible)
- Change `url_for()` to `{% url %}` tag
- Change `session` to `request.session`
- Change `flash()` messages to Django messages framework
- Update form rendering to use Django forms

### 3. Static Files
- Ensure static files are properly configured
- Update template references to use `{% static %}` tag

### 4. Additional Features
- ⏳ File uploads handling
- ⏳ JSON responses for AJAX endpoints
- ⏳ Stripe payment integration
- ⏳ Email sending (configured, needs testing)

## Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements_django.txt
```

2. **Run migrations:**
```bash
python manage.py migrate
```

3. **Create superuser:**
```bash
python manage.py createsuperuser
```

4. **Run server:**
```bash
python manage.py runserver
```

## Key Differences: Flask vs Django

| Flask | Django |
|-------|--------|
| `@app.route('/path')` | `path('path', view)` in urls.py |
| `render_template()` | `render(request, 'template.html')` |
| `session['key']` | `request.session['key']` |
| `flash()` | `messages.success/error/info()` |
| `url_for('route')` | `{% url 'route' %}` in templates |
| `request.form` | Form classes with `cleaned_data` |
| `redirect(url_for())` | `redirect('route_name')` |
| Custom decorators | Same approach works |

## Next Steps

1. **Convert remaining views** - Start with exam views, then proctoring
2. **Update templates** - Convert Jinja2 to Django template syntax
3. **Test functionality** - Test each feature after conversion
4. **Handle file uploads** - Configure media file handling
5. **Add tests** - Create unit tests for critical functionality

## Notes

- The database schema remains the same (SQLite)
- All models use `db_table` to match existing table names
- Custom User model extends `AbstractBaseUser` and `PermissionsMixin`
- Session handling uses Django's session framework
- Email configuration matches Flask settings
