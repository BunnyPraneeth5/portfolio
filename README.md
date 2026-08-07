# Personal Portfolio Website

A personal portfolio website built with Django to showcase my projects, skills, certifications, achievements, and experience. The website includes a powerful admin dashboard that allows portfolio content to be managed dynamically without modifying the source code.

🌐 Live Website: https://bunnypraneeth.pythonanywhere.com/

## Why I Built This

I wanted a portfolio that was more than just a static website. Instead of hardcoding every update, I built a system where projects, skills, achievements, certifications, blog posts, and site appearance can be managed directly through the Django admin panel.

The project also serves as a reusable portfolio solution that can be customized by other developers, students, and professionals.

## Features

* Dynamic content management through Django Admin
* Project showcase with metric kickers & tech tags
* Categorized skill matrix (Agentic AI, ML, Web, Security, Tools, etc.)
* Timeline management (Education, Experience, Events & Leadership)
* Certifications and achievements showcase
* Built-in Blog engine with detail pages
* Customizable site appearance (theme accent colors) & site settings (hero, social links, contact info)
* Responsive design with dynamic micro-animations
* Contact form with database logging & toggle control

## Tech Stack

* **Backend**: Python, Django 5.x
* **Database**: SQLite (Local development), MySQL (Production)
* **Frontend**: HTML5, Tailwind CSS, JavaScript, FontAwesome 6, AOS Animation Library
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

The portfolio content is managed through the Django admin panel, making it easy to update information without changing the frontend code. This allows the website to remain maintainable as new projects and achievements are added.

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

