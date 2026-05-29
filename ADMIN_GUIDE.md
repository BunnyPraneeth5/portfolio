# Admin Panel Guide

## ✅ Admin is Working!

All models (About, Skills, Projects, Blog, Contact) are functioning correctly.

## Quick Start

### 1. Start Local Server
```bash
python manage.py runserver --settings=config.settings_local
```

Or double-click: `run_local.bat`

### 2. Access Admin
Open browser: http://127.0.0.1:8000/admin/

### 3. Login
Use the superuser credentials you created

## Admin Features

### About Section
- **Add**: Click "About" → "Add About"
- **Edit**: Click on existing entry
- **Fields**: Title, Description, Image, Resume
- **Note**: Usually only one About entry needed

### Skills
- **Add**: Click "Skills" → "Add Skill"
- **Edit**: Click on skill name OR edit inline
- **Fields**: 
  - Name (e.g., "Python")
  - Percentage (0-100)
  - Icon (Font Awesome class, e.g., "fab fa-python")
  - Order (for sorting)
- **Inline Editing**: Change percentage/order directly in list

### Projects
- **Add**: Click "Projects" → "Add Project"
- **Edit**: Click on project title
- **Fields**:
  - Title
  - Description
  - Image (optional)
  - Live URL
  - GitHub URL
  - Technologies (comma-separated)
  - Featured (shows on homepage)
- **Inline Editing**: Toggle "Featured" directly in list

### Blog Posts
- **Add**: Click "Blog posts" → "Add Blog post"
- **Edit**: Click on post title
- **Fields**:
  - Title
  - Slug (auto-generated from title)
  - Content (HTML supported)
  - Excerpt (short preview)
  - Image (optional)
  - Published (toggle visibility)
- **Inline Editing**: Toggle "Published" directly in list

### Contact Messages
- **View**: Click "Contact messages"
- **Read**: Click on message to view details
- **Note**: Read-only, submitted via contact form

## Common Tasks

### Add a New Skill
1. Go to Skills → Add Skill
2. Enter name: "Django"
3. Set percentage: 85
4. Add icon: "fab fa-python" (optional)
5. Set order: 2
6. Click "Save"

### Feature a Project
1. Go to Projects
2. Check the "Featured" box for desired project
3. It will appear on homepage

### Publish a Blog Post
1. Go to Blog posts
2. Check the "Published" box
3. Post will be visible on blog page

### Update About Section
1. Go to About
2. Click on existing entry
3. Update text/upload new image
4. Click "Save"

## Troubleshooting

### Can't Login?
Create new superuser:
```bash
python manage.py createsuperuser --settings=config.settings_local
```

### Changes Not Showing?
1. Clear browser cache (Ctrl+Shift+Delete)
2. Refresh page (Ctrl+F5)
3. Check if item is published/featured

### Images Not Uploading?
- Ensure `media/` folder exists
- Check file size (keep under 5MB)
- Use common formats: JPG, PNG, GIF

### Admin Looks Broken?
Run collectstatic:
```bash
python manage.py collectstatic --settings=config.settings_local --noinput
```

## Tips

- **Bulk Actions**: Select multiple items and use dropdown actions
- **Search**: Use search box to find specific entries
- **Filters**: Use right sidebar to filter by date/status
- **Ordering**: Drag items to reorder (where supported)
- **Preview**: Open site in new tab to see changes

## Production (PythonAnywhere)

For production, use default settings (MySQL):
```bash
python manage.py runserver  # No --settings flag
```

Admin URL: `https://your_username.pythonanywhere.com/admin/`
