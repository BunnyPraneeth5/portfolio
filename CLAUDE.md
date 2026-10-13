# CLAUDE.md

Portfolio for Karu Praneeth Kumar (Bunny). Plan: `docs/REDESIGN_PLAN.md`. Tasks: `TASKS.md`. Log: `PROGRESS.md`. Decisions: `DECISIONS.md`.

## Stack
- Django 5.2, project `config`, single app `portfolio`. Venv: `venv/Scripts/python.exe`. SQLite locally, MySQL on PythonAnywhere (DB switched by hand in `config/settings.py`).
- Pages in `templates/` extend `base.html` (head, nav, scripts, pet widget). CSS in `static/styles.css` (design tokens at the top; use them, no new hardcoded colours), admin CSS in `static/admin.css`. No CSS/JS libraries (Google Fonts only). Vanilla JS, no build step. Full contact section only on home, case files and logs.
- Chat helper: `templates/pet_widget.html` + `static/chat_widget.js` -> `POST /api/chat/` -> `portfolio/chatbot.py`. Topics/keywords/answers live in `ChatAnswer` (admin); eval set in `portfolio/chat_eval.py`. Respect `SiteSettings.job_search_mode`.
- Replays: `ProjectReplay` + shared validator `portfolio/replays.py` (admin upload and `import_replay` command), player `static/replay.js`. Format: `docs/REPLAY_FORMAT.md`.

## Key models (`portfolio/models.py`)
- `SiteSettings` (singleton, `load()`), `About`, `Project` (slug, `/projects/<slug>/` case file; `CaseDecision`, `CaseIncident` inlines), `Skill`, `BlogPost`, `ContactMessage`
- `ExperienceEntry` (real roles only), `Certification`, `EducationEntry`, `EventEntry`, `WhatIDo`

## Boundaries
- Never read, print, create or edit `.env` or any secret. Never hardcode keys, emails or passwords.
- Never deploy. Only Bunny deploys to PythonAnywhere. Never delete files in `media/`. Never commit `db.sqlite3`, `media/` or raw logs.

## Rules
- Stay in scope of the current phase. Stop at the end of a phase and wait for Bunny's go.
- No new dependencies without asking. Don't touch files unrelated to the current task.
- If the plan conflicts with the code, stop and ask. Don't guess. One clearly named migration set per phase.
- Run `venv/Scripts/python.exe manage.py test portfolio` before starting and before saying done. Never claim done with failing tests.
- Update `TASKS.md` and add a `PROGRESS.md` entry at the end of each session.

## Public content rules (anything visitors see)
- Don't invent content about Bunny (roles, projects, bugs, metrics, dates). Use `[TODO: Bunny]` or an empty admin field.
- Ask Bunny before writing any claim about Bunny.
- No fake or unverifiable metrics. No vague hero text. No filler or lorem text.
- No emoji icons. No em dashes in site copy.
- No heavy animations. Avoid the generic template look.

## Current focus
Phase 8 (page redesigns) in progress, step by step. See TASKS.md.
