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

## 5. Add & Manage Content

### Configure Site Settings & Hero:
- Click **Site Settings** → Edit entry
- Upload profile image and resume PDF
- Set hero name display, multiline rotating roles, and bio description
- Configure social links (GitHub, LinkedIn, LeetCode, Kaggle, HackerRank) and contact email/location
- Save

### Configure Site Appearance:
- Click **Site Appearance** → Edit entry
- Choose primary, secondary, and accent colors using color pickers
- Save

### Add About Info:
- Click **About** → Edit entry
- Fill in title, subtitle, and bio paragraphs (1–3)
- Set stat metrics (e.g., Accuracy %, MCP Agents Built, Projects Completed)
- Save

### Add Skills:
- Click **Skills** → **Add Skill**
- Enter skill name, select category (Agentic AI & MCP, ML & Data, Web & APIs, Languages, Security, Tools, Soft Skills)
- Check "Is featured" to display on homepage
- Set order number
- Save

### Add Projects:
- Click **Projects** → **Add Project**
- Fill in title, short description, and optional long description
- Upload thumbnail image
- Add tech tags (comma-separated, e.g., `Python, Django, Tailwind`)
- Enter Live Demo URL and GitHub URL
- Check "Is featured" to feature on homepage or "Is published" to publish
- Optionally add metric kickers and key metric statistics
- Save

### Add Timeline & Experience Entries:
- **What I Do**: Add key skills & focus areas
- **Education**: Add degree, field of study, institution, year range, bullet points
- **Professional Experience**: Add organization, role, year, side (left/right column), tags, and certificate upload links
- **Events & Leadership**: Add event title, role, year, location, description, and event stats
- **Additional Certifications**: Add certificate title, FontAwesome icon, and certificate PDF download

### Add Blog Posts:
- Click **Blog posts** → **Add Blog post**
- Enter title (slug auto-generates)
- Write content (HTML supported)
- Add excerpt and upload featured image
- Check "Published" to make visible
- Save

## 6. View Website
Visit: `http://127.0.0.1:8000/`

All content managed from the admin panel will display dynamically!

