# Personal Portfolio Website

A personal portfolio website built with Django to showcase my projects, skills, certifications, achievements, and experience. The website includes a powerful admin dashboard that allows portfolio content to be managed dynamically without modifying the source code.

🌐 Live Website: https://bunnypraneeth.pythonanywhere.com/

## Why I Built This

I wanted a portfolio that was more than just a static website. Instead of hardcoding every update, I built a system where projects, skills, achievements, certifications, blog posts, and site settings can be managed directly through the Django admin panel.

The project also serves as a reusable portfolio solution that can be customized by other developers, students, and professionals.

## Features

* Dynamic content management through Django Admin
* Project case files: brief, decisions, incidents, open leads and metrics
* Recorded agent replays on case files, uploaded in admin or imported with `python manage.py import_replay`
* Rule-based chat helper whose answers, keywords and job search mode are edited in admin
* Categorized skills, with the core stack marked
* Experience, education, events and certifications on the About page
* Blog posts presented as logs
* Site settings for hero text, social links, contact details and SEO
* Meta descriptions and Open Graph tags on every page
* Contact form with database logging and an on/off switch

## Tech Stack

* **Backend**: Python, Django 5.x
* **Database**: SQLite (Local development), MySQL (Production)
* **Frontend**: HTML5, one hand-written stylesheet, vanilla JavaScript (no frontend libraries, no build step)
* **Media & Utilities**: Pillow, Python-Dotenv

## Getting Started

### Clone the Repository

```bash
git clone https://github.com/BunnyPraneeth5/portfolio.git
cd portfolio
```

### Create a Virtual Environment

```bash
python -m venv venv
```

### Activate the Environment

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Migrations

```bash
python manage.py migrate
```

### Create an Admin Account

```bash
python manage.py createsuperuser
```

### Run the Tests

```bash
python manage.py test portfolio
```

### Start the Development Server

```bash
python manage.py runserver
```

Visit:

```text
http://127.0.0.1:8000/
```

Admin Panel:

```text
http://127.0.0.1:8000/admin/
```

## Project Structure

The portfolio content is managed through the Django admin panel, making it easy to update information without changing the frontend code. See `ARCHITECTURE.md` for routes, models and the request flow, `ADMIN_GUIDE.md` for filling content, and `docs/REPLAY_FORMAT.md` for the replay file format.

## Future Improvements

* Resume download tracking & analytics
* Dark / Light mode toggle switch
* Advanced project search and tag filtering
* Visitor analytics dashboard
* Multi-user support

## Contributing

If you have suggestions or improvements, feel free to open an issue or submit a pull request.

## Author

Praneeth

GitHub: https://github.com/BunnyPraneeth5

