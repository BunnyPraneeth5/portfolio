# Local Development Guide

## Problem
The project is configured for MySQL (PythonAnywhere), but you need SQLite for local development.

## Solution: Use Local Settings

### Run Server Locally
```bash
python manage.py runserver --settings=config.settings_local
```

### Run Migrations Locally
```bash
python manage.py migrate --settings=config.settings_local
```

### Create Superuser Locally
```bash
python manage.py createsuperuser --settings=config.settings_local
```

### Access Admin Locally
```
http://127.0.0.1:8000/admin/
```

## Quick Commands

**Start server:**
```bash
python manage.py runserver --settings=config.settings_local
```

**Make migrations:**
```bash
python manage.py makemigrations --settings=config.settings_local
python manage.py migrate --settings=config.settings_local
```

**Collect static files:**
```bash
python manage.py collectstatic --settings=config.settings_local --noinput
```

## Testing Admin Features

1. Start server: `python manage.py runserver --settings=config.settings_local`
2. Go to: http://127.0.0.1:8000/admin/
3. Login with your credentials
4. Test adding/editing/deleting:
   - About section
   - Skills
   - Projects
   - Blog posts
   - Contact messages

## File Structure

- `config/settings.py` - Production settings (MySQL for PythonAnywhere)
- `config/settings_local.py` - Local development settings (SQLite)

## Important Notes

- Local database (SQLite) is separate from production (MySQL)
- Changes in local database won't affect production
- Always use `--settings=config.settings_local` for local development
- For production deployment, use default settings (MySQL)
