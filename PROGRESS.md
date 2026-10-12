# PROGRESS

Newest entry at the top.

---

## 2026-10-12 — Session 1b: Phase 0 implemented

**Phase:** 0 (done locally, waiting for review)

**Decisions from Bunny (0.1):** recorded in `docs/REDESIGN_PLAN.md` Phase 0. Short version: all 5 `ExperienceEntry` rows + all `AdditionalCertification` rows become `Certification`; second file field kept; `side`, `icon_*`, `year_label` (→ `Certification.category`), `see_experience_note` dropped; events stay in the chat experience reply.

**Done**
- Migrations: `0015_experience_fields_and_certification` (schema), `0016_move_certificates_to_certification` (RunPython, reversible), `0017_remove_legacy_experience_and_additional_certification`.
- Local SQLite: 5 + 3 rows → 8 `Certification` rows, file paths unchanged, old About order kept. Migrate → rollback to 0014 → migrate verified. Backup of the pre-migration DB kept outside the repo.
- Admin: "Professional Experience" (fieldsets Role/Dates/Details/Links, start date required, end date validated) and "Certifications" (has-file column). `ADMIN_GUIDE.md` updated.
- About: new experience timeline (type badge, date range/Present, location/Remote, summary, collapsible Highlights, project link), "Certifications" list, no "Credential" badge, empty sections hidden, ✓ character fixed.
- Homepage: "Recent: <role> at <organization>" line, hidden when no roles.
- Chatbot: experience reply (roles newest first, then "Hackathons and leadership"), certifications reply from `Certification`, no hardcoded fallback content, new `past_work` intent so "your internship / where did you work / your experience" go to experience while "open to internships" stays on availability.
- Deleted `portfolio/_tmp_widget_smoke.py`; `test_projects_view` creates its own projects.
- Tests: 8 → 25, all pass. `makemigrations --check` clean.
- Checked visually at 1024px and 390px (no horizontal scroll) with a temporary role, then deleted it.

**Deploy note for Bunny (PythonAnywhere)**
1. Back up the MySQL DB first.
2. Check in admin that production has only certificate rows under the old Experience entries (all of them will move).
3. Pull, then `python manage.py migrate` (applies 0015–0017), `python manage.py collectstatic`, reload the web app.
4. Check `/about/` Certifications and that every "View certificate" link opens.

**Next**
- Bunny: review, test migrations on MySQL, add the internship in admin.
- Then Phase 1 (first task: templates extend `base.html`).

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
