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

1. **Site Settings**: Set profile image, resume PDF, hero display title, social URLs, and contact info
2. **Site Appearance**: Customize site primary, secondary, and accent colors
3. **About Section**: Add bio paragraphs and key metric stats
4. **Skills**: Add skills grouped by category (Agentic AI, ML, Web, Security, Tools, etc.)
5. **Projects**: Add featured and archived projects with short/long descriptions, tech tags, URLs, and performance metrics
6. **Education & Experience**: Populate education history, work experience timeline, events, and additional certifications
7. **Blog Posts**: Publish technical posts and case studies
8. **Contact Messages**: View incoming messages sent via the contact form

## Project Structure

```
portfolio/
├── config/              # Django settings & URL routing
│   ├── settings.py      # Core configuration (env-aware)
│   ├── settings_local.py# Optional local override settings
│   └── urls.py          # Root URL dispatcher
├── portfolio/           # Main application
│   ├── models.py        # Database schema definitions
│   ├── views.py         # Views & request handlers
│   ├── urls.py          # Application URL patterns
│   ├── context_processors.py # Global site settings & appearance processors
│   └── admin.py         # Customized Django admin interface
├── templates/           # HTML templates (Tailwind & Django template tags)
├── static/              # Custom CSS stylesheets & JS scripts
└── media/               # Uploaded images, resumes, and certificates
```

## Features Implemented

✅ Django backend with SQLite (default local) & MySQL (production support)  
✅ Fully customized Admin panel for zero-code dynamic content management  
✅ Contact form with database storage and availability toggle  
✅ Built-in Blog engine with detail page routing  
✅ Project showcase with metrics, kickers, and tech tags  
✅ Categorized skill matrix  
✅ Experience, Education, Events, & Certifications timeline engine  
✅ Dynamic theme accent color customizer via CSS root variables  

## Next Steps

1. Configure site settings and appearance via admin panel
2. Populate projects, skills, education, and experience entries
3. Write and publish blog posts
4. Deploy to production (PythonAnywhere, VPS, Heroku, Railway, etc.)

## Environment Variables (.env)

```env
# Django Core Settings
DEBUG=True
SECRET_KEY=your-custom-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Production Database Configuration (Optional for local SQLite testing)
DB_NAME=your_username$portfolio
DB_USER=your_username
DB_PASSWORD=your_mysql_password
DB_HOST=your_username.mysql.pythonanywhere-services.com
DB_PORT=3306
```

