# PROGRESS

Newest entry at the top.

---

## 2026-10-12 — Session 1: plan review and setup

**Phase:** 0 (not started; setup only)

**Done**
- Read `docs/REDESIGN_PLAN.md` and the codebase (models, views, urls, admin, chatbot, templates, top of `styles.css`).
- Gap check between plan and code (results shared in chat; open questions copied to `TASKS.md` 0.1).
- Created `CLAUDE.md`, `TASKS.md`, `PROGRESS.md`.
- No app code changed.

**State**
- `venv/Scripts/python.exe manage.py test portfolio`: 8 tests, all pass (Django 5.2.16).
- Local DB has 5 `ExperienceEntry` rows (all look like certificates / virtual internships) and 3 `AdditionalCertification` rows. The new internship is not in the DB yet.

**Open questions for Bunny** — see `TASKS.md` 0.1.

**Next**
- Get answers to 0.1, then start 0.2 (schema migration).
