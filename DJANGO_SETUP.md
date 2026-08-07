# Django Portfolio Setup Guide

## Local Development Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Migrations
Default database setup in `config/settings.py` uses SQLite (`db.sqlite3`). Simply run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Superuser
```bash
python manage.py createsuperuser
```

### 4. Run Development Server
```bash
python manage.py runserver
```

Access admin panel at: `http://127.0.0.1:8000/admin/`

---

## PythonAnywhere Deployment

### 1. Upload Files
- Upload all project files to PythonAnywhere or clone from Git

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

### 3. Configure ALLOWED_HOSTS & Environment Variables
In `config/settings.py` or `.env`:
```python
ALLOWED_HOSTS = ['your_username.pythonanywhere.com']
```

### 4. Run Migrations on PythonAnywhere
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
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

---

## Admin Panel Usage

### Access Admin
- Local: `http://127.0.0.1:8000/admin/`
- Live: `https://your_username.pythonanywhere.com/admin/`

### Managing Content

**Site Settings:**
- Profile image & Resume PDF link
- Hero title, rotating multiline roles, and description
- CTA button labels & links
- Social media profiles (GitHub, LinkedIn, Kaggle, LeetCode, HackerRank)
- Contact email, location, tagline, and form availability toggle

**Site Appearance:**
- Customize primary, secondary, and accent colors via color pickers

**About Section:**
- Add/Edit title, subtitle, and bio paragraphs (1–3)
- Configure performance stat metrics (Accuracy %, MCP Agents Built, Projects, Teams)

**Skills:**
- Add skills with name, category choice, and display order
- Toggle `is_featured` to display on homepage

**Projects:**
- Add project title, short description, and optional long description
- Upload thumbnail image
- Add live demo URL and GitHub repository URL
- List technologies via `tech_tags` (comma-separated)
- Toggle `is_featured` and `is_published`
- Set metric kickers and metric statistics

**Education & Experience Timelines:**
- Manage Education entries, Experience timeline items (with certificate download links), Events & Leadership entries, and Additional Certifications

**Blog Posts:**
- Create blog posts with title, slug, content (HTML supported), excerpt, and featured image
- Toggle `published` status

---

## Template Integration

Templates reside in `templates/` directory and use standard Django template tags:

```django
<!-- Load static files -->
{% load static %}

<!-- Display projects -->
{% for project in projects %}
    <h3>{{ project.title }}</h3>
    <img src="{{ project.card_image.url }}" alt="{{ project.title }}">
    <p>{{ project.card_description }}</p>
{% endfor %}

<!-- Display skills -->
{% for skill in skills %}
    <div>{{ skill.name }} ({{ skill.get_category_display }})</div>
{% endfor %}
```

## Security Notes

- Change `SECRET_KEY` in production
- Set `DEBUG = False` in production
- Never commit database credentials or secrets to public Git repositories
- Use environment variables (`.env`) for sensitive data

