# TASKS

Current phase: **Phase 0 — Split Experience and Certifications** (see `docs/REDESIGN_PLAN.md` §3).
Uses current styling. No redesign work. Tasks marked BLOCKED need an answer from Bunny first.

Status key: `[ ]` todo · `[~]` in progress · `[x]` done · `BLOCKED` waiting on Bunny

---

## 0.1 Decisions from Bunny — BLOCKED
- [ ] For each current `ExperienceEntry`, mark it **role** or **certificate**:
      Anthropic Academy / MCP Certification · TATA / Data Visualization (Virtual Internship) ·
      HackerRank / Python & Problem Solving · Kaggle / Python Certification ·
      Deloitte / Data Analytics & Cyber Security (Virtual Internship). Confirm production has the same rows.
- [ ] Entries with two certificate files (HackerRank, Deloitte): split into two `Certification` rows, or one row with two files?
- [ ] Drop `ExperienceEntry.side` (unused by the template)? Drop `icon_class` / `icon_color` from `ExperienceEntry`?
- [ ] Keep `year_label`, or derive the date label from `start_date` / `end_date`?
- [ ] Chatbot `experience` reply: keep `EventEntry` (hackathon/leadership) lines after the roles, or split them out?

**Acceptance:** every question above has a written answer in `PROGRESS.md`.

## 0.2 Add new fields and `Certification` model (schema only)
- [ ] Add to `ExperienceEntry`: `employment_type` (internship, part_time, full_time, contract, freelance), `start_date`, `end_date` (optional), `is_current`, `location` (optional), `is_remote`, `summary`, `highlights`, `related_project` (FK `Project`, `SET_NULL`, optional).
- [ ] New `Certification`: `title`, `issuer`, `issued_date` (opt), `certificate_file` (opt), `credential_url` (opt), `order`.
- [ ] New fields must be nullable/blank or have defaults so existing rows migrate without guessed data.

**Acceptance:** one clearly named migration; `migrate` runs clean on a copy of local SQLite; no existing data changed; tests pass.

## 0.3 Data migration: move certificates — depends on 0.1, 0.2
- [ ] Copy every `AdditionalCertification` into `Certification` (title, file, order). Issuer left blank unless known.
- [ ] Copy the `ExperienceEntry` rows Bunny marked as certificates into `Certification` (organization → issuer, role → title, files per 0.1), then delete those rows.
- [ ] Match rows by the identifiers Bunny confirms, not by guessing. Files stay where they are in `media/`.
- [ ] Reverse migration restores the moved rows.

**Acceptance:** after migrate, cert count = old `AdditionalCertification` count + moved entries (+ splits); every file path still resolves; no file in `media/` deleted; migrate → rollback → migrate works on SQLite.

## 0.4 Remove old structures — depends on 0.3 confirmed by Bunny
- [ ] Remove `AdditionalCertification` model and admin.
- [ ] Remove `certificate_file`, `certificate_file_2` (and `side` / `icon_*` / `year_label` if 0.1 says so) from `ExperienceEntry`.
- [ ] Remove unused `experience_left` / `experience_right` from `about_view`.

**Acceptance:** separate migration; `makemigrations --check` clean; `grep` finds no references to removed fields/models in code or templates; tests pass.

## 0.5 Admin
- [ ] `ExperienceEntry` admin: fieldsets Role / Dates / Details / Links; `list_display` organization, role, employment type, start, end, is_current.
- [ ] `Certification` admin: `list_display` title, issuer, issued_date, has file (boolean column).
- [ ] Verbose names: "Professional Experience" and "Certifications".
- [ ] Update `ADMIN_GUIDE.md` sections 7 and 9.

**Acceptance:** Bunny can add an internship with summary and highlights in admin without errors; admin index shows the new labels.

## 0.6 About page
- [ ] Professional Experience timeline: organization, role, type badge, date range ("Present" if current), location / Remote, summary.
- [ ] Highlights in `<details>`/`<summary>`, one bullet per line, closed by default.
- [ ] "See the project →" link when `related_project` is set and published.
- [ ] Remove the hardcoded "Credential" badge.
- [ ] Replace "Additional Certifications" with "Certifications": title, issuer, date, "View certificate" link (only if a file or URL exists).
- [ ] Sections with no entries are hidden.

**Acceptance:** no "Credential" text on `/about/`; all certificates listed with working links; layout OK at 390px and desktop in current styling.

## 0.7 Homepage "Recent" line
- [ ] `index` view passes the latest `ExperienceEntry` by `start_date`.
- [ ] Hero shows "Recent: <role> at <organization>"; hidden when there is none.

**Acceptance:** line appears with one entry, disappears with none; tests cover both.

## 0.8 Chatbot
- [ ] `experience` reply reads new fields: latest role first, then others (+ events per 0.1).
- [ ] `certifications` reply lists `Certification` titles (short list); remove the hardcoded fallback certificate names.
- [ ] Questions like "tell me about your internship" currently hit the `internship` (availability) intent; route past-internship questions to `experience` without breaking "are you open to internships".

**Acceptance:** wording style unchanged; tests for both replies with and without data, and for the internship routing.

## 0.9 Tests and wrap-up
- [ ] Tests: new models (str, ordering, date label/"Present"), About sections, homepage line, chatbot replies.
- [ ] Full test suite passes; `makemigrations --check` clean.
- [ ] Note for Bunny: migrations to run on PythonAnywhere MySQL, DB backup first (MySQL run not verifiable locally).

**Acceptance:** all Phase 0 "Done when" items in the plan are true, except the MySQL run, which Bunny confirms.
