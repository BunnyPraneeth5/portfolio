# TASKS

Current phase: **Phase 5b — Chat answers in admin, smarter matching, job search mode** (see `docs/REDESIGN_PLAN.md` §3).
**Status: implemented, waiting for Bunny's review.** Phases 0 to 6 committed and pushed on `redesign/phase-0`.

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
- [x] Critique pass shared 2026-10-12; Bunny approved all recommendations (split into 5a / 5b).

## Phase 5a — Chat helper (done, waiting for review)
- [x] Robot parked bottom-right (72px / 56px phone), idle bob + blink off under reduced motion; footer keeps a bottom strip clear.
- [x] Robot is a real button (Enter/Space); console-style `role="dialog"`; focus moves to the input; Esc closes and returns focus; history kept while the page is open.
- [x] `SuggestedQuestion` chips (admin-editable, seeded with 6 questions; SOC Copilot chip only if that project exists). Migrations 0022, 0023.
- [x] `/api/chat/` returns `{reply, links, chips}`; project answers link the case file and "Play the replay" when one is published. Links rendered only for safe URLs; all text via textContent.
- [x] Third-person, data-only replies; no hardcoded claims or fallback content. 16 story replies pending review (kept verbatim in code). Honest "is this AI" reply (+ a few extra phrasings).
- [x] `ChatQuery` log (scrubbed, no IP, 90-day purge) with read-only admin, filter by fallback.
- [x] Rate limit 20/min per visitor via hashed `X-Real-IP` / `REMOTE_ADDR` in cache; 429 with a friendly reply. CSRF kept.
- [x] 77 tests pass. Browser: keyboard open/close, chips, links, typed question, desktop gutter placement, phone layout.

## Phase 5b — done, waiting for review
- [x] Eval set researched and approved: 74 topics, 259 phrasings (`portfolio/chat_eval.py`, readable `docs/CHATBOT_EVAL_QUESTIONS.md`). Baseline before changes: 116 ok / 66 wrong / 33 missing topics.
- [x] `ChatAnswer` model: keywords, synonyms, answer text with safe placeholders, link, priority, is_active, needs_review, follows_job_search_mode. 65 rows seeded (migrations 0025, 0026); 16 story texts copied verbatim (verified), all 26 story/personal topics need review.
- [x] Matching: same normalisation for questions and keywords, shorthand synonyms, typo correction (5+ letters; long words need a closer match), plural only for 3+ letter words (fixes "his" = greeting), longest specific phrase wins, overlapping keywords count once. Result: 259/259.
- [x] Job search mode (Open / Quiet / Not looking, default Quiet) replaces "Open to work": homepage, chips and replies follow it; editable mode replies; availability timestamp.
- [x] Neutral answers for salary, work authorization, other offers, leading questions.
- [x] Admin: Chat answers editor with "Answer comes from" column, "Try a question" page, "Create a chat answer" action on Chat queries; cache cleared on save.
- [x] 108 tests pass (eval, mode, admin edits, review flow, validation, admin pages).
- Bunny: review the 26 "needs review" topics; About bio paragraph 3 says "actively seeking ... roles", which contradicts Quiet mode.

## Phase 5 (later) — tasks carried forward
- [ ] Eval test: 30 to 50 recruiter questions, each with its expected intent. Bunny supplies the questions; do not write them.
      **Acceptance:** one test runs every question through intent matching and reports each mismatch (question, expected, actual).

## Phase 6 — Blog as "Logs" (done, waiting for review)
Decisions (Bunny, 2026-10-12): remove "Coming Soon" placeholder cards; sort by event date.
- [x] `BlogPost.log_type` (decision, incident, build_log, note; default note) + ordering by event date. Migration `0024_blogpost_log_type`. Admin list/filter/form updated.
- [x] Logs index: mono `TYPE · date` label + serif title + excerpt; filter links (`?type=`) for types that have posts; honest empty states.
- [x] Log detail in case-file typography (breadcrumb LOGS / TYPE, kicker, title, excerpt, image, body).
- [x] Homepage "From the logs" shows the type. Nav already "Logs"; `/blog/` URL unchanged.
- [x] 85 tests pass. Browser: desktop + 390px, filter and empty state checked.
- Phase 7: old blog card CSS (`blog-card-visual--*`, `blog-placeholder-card`) is now unused; remove in the CSS cleanup.

## Phase 7 — Polish and launch checks (done, waiting for review)
Decisions (Bunny, 2026-10-13): full contact section only on home, case files and logs; restyle About, Skills and Contact; remove Tailwind and AOS; Lighthouse via a temporary `npx` download.
- [x] Removed Tailwind CDN, Font Awesome, AOS. Small base reset added to `styles.css` in place of Tailwind's preflight.
- [x] `script.js` cut to background layers + mobile nav (no 180 ms timer, no fade-ins/count-ups), loaded with `defer`.
- [x] Pruned unused CSS (272 selectors, 139 classes, incl. old blog cards and Tailwind shims); dynamic class prefixes kept.
- [x] About, Skills, Contact restyled with the case-file panels; hardcoded "College Level" / "Organizer" badges removed; About stats show only filled values.
- [x] Meta description on every page (falls back to hero description); Open Graph + Twitter tags; case files and logs share their own title, summary and image.
- [x] Site settings loaded once per request (`RequestMemoMiddleware`).
- [x] Layout checked at 390px and 1440px on all 8 pages; contrast check: no text below 4.5:1.
- [x] Lighthouse (local dev server, after `defer`) home mobile 61 → 88, desktop 94 → 96, SEO 90 → 100, weight 642 → 218 KiB; case file mobile 64 → 86, desktop 94 → 97. Accessibility and best practices 100. Single runs vary (one case-file mobile run scored 66; two reruns 86).
- [x] README, ARCHITECTURE rewritten; SiteAppearance removed from setup docs; ADMIN_GUIDE updated.
- [x] Tests pass.
- Left as is: Django admin's own calendar/clock icons; text compression (server setting); `SECURE_PROXY_SSL_HEADER` not set (OG URLs may be http on PythonAnywhere), decide with Bunny.

## Phase 8 — Page redesigns (in progress)
Plan: `docs/REDESIGN_PLAN.md` Phase 8. Approved 2026-10-14 after mockups.
- [x] 8.0 New admin fields (migration `0027_phase8_page_fields`, 13 optional fields) + admin fieldsets + ADMIN_GUIDE; 119 tests pass. Waiting for review.
- [x] 8.1 Case board: featured rows (case no., stamp, role · year · type, evidence counts, Watch the run via existing player), archive table (year column only when any year), no duplicate title; old projects CSS pruned (71 selectors, other 7 pages layout-identical); 127 tests pass. Waiting for review.
- [x] 8.2 Home: Currently line (hidden when empty), roster featured-only (fallback first 4) with one-liner or first sentence, dated log list, footer Last updated on every page (+3 small queries); fixed has_replays name clash from 8.1; 134 tests pass. Waiting for review.
- [x] 8.3 Logs: index grouped by year with type stamp, reading time, Filed under (published cases only); post page with side rail and older/newer links; case file Logs on this case section + nav link; 141 tests pass. Waiting for review.
- [ ] 8.4 About (card grid, separate Work / Education / Events, featured certificates, no stat tiles)
- [ ] 8.5 Checks and docs
