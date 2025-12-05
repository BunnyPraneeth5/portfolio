# Django Portfolio Setup Guide

## Quick Start

### 1. Create and Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Create Superuser
```bash
python manage.py createsuperuser
```

### 3. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 4. Run Development Server
```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

## Admin Panel

Access admin at: http://127.0.0.1:8000/admin/

### Add Content via Admin:

1. **About Section**: Add your bio and information
2. **Skills**: Add skills with percentages (0-100)
3. **Projects**: Add projects with descriptions, links, and technologies
4. **Blog Posts**: Create blog posts (optional)
5. **Contact Messages**: View messages from contact form

## Project Structure

```
portfolio/
├── config/              # Django settings
├── portfolio/           # Main app
│   ├── models.py       # Database models
│   ├── views.py        # View functions
│   ├── urls.py         # URL patterns
│   └── admin.py        # Admin configuration
├── templates/          # HTML templates
├── static/            # CSS, JS, images
└── media/            # Uploaded files
```

## Features Implemented

✅ Django backend with SQLite database
✅ Admin panel for content management
✅ Contact form with database storage
✅ Blog system (ready for content)
✅ Projects showcase
✅ Skills management
✅ Static files properly configured
✅ All pages converted to Django templates

## Next Steps

1. Add content through admin panel
2. Customize templates as needed
3. Add blog posts
4. Configure email backend for contact form notifications
5. Deploy to production (Heroku, Railway, etc.)

## Environment Variables (Production)

```
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
```
