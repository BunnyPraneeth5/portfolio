# Local Development Guide

## Overview
`config/settings.py` is pre-configured to use **SQLite** by default for local development. You do not need external database servers (like MySQL) to run the project locally.

## Standard Local Development Workflow

### 1. Run Migrations
```bash
python manage.py migrate
```

### 2. Create Superuser
```bash
python manage.py createsuperuser
```

### 3. Start Development Server
```bash
python manage.py runserver
```

Visit:
- Website: `http://127.0.0.1:8000/`
- Admin Panel: `http://127.0.0.1:8000/admin/`

---

## Using Local Settings Override (Optional)

If you wish to test custom overrides without modifying `config/settings.py`, you can use `config.settings_local`:

### Run Server with Local Settings:
```bash
python manage.py runserver --settings=config.settings_local
```

### Run Migrations with Local Settings:
```bash
python manage.py migrate --settings=config.settings_local
```

### Collect Static Files:
```bash
python manage.py collectstatic --noinput
```

---

## File Structure & Configuration

- `config/settings.py` - Core Django settings (Defaults to SQLite; evaluates `.env` for production override)
- `config/settings_local.py` - Optional local settings override
- `.env.example` - Template for environment variables (`DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`, database configuration)

## Quick Tips

1. **Admin Panel Access**: Login at `http://127.0.0.1:8000/admin/` using your superuser credentials.
2. **Local Media Uploads**: Profile images, project thumbnails, resumes, and certificates are saved to `media/` directory during local testing.
3. **Database Reset**: To reset local data, delete `db.sqlite3` and run `python manage.py migrate` followed by `python manage.py createsuperuser`.

