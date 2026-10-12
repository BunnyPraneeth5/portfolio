# PROGRESS

Newest entry at the top.

---

## 2026-10-12 — Session 4: Phase 2 committed, Phase 3 implemented

**Phase 2:** committed as `e9ecda3` on `redesign/phase-0`.

**Phase 3:** done locally, waiting for review.

**Decisions from Bunny:** Brief falls back to `long_description`; stamp wording per plan mapping; empty case number hides the number.

**Done**
- `Project` case file fields + `CaseDecision` / `CaseIncident` models, admin inlines (migration 0020). `ADMIN_GUIDE.md` updated.
- `project_detail.html` rebuilt as a case file: top bar, title block with stamp, evidence strip, sticky section nav, sections that hide when empty, previous/next case.
- Thumbnail fallback partial used on the case file and /projects/ cards.
- Tests 34 → 43, all pass.
- Browser: temporary fully-filled project checked at desktop and phone, then deleted.

**Correction to Phase 1:** the dead-CSS pass removed `.project-thumbnail--soc/ml/gate/ai` because the template built those class names with `{% cycle %}`, which my scan did not detect. Visual impact was small (the base placeholder styling stayed; only the four tints were lost), and Phase 3 replaced that fallback entirely. Future CSS cleanups should also check for dynamically built class names.

**Deploy note for Bunny:** back up MySQL, pull, `migrate` (0020), `collectstatic`, reload.

**Next**
- Bunny: review Phase 3; write case file content in admin (SOC Copilot first).
- Then Phase 4 (replay feature).

## 2026-10-12 — Session 3: Phase 1 committed, Phase 2 implemented

**Phase 1:** committed as `34039c1` on `redesign/phase-0`.

**Phase 2:** done locally, waiting for review.

**Decisions from Bunny:** nav = Agents, Cases, Logs, About, Contact; replay shell hidden until Phase 4; portrait off the homepage.

**Done**
- Homepage rebuilt: status line, name, roles, recent role, pitch, three buttons, 30-second view panel, agent roster table, hidden replay shell, latest 3 logs.
- New fields: `SiteSettings.looking_for`, `Project.status` (migration 0019). Admin updated; `ADMIN_GUIDE.md` updated.
- Header: `KP OPS://BUNNY` brand and new nav. Contact section + footer added to every page via `base.html` (contact section skipped on /contact/).
- Removed: splash screen, scroll progress bar, rotating roles (incl. a hardcoded fallback role list in JS), old homepage CSS, client-side nav active override.
- Tests 27 → 34, all pass.
- Browser checks: desktop 1440x900 shows who/role/best work/contact above the fold; 390px has no page overflow (roster scrolls inside); nav highlighting correct on each page; mobile menu works; homepage colours/fonts clean.

**Deploy note for Bunny:** back up MySQL, pull, `migrate` (0019), `collectstatic`, reload. Browsers may need a hard refresh for the new `script.js`.

**Next**
- Bunny: review Phase 2; fill `Looking for` and project `Status` in admin.
- Then Phase 3 (case file project pages).

## 2026-10-12 — Session 2: Phase 1 implemented

**Phase:** 1 (done locally, waiting for review). Same branch `redesign/phase-0`.

**Decision from Bunny:** delete `SiteAppearance` entirely.

**Done**
- All 8 public templates extend `base.html`. Verified by snapshotting rendered HTML before and after: identical apart from whitespace.
- Design tokens + spacing/radius scale at the top of `styles.css`; old variable names aliased; hardcoded colours/fonts swapped for tokens.
- Fonts: Cormorant Garamond / IBM Plex Sans / JetBrains Mono loaded once in `base.html`; Orbitron, Space Grotesk, Outfit removed.
- `SiteAppearance` removed (model, admin, context processor, settings, admin link, ADMIN_GUIDE). Migration `0018_delete_siteappearance` applied locally.
- Components: `.btn-primary`, `.btn-ghost`, `.panel`, `.label-mono`, `.status-dot`, `.stat-tile`, `.section-head` (+ `.text-accent`, `.form-input`). Template buttons/links/inputs moved onto them.
- Dead CSS: 71 unused selectors removed (2702 → ~2340 lines before components were added).
- Admin restyled on the same tokens.
- Fixes found while checking: page titles were rendering in the body font (global `span` rule); contact submit button was overridden by an old generic rule.
- Tests 25 → 27, all pass.
- Browser checks: computed-colour audit on all 8 pages + admin finds no blue/purple/cyan; only the three fonts in use; no horizontal scroll at 390px. A temporary admin user/session used for the admin check was deleted afterwards.

**Deploy note for Bunny:** back up MySQL, pull, `python manage.py migrate` (applies 0018), `collectstatic`, reload.

**Next**
- Bunny: review Phase 1. Then Phase 2 (homepage rebuild).

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
