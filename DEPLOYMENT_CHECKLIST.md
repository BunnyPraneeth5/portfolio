# PythonAnywhere Deployment Checklist

## Before Deployment

- [ ] Create `.env` file (or update `config/settings.py`) with your MySQL credentials
- [ ] Set `SECRET_KEY` and `DEBUG=False` in environment / settings
- [ ] Update `ALLOWED_HOSTS` with your PythonAnywhere domain (`your_username.pythonanywhere.com`)
- [ ] Install mysqlclient dependency (`pip install mysqlclient`)

## On PythonAnywhere

### 1. Database Setup
- [ ] Go to Databases tab
- [ ] Initialize MySQL (set password)
- [ ] Create database: `your_username$portfolio`
- [ ] Note credentials

### 2. Upload Project
- [ ] Upload files OR clone from Git (`https://github.com/BunnyPraneeth5/portfolio.git`)
- [ ] Navigate to project directory (`cd ~/portfolio`)

### 3. Install Dependencies
```bash
cd ~/portfolio
pip install --user -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 5. Configure Web App
- [ ] Create new web app (Manual configuration, Python 3.10+)
- [ ] Update WSGI file (copy reference from `_backup/wsgi_pythonanywhere.py`)
- [ ] Add static files mapping: `/static/` → `/home/your_username/portfolio/staticfiles`
- [ ] Add media files mapping: `/media/` → `/home/your_username/portfolio/media`

### 6. Launch
- [ ] Click Reload button
- [ ] Visit your site (`https://your_username.pythonanywhere.com`)
- [ ] Test admin panel (`https://your_username.pythonanywhere.com/admin`)
- [ ] Configure Site Settings & Site Appearance

## Post-Deployment

- [ ] Change `SECRET_KEY` in production environment
- [ ] Verify `DEBUG = False`
- [ ] Test all pages (About, Skills, Projects, Blog, Contact)
- [ ] Test contact form submission
- [ ] Upload resume PDF and project images via admin

## Quick Reference

**Your URLs:**
- Site: `https://your_username.pythonanywhere.com`
- Admin: `https://your_username.pythonanywhere.com/admin`

**Update Site:**
```bash
cd ~/portfolio
git pull  # if using git
python manage.py migrate
python manage.py collectstatic --noinput
# Click Reload in Web tab
```

