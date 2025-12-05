# PythonAnywhere Deployment Guide

## Step 1: Create MySQL Database

1. Go to PythonAnywhere Dashboard → **Databases** tab
2. Set MySQL password (if not already set)
3. Create a new database: `your_username$portfolio`
4. Note your credentials:
   - Database name: `your_username$portfolio`
   - Username: `your_username`
   - Password: (your MySQL password)
   - Host: `your_username.mysql.pythonanywhere-services.com`

## Step 2: Update settings.py

Replace placeholders in `config/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_username$portfolio',  # Replace your_username
        'USER': 'your_username',             # Replace your_username
        'PASSWORD': 'your_mysql_password',   # Replace with actual password
        'HOST': 'your_username.mysql.pythonanywhere-services.com',  # Replace your_username
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}

ALLOWED_HOSTS = ['your_username.pythonanywhere.com', 'localhost', '127.0.0.1']  # Replace your_username
```

## Step 3: Upload Files to PythonAnywhere

### Option A: Git (Recommended)
```bash
# On PythonAnywhere Bash console
cd ~
git clone https://github.com/yourusername/portfolio.git
cd portfolio
```

### Option B: Upload Files
- Use PythonAnywhere Files tab to upload project folder

## Step 4: Install Dependencies

In PythonAnywhere Bash console:
```bash
cd ~/portfolio
pip3.10 install --user -r requirements.txt
```

## Step 5: Run Migrations

```bash
python3.10 manage.py migrate
python3.10 manage.py createsuperuser
python3.10 manage.py collectstatic --noinput
```

## Step 6: Configure Web App

1. Go to **Web** tab → **Add a new web app**
2. Choose **Manual configuration**
3. Select **Python 3.10**

### Configure WSGI file

Click on WSGI configuration file link and replace content:

```python
import sys
import os

# Add your project directory to the sys.path
path = '/home/your_username/portfolio'  # Replace your_username
if path not in sys.path:
    sys.path.append(path)

# Set environment variable for Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### Configure Static Files

In Web tab, add static file mappings:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/your_username/portfolio/staticfiles` |
| `/media/` | `/home/your_username/portfolio/media` |

### Set Virtualenv (Optional)

If using virtualenv:
- Virtualenv: `/home/your_username/.virtualenvs/portfolio`

## Step 7: Reload Web App

Click the green **Reload** button

## Step 8: Access Your Site

- Website: `https://your_username.pythonanywhere.com`
- Admin: `https://your_username.pythonanywhere.com/admin`

## Troubleshooting

### Check Error Logs
- Go to Web tab → Error log
- Go to Web tab → Server log

### Common Issues

**Import Error:**
```bash
pip3.10 install --user mysqlclient
```

**Static files not loading:**
```bash
python3.10 manage.py collectstatic --noinput
```

**Database connection error:**
- Verify database credentials in settings.py
- Check MySQL is initialized in Databases tab

## Update Deployment

When you make changes:
```bash
cd ~/portfolio
git pull  # If using git
python3.10 manage.py migrate
python3.10 manage.py collectstatic --noinput
```

Then click **Reload** in Web tab

## Security Checklist

- [ ] Changed SECRET_KEY in settings.py
- [ ] Set DEBUG = False for production
- [ ] Updated ALLOWED_HOSTS with your domain
- [ ] Database credentials are correct
- [ ] Static files collected
- [ ] Admin user created
