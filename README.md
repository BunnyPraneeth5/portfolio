# Personal Portfolio Website

A personal portfolio website built with Django to showcase my projects, skills, certifications, achievements, and experience. The website includes a powerful admin dashboard that allows portfolio content to be managed without modifying the source code.

🌐 Live Website: https://bunnypraneeth.pythonanywhere.com/

## Why I Built This

I wanted a portfolio that was more than just a static website. Instead of hardcoding every update, I built a system where projects, skills, achievements, certifications, and other content can be managed directly through the Django admin panel.

The project also serves as a reusable portfolio solution that can be customized by other developers, students, and professionals.

## Features

* Responsive portfolio design
* Dynamic content management through Django Admin
* Project showcase section
* Skills section
* Certifications and achievements
* About and contact sections
* Easy customization and extension
* Open-source project structure

## Tech Stack

* Python
* Django
* HTML
* CSS
* JavaScript
* Bootstrap
* SQLite

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

## Project Structure

The portfolio content is managed through the Django admin panel, making it easy to update information without changing the frontend code. This allows the website to remain maintainable as new projects and achievements are added.

## Future Improvements

* Blog integration
* Resume download tracking
* Dark mode
* Advanced project filtering
* Visitor analytics
* Multi-user support

## Contributing

If you have suggestions or improvements, feel free to open an issue or submit a pull request.

## Author

Praneeth

GitHub: https://github.com/BunnyPraneeth5
