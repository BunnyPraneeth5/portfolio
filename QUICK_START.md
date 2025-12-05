# Quick Start Guide

## 1. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## 2. Create Admin User
```bash
python manage.py createsuperuser
```
Enter username, email, and password when prompted.

## 3. Start Server
```bash
python manage.py runserver
```

## 4. Access Admin Panel
Open browser: `http://127.0.0.1:8000/admin/`

Login with your superuser credentials.

## 5. Add Content

### Add About Info:
- Click "Abouts" → "Add About"
- Fill in title, description
- Upload image and resume
- Save

### Add Skills:
- Click "Skills" → "Add Skill"
- Enter name, percentage (0-100)
- Add Font Awesome icon class (optional)
- Set order number
- Save

### Add Projects:
- Click "Projects" → "Add Project"
- Fill in title, description
- Upload project image
- Add URLs and technologies
- Check "Featured" to show on homepage
- Save

### Add Blog Posts:
- Click "Blog posts" → "Add Blog post"
- Enter title (slug auto-generates)
- Write content (HTML supported)
- Add excerpt
- Upload featured image
- Check "Published" to make visible
- Save

## 6. View Website
Visit: `http://127.0.0.1:8000/`

All content from admin panel will display automatically!
