# Django Portfolio Setup Guide

## Local Development Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Database (Local Testing with SQLite)
For local testing, temporarily change `config/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### 3. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser
```bash
python manage.py createsuperuser
```

### 5. Run Development Server
```bash
python manage.py runserver
```

Access admin panel at: `http://127.0.0.1:8000/admin/`

## PythonAnywhere Deployment

### 1. Upload Files
- Upload all project files to PythonAnywhere

### 2. Setup MySQL Database
- Go to PythonAnywhere Dashboard → Databases
- Create MySQL database and note credentials
- Update `config/settings.py` with your MySQL credentials:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_username$dbname',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'your_username.mysql.pythonanywhere-services.com',
        'PORT': '3306',
    }
}
```

### 3. Configure ALLOWED_HOSTS
```python
ALLOWED_HOSTS = ['your_username.pythonanywhere.com']
```

### 4. Run Migrations on PythonAnywhere
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

### 5. Configure WSGI
Edit `/var/www/your_username_pythonanywhere_com_wsgi.py`:
```python
import sys
import os

path = '/home/your_username/portfolio'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 6. Configure Static/Media Files
In PythonAnywhere Web tab:
- Static URL: `/static/` → Directory: `/home/your_username/portfolio/staticfiles`
- Static URL: `/media/` → Directory: `/home/your_username/portfolio/media`

### 7. Reload Web App
Click "Reload" button in PythonAnywhere Web tab

## Admin Panel Usage

### Access Admin
- Local: `http://127.0.0.1:8000/admin/`
- Live: `https://your_username.pythonanywhere.com/admin/`

### Managing Content

**About Section:**
- Add/Edit personal information
- Upload profile image
- Upload resume PDF

**Skills:**
- Add skills with name and percentage
- Set order for display
- Add Font Awesome icon class (e.g., 'fab fa-python')

**Projects:**
- Add project title, description
- Upload project image
- Add live URL and GitHub URL
- List technologies (comma-separated)
- Mark as featured to show on homepage

**Blog Posts:**
- Create blog posts with title and slug
- Write content (supports HTML)
- Upload featured image
- Add excerpt for preview
- Toggle published status

## Template Integration

Move your existing HTML files to `templates/` directory and update them to use Django template tags:

```django
<!-- Load static files -->
{% load static %}

<!-- Display projects -->
{% for project in projects %}
    <h3>{{ project.title }}</h3>
    <img src="{{ project.image.url }}" alt="{{ project.title }}">
    <p>{{ project.description }}</p>
{% endfor %}

<!-- Display skills -->
{% for skill in skills %}
    <div>{{ skill.name }}: {{ skill.percentage }}%</div>
{% endfor %}
```

## Security Notes

- Change SECRET_KEY in production
- Set DEBUG = False in production
- Never commit database credentials to Git
- Use environment variables for sensitive data
