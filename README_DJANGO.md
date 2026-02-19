# Django Conversion - MyProctor.ai

This project has been converted from Flask to Django framework.

## Project Structure

```
quizapp/
├── manage.py
├── quizapp/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/         # User authentication app
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
├── exams/            # Exam management app
│   ├── models.py
│   ├── urls.py
│   └── admin.py
├── proctoring/       # Proctoring features app
│   ├── models.py
│   ├── urls.py
│   └── admin.py
├── templates/        # HTML templates (shared)
├── static/           # Static files (CSS, JS, images)
└── media/            # User uploaded files
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements_django.txt
```

2. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

3. Create superuser:
```bash
python manage.py createsuperuser
```

4. Run development server:
```bash
python manage.py runserver
```

## Key Changes from Flask

### Models
- All database models converted to Django ORM
- Custom User model extends AbstractBaseUser
- Foreign key relationships properly defined

### Views
- Flask routes converted to Django class-based or function-based views
- Session handling uses Django's session framework
- Authentication uses Django's auth system

### Forms
- Flask-WTF forms converted to Django forms
- Form validation using Django's form validation

### URLs
- Flask `@app.route` decorators converted to Django URL patterns
- URL routing organized by app

### Templates
- Jinja2 templates need to be converted to Django template syntax
- Template inheritance works similarly
- Context variables passed via `render()` function

## Next Steps

1. **Convert remaining views**: Complete conversion of all 73 Flask routes to Django views
2. **Update templates**: Convert Jinja2 syntax to Django template syntax
3. **Add middleware**: Implement custom decorators as middleware if needed
4. **Test functionality**: Test all features after conversion
5. **Deploy**: Configure for production deployment

## Migration Notes

- Database: SQLite (same as Flask version)
- Email: Django's email backend configured
- Static files: Django static files handling
- Media files: Django media files handling
- Sessions: Django session framework

## Status

✅ Project structure created
✅ Models converted
✅ Basic authentication views converted
⏳ Remaining views need conversion
⏳ Templates need Django syntax conversion
⏳ Forms need completion
