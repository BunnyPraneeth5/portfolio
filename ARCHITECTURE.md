# System Architecture

## 1. Overview

A personal portfolio built with Django. One app (`portfolio`) renders server-side HTML templates, styled by a single stylesheet (`static/styles.css`) and a small amount of vanilla JavaScript. There is no frontend build step and no third-party CSS or JS library (Tailwind, Font Awesome and AOS were removed in Phase 7). The only external asset is Google Fonts.

### Dependencies (`requirements.txt`)
* `Django>=5.0,<6.0`
* `Pillow` (image fields)
* `mysqlclient` (production database)
* `python-dotenv` (loads environment variables)

### Databases
* SQLite (`db.sqlite3`) for local development.
* MySQL on PythonAnywhere. The database block is switched by hand in `config/settings.py`.

### Hosting
PythonAnywhere (`bunnypraneeth.pythonanywhere.com`) through the WSGI entry point `config/wsgi.py`. `DEBUG`, `SECRET_KEY` and `ALLOWED_HOSTS` come from the environment.

---

## 2. Request lifecycle

`config/urls.py` -> `portfolio/urls.py` -> view in `portfolio/views.py` -> template in `templates/`.

On every request:
* `portfolio.middleware.RequestMemoMiddleware` opens a per-request memo so `SiteSettings.load()` hits the database once per page, however many templates and helpers call it. Outside a request (shell, management commands) nothing is cached.
* Context processors in `portfolio/context_processors.py`:
  * `site_settings`: `site_settings`, `profile_image_url`, `absolute_profile_image_url` (for Open Graph), `default_meta_description` (Site Settings meta description, or the hero description trimmed to 160 characters), `resume_url`, and `site_last_updated` (a callable the footer calls once: newest `updated_at` across published projects and logs, About and Site Settings; 3 small queries).
  * `chat_helper`: greeting text and suggested question chips for the chat widget.

### Routes
| URL | View | Template |
| --- | --- | --- |
| `/` | `index` | `index.html` |
| `/about/` | `about_view` | `about.html` |
| `/skills/` | `skills_view` | `skills.html` (Toolkit: core cards and areas, each skill with the published cases whose tags match it) |
| `/projects/` | `projects_view` | `projects.html` (Case board: featured cases + archive table) |
| `/projects/<slug>/` | `project_detail` | `project_detail.html` (case file) |
| `/blog/` | `blog_view` | `blog.html` (logs, grouped by year) |
| `/blog/<slug>/` | `blog_detail` | `blog_detail.html` (side rail, older and newer links) |
| `/contact/` | `contact_view` | `contact.html` |
| `/api/chat/` (POST) | `chat_reply` | JSON |
| `/admin/` | Django admin | |

Favicon and manifest paths redirect to `static/favicon_io/`.

### Templates
All pages extend `templates/base.html`, which holds the head (meta description, Open Graph and Twitter tags as overridable blocks), navigation, footer, the chat widget (`pet_widget.html`) and the deferred scripts. The full contact section (`partials/contact_section.html`) appears only on the home page, case files and log posts; other pages keep the contact link in the nav and footer.

### Static files
* `static/styles.css`: design tokens at the top, then base reset, layout and page styles.
* `static/script.js`: background layers and mobile navigation.
* `static/chat_widget.js`: chat helper.
* `static/replay.js`: recorded agent replay player on case files.
* `static/admin.css`: admin styling.

---

## 3. Data models (`portfolio/models.py`)

| Model | Purpose |
| --- | --- |
| `SiteSettings` | Singleton (`load()`). Hero text and buttons, profile image, resume, social links, contact details, contact form toggle, meta title and description, and job search fields (`job_search_mode`: open, quiet or not looking, plus the replies and preferences the chat helper uses). |
| `About` | Bio paragraphs, `off_duty` and `pull_quote` cards, `updated_at`. Stat fields are kept in admin but no longer shown (Phase 8.4). |
| `Skill` | Name, category, featured flag (shown as Core). |
| `Project` | Case file: slug, case number, summaries, brief, architecture notes, open leads, metrics, links, thumbnail, tech tags, status, featured and published flags, and Case board fields `role`, `year`, `project_type`, `one_liner` (homepage roster), `personal_note` (Field note on the case file), `updated_at`. |
| `CaseDecision`, `CaseIncident` | Inline rows on a project (foreign key to `Project`). |
| `ProjectReplay` | Recorded agent run shown on a case file (foreign key to `Project`). Validated by `portfolio/replays.py`. |
| `BlogPost` | Log entry with `log_type`, optional `related_project` (shown as "Filed under" and listed on that case file while the case is published), `reading_minutes` (200 words a minute). |
| `ContactMessage` | Contact form submissions. |
| `ChatAnswer` | One topic the chat helper can answer: keywords, synonyms, answer text, priority, review flag, job-search-mode flag. |
| `SuggestedQuestion` | Clickable chips in the chat helper. |
| `ChatQuery` | Questions asked in the chat helper, emails and phone numbers scrubbed, no IP, 90-day retention. |
| `ExperienceEntry` | Real roles only, optional link to a related project. |
| `Certification`, `EducationEntry`, `EventEntry`, `WhatIDo` | About page sections. `Certification.is_featured` shows a certificate as a large card; the rest are chips. |

### Chat helper
`chat_widget.js` posts to `/api/chat/`. `portfolio/chatbot.py` normalises the question, applies synonyms, corrects typos with `difflib`, scores `ChatAnswer` keyword matches and also matches project titles and tags. Answers respect `SiteSettings.job_search_mode`. The evaluation set lives in `portfolio/chat_eval.py` and runs in the test suite.

### Replays
A replay is a JSON file (format in `docs/REPLAY_FORMAT.md`). It can be uploaded in the admin on a `ProjectReplay`, or imported with:
```bash
python manage.py import_replay <project-slug> <file.json>
```
Both paths use the same validator in `portfolio/replays.py`.

---

## 4. Admin

Every model above is registered in `portfolio/admin.py`. `SiteSettings` is a singleton (no add after the first row, no delete). Project decisions, incidents and replays are edited on the project page. See `ADMIN_GUIDE.md` for how to fill each section.

---

## 5. Static, media and configuration

* Static: `STATIC_URL=/static/`, `STATICFILES_DIRS=[static]`, `STATIC_ROOT=staticfiles` (run `collectstatic` on deploy).
* Media: `MEDIA_URL=/media/`, `MEDIA_ROOT=media`. Upload folders: `appearance/` (profile image), `resume/`, `projects/`, `blog/`, `certificates/`.
* With `DEBUG=True`, Django serves static and media files itself.

### Environment variables (names from `.env.example`)
`DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.

---

## 6. Known gaps

* Static files are served without versioned names, so browsers can keep an old `styles.css` after a deploy. `ManifestStaticFilesStorage` would fix this; not enabled yet.

* `SECURE_PROXY_SSL_HEADER` is not set. Behind the PythonAnywhere proxy, `request.build_absolute_uri()` may produce `http://` URLs, which affects `og:url` and `og:image`.
* Text compression (gzip) is a server setting and is not handled by the app.
* The database engine is switched by hand in `config/settings.py`.

---

## 7. Local setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Run the tests with `python manage.py test portfolio`.
