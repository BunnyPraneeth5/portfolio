# TASKS

Current phase: **Phase 0 — Split Experience and Certifications** (see `docs/REDESIGN_PLAN.md` §3).
**Status: implemented, waiting for Bunny's review + MySQL migration test.** Bunny still needs to add the internship in admin.
Uses current styling. No redesign work.

Status key: `[ ]` todo · `[~]` in progress · `[x]` done · `BLOCKED` waiting on Bunny

---

## 0.1 Decisions from Bunny
- [x] Answered 2026-10-12. Recorded in `docs/REDESIGN_PLAN.md` Phase 0 "Decisions confirmed by Bunny".

## 0.2 Add new fields and `Certification` model (schema only)
- [x] Add to `ExperienceEntry`: `employment_type` (internship, part_time, full_time, contract, freelance), `start_date` (null), `end_date` (null), `is_current`, `location`, `is_remote`, `summary`, `highlights`, `related_project` (FK `Project`, `SET_NULL`, null).
- [x] New `Certification`: `title`, `issuer`, `category` (opt), `issued_date` (opt), `certificate_file` (opt), `certificate_file_2` (opt), `credential_url` (opt), `order`.

**Acceptance:** clearly named migration; existing data unchanged; tests pass.

## 0.3 Data migration: move all certificates
- [x] Every `AdditionalCertification` → `Certification` (title, file, order).
- [x] Every `ExperienceEntry` → `Certification` (organization → issuer, role → title, year_label → category, both files, order), then delete the entry.
- [x] RunPython only, no raw SQL. Reverse migration restores the rows.
- [x] Files stay where they are in `media/`.

**Acceptance:** cert count = old AdditionalCertification + old ExperienceEntry count; every file path unchanged; migrate → rollback → migrate works on a copy of local SQLite.

## 0.4 Remove old structures
- [x] Remove `AdditionalCertification` model and admin.
- [x] Remove `year_label`, `certificate_file`, `certificate_file_2`, `icon_class`, `icon_color`, `side` from `ExperienceEntry`.
- [x] Remove unused `experience_left` / `experience_right` from `about_view`.

**Acceptance:** `makemigrations --check` clean; no references to removed fields/models in code or templates; tests pass.

## 0.5 Admin
- [x] `ExperienceEntry` admin: fieldsets Role / Dates / Details / Links; `list_display` organization, role, employment type, start, end, is_current. Form requires `start_date`.
- [x] `Certification` admin: `list_display` title, issuer, category, issued_date, has file.
- [x] Verbose names: "Professional Experience" and "Certifications".
- [x] Update `ADMIN_GUIDE.md`.

**Acceptance:** an internship can be added in admin with summary and highlights; saving without `start_date` shows an error.

## 0.6 About page
- [x] Professional Experience timeline: organization, role, type badge, date range ("Present" if current), location / Remote, summary.
- [x] Highlights in `<details>`/`<summary>`, one bullet per line, closed by default.
- [x] "See the project →" link when `related_project` is set and published.
- [x] Remove the hardcoded "Credential" badge.
- [x] "Certifications" section: title, issuer, date, "View certificate" link(s).
- [x] Sections with no entries are hidden.
- [x] Fix broken ✓ in education bullets.

**Acceptance:** no "Credential" text on `/about/`; all certificates listed with working links.

## 0.7 Homepage "Recent" line
- [x] `index` view passes the latest `ExperienceEntry` by `start_date`.
- [x] Hero shows "Recent: <role> at <organization>"; hidden when none.

**Acceptance:** tests cover both cases.

## 0.8 Chatbot
- [x] `experience` reply: roles (latest first), then "Hackathons and leadership" events.
- [x] `certifications` reply lists `Certification` titles.
- [x] No hardcoded fallback content: empty tables → say so and point to /about/.
- [x] Routing: "open to internships" → `internship`; "your internship", "where did you work", "work experience" → `experience`.

**Acceptance:** tests for both replies with and without data, and for the routing.

## 0.9 Cleanup and tests
- [x] Delete `portfolio/_tmp_widget_smoke.py`.
- [x] `test_projects_view` creates its own Project rows.
- [x] Tests: new models, About sections, homepage line, chatbot replies.
- [x] Full suite passes; `makemigrations --check` clean.
- [x] Deploy note for Bunny (backup, migrate on MySQL). — in PROGRESS.md; MySQL run pending Bunny

---

## Phase 1 (later) — notes carried forward
- [ ] **First task:** convert all public templates to extend `base.html`.
- Note: `SiteAppearance` vars are injected into all 8 public templates + admin "Appearance" shortcut.
- Note: fonts — Outfit/Cormorant/JetBrains via `styles.css`, Orbitron/Space Grotesk via templates; IBM Plex Sans not loaded.

## Phase 7 (later) — notes carried forward
- `ARCHITECTURE.md` still describes the old `ExperienceEntry` / `AdditionalCertification` fields. Rewrite with the Phase 7 docs update.
