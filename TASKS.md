# TASKS

Current phase: **Phase 4 — Replay feature** (see `docs/REDESIGN_PLAN.md` §3).
**Status: implemented, waiting for Bunny's review.** Phases 0 to 3 committed on `redesign/phase-0`.

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

## Phase 1 — Cleanup and design system

## 1.0 Templates extend `base.html`
- [x] All 8 public templates extend `base.html` (head, nav, mobile menu, scripts, pet widget). Active nav link comes from the URL name.

**Acceptance:** rendered HTML of all 8 pages identical to before (whitespace ignored). Verified.

## 1.1 Remove leftover file
- [x] `portfolio/_tmp_widget_smoke.py` (done in Phase 0).

## 1.2 Design tokens
- [x] Tokens at the top of `static/styles.css`: colours, three font families, spacing scale (`--space-1..8`), radius (4px buttons, 6px panels). Old variable names aliased onto tokens.
- [x] Hardcoded hex colours and fonts in `styles.css` replaced with tokens; faint blue glows turned gold.

## 1.3 Fonts
- [x] Cormorant Garamond, IBM Plex Sans, JetBrains Mono loaded once in `base.html`. Orbitron, Space Grotesk, Outfit and the CSS `@import` removed. `font-['Orbitron']` class renamed `font-display`.

**Acceptance:** computed fonts on all 8 pages are only the three fonts (+ Font Awesome). Verified.

## 1.4 Remove blue/purple/cyan + `SiteAppearance` (Bunny chose: delete)
- [x] `SiteAppearance` model, admin, context processor, settings entry, admin shortcut, `ADMIN_GUIDE.md` section removed. Migration `0018_delete_siteappearance`.
- [x] Blue/purple Tailwind classes in templates replaced with design-system classes. Decorative ping dots and a dead `{% comment %}` block in `about.html` removed.

**Acceptance:** computed-colour audit finds no blue/purple/cyan on any of the 8 pages or the admin. Verified.

## 1.5 Components
- [x] `.btn-primary`, `.btn-ghost`, `.panel` (+ `.panel--deep`), `.label-mono`, `.status-dot`, `.stat-tile`, `.section-head`, `.text-accent`, `.form-input`.
- Primary/secondary buttons, accent links and contact inputs already use them. `.panel`, `.status-dot`, `.stat-tile`, `.section-head` are ready for Phase 2.

## 1.6 Dead CSS
- [x] Removed 71 selectors for classes no template, script or Python file uses (old colour overrides, engineering/project-node visuals, old project/skill card classes). Kept the Tailwind utility shims and the new components.

## 1.7 / 1.8 Admin
- [x] `static/admin.css` rewritten on the same tokens and fonts (Django admin variables overridden for light and dark themes; theme toggle hidden). Admin header fonts swapped; Appearance link removed.

**Acceptance:** admin index, changelist and add form readable; no blue/purple in computed styles. Verified.

## Phase 1 checks
- [x] 27 tests pass; `makemigrations --check` clean.
- [x] No horizontal scroll at 390px on all 8 pages; desktop checked at 1440px.

## Phase 2 — Homepage rebuild (ops console)
Decisions (Bunny, 2026-10-12): nav = Agents, Cases, Logs, About, Contact; replay shell hidden until Phase 4; no portrait on the homepage.

## 2.1 Splash
- [x] Opening splash removed (markup, CSS, JS). Homepage content has no fade-in delay.

## 2.2 Header
- [x] `KP` + `OPS://BUNNY` brand; nav Agents (`/#agents`), Cases, Logs, About, Contact. Mobile menu kept (now sets `aria-expanded`).
- [x] Active link set server-side only; script.js no longer overrides it. Same-page anchors scroll instead of fade + reload.

## 2.3 Hero
- [x] Teal status line "Open to roles · <location>" when `open_to_work`; name; roles on one line; Recent role line; pitch; buttons View agents / Resume / Contact.
- [x] Rotating-role animation removed (and its hardcoded fallback roles).

## 2.4 30-second view
- [x] Looking for (new `SiteSettings.looking_for`, hidden when empty), Best work (Flagship project, else first featured), Degree (first `EducationEntry`), Core stack (featured skills, max 8), Location (+ open to remote), Notice period, Links.

## 2.5 Agent roster
- [x] Table of published projects by `order`: agent (title + short description), stack (first 4 tags), key metric (metric 1), status. Whole row links to the case file. Scrolls inside its box on phone.
- [x] New `Project.status` (flagship, live, benchmarking, archived; blank hides the badge) in admin list + form.

## 2.6 Replay preview
- [x] Shell partial `templates/partials/replay_preview.html`, rendered only when `replay_preview` is set (Phase 4).

## 2.7 From the logs
- [x] Latest 3 published posts; section hidden when none.

## 2.8 Contact section + footer
- [x] `partials/contact_section.html` on every page except /contact/ (email, location, links, Send a message / Resume). Heading = `SiteSettings.contact_tagline`.
- [x] `partials/site_footer.html` on every page.

## 2.9 Spacing
- [x] One heading per section (mono label + different heading text). Consistent section spacing; anchored sections clear the fixed header.

## Phase 2 checks
- [x] Migration `0019_sitesettings_looking_for_project_status`. 34 tests pass.
- [x] 1440x900: who, role, best work and contact visible without scrolling.
- [x] 390px: no horizontal page scroll on all pages; roster scrolls inside its own box.
- [x] Computed-colour audit on the homepage: no blue/purple; only the three fonts.

## Content for Bunny (not code)
- `Looking for` is empty: fill it in Site Settings to show the row.
- Set `Status` on each project (SOC Copilot as Flagship?) so roster badges and Best work are deliberate.
- The hero pitch (`Hero description`) is three lines with manual line breaks; the plan asks for one line.

## Phase 3 — Case file project pages
Decisions (Bunny, 2026-10-12): Brief falls back to `long_description`; stamp mapping as in the plan; empty case number hides the number.

## 3.1 Models + admin
- [x] `Project`: `case_number`, `brief`, `architecture_notes`, `open_leads` (all optional). Helpers: `case_label`, `status_stamp`, `brief_text`, `open_leads_list`, `metrics`.
- [x] `CaseDecision` (code, decision, tradeoff, order) and `CaseIncident` (symptom, root cause, fix, order) as stacked inlines on the Project admin. "Case file" fieldset added. Migration `0020_project_case_file`.

## 3.2 Case file template
- [x] Top bar: back to roster (`/#agents`), breadcrumb CASES / 00X.
- [x] Title block: CASE FILE NO. 00X, title, short description, status stamp.
- [x] Evidence strip: metric tiles (metric 1 to 3), stack tags, View code / Live demo.
- [x] Section nav (sticky on desktop, inline on phone): Brief, Investigation, Decisions, Incidents, Replay (Phase 4), Open leads. Each section and its nav link render only with content.
- [x] Previous / next case by `order` among published projects.

## 3.3 Thumbnail fallback
- [x] `partials/case_thumb.html`: image, or a styled "Case file" placeholder. Used on the case file and the /projects/ cards (replaces the old `project-thumbnail--{soc,ml,gate,ai}` classes).

## Phase 3 checks
- [x] 43 tests pass (detail view with and without decisions/incidents, empty sections hidden, brief fallback, prev/next, 404 for unpublished, admin inlines).
- [x] Browser: a temporary fully-filled project checked at 1440px and 390px (then deleted); SOC Copilot renders with only existing data.

## Content for Bunny (Phase 3)
- Per project: brief, architecture notes, 2 to 3 decisions, 1 to 2 incidents, open leads, and a case number if you want one. SOC Copilot first.
- Local DB: SOC Copilot's long description is placeholder keyboard text; check production's.

## Phase 4 — Replay feature
Decision (Bunny, 2026-10-12): validator also blocks obvious leaks (emails, tokens, public IPs).

## 4.1 Model
- [x] `ProjectReplay` (project, title, duration_s, steps JSON, is_published default off, is_featured_on_home unique, order). Migration `0021_projectreplay`.

## 4.2 Shared validator (`portfolio/replays.py`)
- [x] Schema, kinds, time order, t within duration, 300-step cap, 500-char text cap, 512 KB file cap, readable per-step errors, leak checks.

## 4.3 Admin upload
- [x] JSON upload field on the ProjectReplay form runs the validator and fills steps (and title/duration if empty).

## 4.4 Management command
- [x] `import_replay <project_slug> <path.json>` with `--publish`, `--feature-on-home`, `--title`, `--order`; same validator; clear `CommandError` on bad files.

## 4.5 Converter (optional)
- [ ] Not built. Raw logs stay out of the repo. Revisit if Bunny wants a helper in `tools/` (git-ignored).

## 4.6 Player (`static/replay.js`)
- [x] Play/pause/resume, restart, speed 1x/2x, progress bar, steps typed in order and coloured by kind, auto-scroll, textContent only.
- [x] `prefers-reduced-motion`: all steps shown at once, controls hidden. Server-rendered transcript works without JS.

## 4.7 Placement
- [x] Homepage Replay section (featured first, switcher when more than one), case file Replay section, Replay nav link once a replay is published. `replay.js` only loads on pages with replays.

## Phase 4 checks
- [x] 63 tests pass (validator, model, admin upload, import command, page context/escaping).
- [x] Browser: example replay imported on two local projects (then deleted); playback, pause, speed, switcher, reduced motion and 390px layout checked.

## Content for Bunny (Phase 4)
- One sanitized SOC Copilot run and one TARS run as JSON (`docs/REPLAY_FORMAT.md`). Import, check, then publish.

## Phase 5 notes carried forward
- The robot still sits over content (e.g. the roster's first row at 1440x900). Phase 5 parks it.

## Before Phase 5
- [ ] Run a critique pass on the Phase 5 plan (robot + chatbot) first. Share findings and wait for Bunny's OK before writing any Phase 5 code.

## Phase 5 (later) — tasks carried forward
- [ ] Eval test: 30 to 50 recruiter questions, each with its expected intent. Bunny supplies the questions; do not write them.
      **Acceptance:** one test runs every question through intent matching and reports each mismatch (question, expected, actual).

## Phase 7 (later) — notes carried forward
- `ARCHITECTURE.md` still describes the old `ExperienceEntry` / `AdditionalCertification` fields. Rewrite with the Phase 7 docs update.
- `SiteAppearance` is still mentioned in `README.md`, `QUICK_START.md`, `SETUP_GUIDE.md`, `DJANGO_SETUP.md`, `DEPLOYMENT_CHECKLIST.md`, `ARCHITECTURE.md`. Clean up in Phase 7.
- Django admin's calendar/clock icons are Django's own blue-grey SVGs; leave or recolour in Phase 7.
- Unused Tailwind utility shims remain at the top of `styles.css` (e.g. `.h-3`, `.w-6`); remove in Phase 7 if still unused.
