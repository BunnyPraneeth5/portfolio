# CLAUDE.md

Personal portfolio for Karu Praneeth Kumar (Bunny). Full plan: `docs/REDESIGN_PLAN.md`. Tasks: `TASKS.md`. Log: `PROGRESS.md`.

## Stack
- Django 5.2, project `config`, single app `portfolio`. Python venv in `venv/` (`venv/Scripts/python.exe`).
- Local DB: SQLite (`db.sqlite3`). Production: MySQL on PythonAnywhere (Bunny switches DB in `config/settings.py` by hand).
- Standalone templates in `templates/` (they do NOT extend `base.html`), CSS in `static/styles.css`, JS in `static/script.js`.
- Tailwind 2 + Font Awesome via CDN in templates. Vanilla JS only. No React, no build step.
- Chat widget: `templates/pet_widget.html` -> `POST /api/chat/` -> `portfolio/chatbot.py` (rule-based keywords, no LLM).

## Key models (`portfolio/models.py`)
- `SiteSettings` (singleton, `load()`), `About`, `Project` (slug, `/projects/<slug>/`), `Skill`, `BlogPost`
- `ExperienceEntry` (today mixes roles and certificates), `AdditionalCertification`, `EducationEntry`, `EventEntry`, `WhatIDo`
- `SiteAppearance` (legacy colour vars, slated for Phase 1), `ContactMessage`

## Boundaries
- Never read, print, create or edit `.env` or any secret. Never hardcode keys, emails or passwords.
- Never deploy. Only Bunny deploys to PythonAnywhere.
- Never delete files in `media/`. Never commit `db.sqlite3`, `media/` or raw logs.

## Rules
- Stay in scope of the current phase. Stop at the end of a phase and wait for Bunny's go.
- No new dependencies without asking.
- Don't touch files unrelated to the current task.
- Don't invent content about Bunny (roles, projects, bugs, metrics, dates). Use `[TODO: Bunny]` or an empty admin field.
- If the plan conflicts with the code, stop and ask. Don't guess.
- One clearly named migration set per phase.
- Run `venv/Scripts/python.exe manage.py test portfolio` before starting and before saying done. Never claim done with failing tests.
- Update `TASKS.md` and add a `PROGRESS.md` entry at the end of each session.

## Current focus
Phase 0: split Professional Experience from Certifications, on the current styling. No redesign work.
