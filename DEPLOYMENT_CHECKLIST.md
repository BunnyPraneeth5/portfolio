# PythonAnywhere Deployment Checklist

## Before Deployment

- [ ] Update `config/settings.py` with your MySQL credentials
- [ ] Replace `your_username` with actual PythonAnywhere username (4 places in settings.py)
- [ ] Replace `your_mysql_password` with actual MySQL password
- [ ] Update `ALLOWED_HOSTS` with your PythonAnywhere domain
- [ ] Install mysqlclient: `pip install mysqlclient`

## On PythonAnywhere

### 1. Database Setup
- [ ] Go to Databases tab
- [ ] Initialize MySQL (set password)
- [ ] Create database: `your_username$portfolio`
- [ ] Note credentials

### 2. Upload Project
- [ ] Upload files OR clone from Git
- [ ] Navigate to project directory

### 3. Install Dependencies
```bash
cd ~/portfolio
pip3.10 install --user -r requirements.txt
```

### 4. Run Migrations
```bash
python3.10 manage.py migrate
python3.10 manage.py createsuperuser
python3.10 manage.py collectstatic --noinput
```

### 5. Configure Web App
- [ ] Create new web app (Manual configuration, Python 3.10)
- [ ] Update WSGI file (copy from `wsgi_pythonanywhere.py`)
- [ ] Add static files mapping: `/static/` → `/home/your_username/portfolio/staticfiles`
- [ ] Add media files mapping: `/media/` → `/home/your_username/portfolio/media`

### 6. Launch
- [ ] Click Reload button
- [ ] Visit your site
- [ ] Test admin panel
- [ ] Add content

## Post-Deployment

- [ ] Change SECRET_KEY in production
- [ ] Set DEBUG = False
- [ ] Test all pages
- [ ] Test contact form
- [ ] Upload resume and certificates
- [ ] Add projects and skills via admin

## Quick Reference

**Your URLs:**
- Site: `https://your_username.pythonanywhere.com`
- Admin: `https://your_username.pythonanywhere.com/admin`

**Update Site:**
```bash
cd ~/portfolio
git pull  # if using git
python3.10 manage.py migrate
python3.10 manage.py collectstatic --noinput
# Click Reload in Web tab
```
