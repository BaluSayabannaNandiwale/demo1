# Database Migration Instructions

## Issue
The database `quizapp.db` already exists from the Flask version. Django migrations are trying to create tables that already exist.

## Solution Options

### Option 1: Use Existing Database (Recommended)
Since the database schema matches, you can fake the initial migrations:

```bash
python manage.py migrate --fake-initial
```

This tells Django that the tables already exist and skips creating them.

### Option 2: Backup and Start Fresh
If you want a clean Django database:

1. Backup existing database:
```bash
cp quizapp.db quizapp.db.backup
```

2. Delete existing database:
```bash
rm quizapp.db
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create superuser:
```bash
python manage.py createsuperuser
```

### Option 3: Use Existing Data
If you want to keep existing data and use Django:

1. Fake initial migrations:
```bash
python manage.py migrate --fake-initial
```

2. The existing data will be accessible through Django ORM

## Recommended Approach

Since you already have data in the database, use Option 1:

```bash
python manage.py migrate --fake-initial
```

This will:
- ✅ Keep all existing data
- ✅ Set up Django's auth tables (if needed)
- ✅ Make Django aware of existing tables
- ✅ Allow Django ORM to work with existing data

## After Migration

1. **Test the application:**
```bash
python manage.py runserver
```

2. **Access admin panel:**
- Go to http://127.0.0.1:8000/admin/
- Login with superuser credentials

3. **Verify models:**
- Check that existing users appear in admin
- Verify relationships work correctly

## Notes

- Django will create additional tables for sessions, admin, etc.
- Your existing `users`, `teachers`, `questions`, etc. tables will remain unchanged
- Django ORM will work with existing data seamlessly
