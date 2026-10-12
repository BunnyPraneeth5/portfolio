# CLAUDE.md

Portfolio for Karu Praneeth Kumar (Bunny). Plan: `docs/REDESIGN_PLAN.md`. Tasks: `TASKS.md`. Log: `PROGRESS.md`. Decisions: `DECISIONS.md`.

## Stack
- Django 5.2, project `config`, single app `portfolio`. Venv: `venv/Scripts/python.exe`. SQLite locally, MySQL on PythonAnywhere (DB switched by hand in `config/settings.py`).
- Pages in `templates/` extend `base.html` (head, nav, scripts, pet widget). CSS in `static/styles.css` (design tokens at the top; use them, no new hardcoded colours), admin CSS in `static/admin.css`. Tailwind 2 + Font Awesome via CDN. Vanilla JS, no build step.
- Chat widget: `templates/pet_widget.html` -> `POST /api/chat/` -> `portfolio/chatbot.py` (rule-based keywords, no LLM).

## Key models (`portfolio/models.py`)
- `SiteSettings` (singleton, `load()`), `About`, `Project` (slug, `/projects/<slug>/`), `Skill`, `BlogPost`, `ContactMessage`
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
Phase 2 implemented, waiting for Bunny's review. Next: Phase 3 (case file project pages).
