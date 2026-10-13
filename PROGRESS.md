# PROGRESS

Newest entry at the top.

---

## 2026-10-14 — Session 10: Phase 7 pushed, research and mockups, Phase 8.0

**Git:** Phase 7 committed and pushed (`8dd2fe2`).

**Research:** Hacker News "share your site" threads and a roundup; visited chini.dev, knowshubhangi.com, brittanychiang.com, eugeneyan.com, emilkowal.ski, jesse-zhou.com, kuber.studio. Reddit was not reachable from the search tool. Takeaway: praised sites have one concept from the person's own work; ours is the ops room, so Phase 8 deepens it instead of copying.

**Mockups approved by Bunny:** Case board (Projects), Home, Logs, About (card grid, v2 with separate Work / Education / Events). Plan saved as Phase 8 in `docs/REDESIGN_PLAN.md`.

**Phase 8.0:** committed (`80ef951`). Migration `0027_phase8_page_fields` adds 13 optional fields (all blank, so pages are unchanged until filled).

**Phase 8.1 to 8.4:** committed one by one (`6e5b970`, `4d2b3a6`, `4c0dd10`, `10e2a2c`): Case board, Home, Logs, About as cards. Old page CSS pruned at each step (layout fingerprints of untouched pages identical).

**Phase 8.5:** Field note (`personal_note`) on the case file. Checks on 10 page types at 390px and 1440px: no horizontal scroll, no overflow, no text below 4.5:1 (checker validated with a planted 1.40:1 element). Lighthouse (local dev server): Home mobile 88 / desktop 98, Case board mobile 86 / desktop 96, accessibility, best practices and SEO 100. Tests 114 → 150.

**Phase 8.5 gaps:** after Bunny asked for a page-by-page comparison with the mockups, fixed every code gap (committed `2a7f592`).

**Phase 8.6 Skills:** Skills had been left out of Phase 8 and was unreachable (no link since the Phase 2 nav). Now in the nav in place of Replay, rebuilt as a Toolkit with automatic "Used in" matching. Tests 155 → 159.

**Local data notes:** the illustrative sample replay is imported and published on SOC Copilot in the local DB only (title "Example run (illustrative only)"). Every other preview value used during checks was set with direct updates and cleared again.

**Deploy note for Bunny (Phase 8)**
1. Back up the MySQL database.
2. Pull the branch, then `python manage.py migrate` (0027; also 0025 and 0026 if Phase 5b was never migrated there).
3. `python manage.py collectstatic --noinput`, then reload the web app.
4. Hard refresh in your browser (static files are not versioned yet, so an old `styles.css` can stick).
5. Fill the new fields in admin: featured ticks, case numbers, statuses, role, year, type, one-liner per project; Currently line; Off duty and quote; featured certificates.

---

## 2026-10-13 — Session 9: Phase 5b committed + pushed, Phase 7 implemented

**Git:** Phase 5b committed (`fa92128`) and pushed.

**Phase 7:** done locally, waiting for review. See TASKS.md for the list.
- Third-party CSS/JS gone (Tailwind, Font Awesome, AOS); script.js 11 KB → 2.3 KB and deferred; styles.css 3884 → about 3000 lines.
- Before any CSS removal and after: layout probe showed no layout change on 8 pages × 2 widths except the intended ones (removed menu icon, contact section placement).
- Lighthouse numbers are from the local dev server (no compression); production will differ.
- Tests 108 → 114, all pass.

**Deploy note for Bunny (Phase 7)**
1. Back up the MySQL database.
2. Pull the branch. No new migrations in Phase 7 (0025 and 0026 from Phase 5b still need `migrate` if not run yet).
3. `python manage.py collectstatic --noinput` (styles.css and script.js changed).
4. Reload the web app.
5. Open Site Settings once and Save.
6. Share a case file link in a preview tool and check og:url / og:image are https. If they are http, we add `SECURE_PROXY_SSL_HEADER` (not done, needs your OK).

**For Bunny (discuss next)**
- About description is "-----" locally; bio paragraph 3 contradicts Quiet mode.
- 26 "needs review" chat answers.
- Extra superuser accounts to deactivate.

---

## 2026-10-12 — Session 8: Phase 6 committed + pushed, recruiter research, Phase 5b implemented

**Git:** Phase 6 committed (`f4b7289`); branch pushed (Phases 0 to 6 on GitHub, no co-author lines).

**Research:** recruiter phone-screen, Indian fresher AI/ML, portfolio/GitHub, agentic-AI, logistics and behavioural sources → 62 topics; Bunny approved and asked for 12 more → 74 topics, 259 phrasings with twisted variants. Baseline on the 5a bot: 116 ok, 66 wrong, 33 missing.

**Phase 5b:** done locally, waiting for review.
- Everything the chat helper says moved to admin (`ChatAnswer`, 65 rows); "Try a question" admin page; create-answer action from chat logs.
- New matcher; all 259 phrasings pass. Fixed root causes: "his" read as "hi", British spellings, shorthand (NP, WFH, CTC, YOE, certs), generic "experience"/"his work" beating specific topics, over-eager typo fixes.
- Job search mode (default Quiet) controls homepage availability, chips and replies; neutral answers for salary / visa / offers / leading questions.
- Checked: 16 story texts identical to the original; a keyword-diff against the 5a table found 12 accidentally dropped keywords, restored.
- Tests 85 → 108, all pass. Browser: homepage in Quiet mode, chat chips, admin Chat answers, Try a question, Site Settings.

**For Bunny**
- Review the 26 "needs review" topics in admin (Chat answers → filter Needs review: Yes).
- About bio paragraph 3 says "actively seeking agentic AI engineering roles and startup internships": edit it if you stay in Quiet mode.
- Deploy: back up MySQL, pull, `migrate` (0025, 0026), `collectstatic`, reload; then open Site Settings once and Save (sets "availability last updated").

**Next**
- Phase 7.

## 2026-10-12 — Session 7: Phase 5a committed, Phase 6 implemented

**Phase 5a:** committed as `f68ccdd` (local; Phases 4 and 5a not pushed yet).

**Checks Bunny asked for:** every contact link is conditional; emptying LeetCode (in a rolled-back transaction) removed it from all 7 pages and the chat reply. Measured performance issues recorded for Phase 7 in TASKS.md.

**Contact section on every page (Bunny to decide in Phase 7):** recommendation is footer links on every page, the full contact section only on the homepage, case files and log posts (where a reader has just seen work), not on About/Skills/Cases list/Logs index.

**Phase 6:** done locally, waiting for review.
- `BlogPost.log_type` + event-date ordering (migration 0024); Logs index with type labels and filters; log detail in case-file style; homepage log cards show the type.
- Removed the three hardcoded "Coming Soon" cards (Bunny's decision).
- Tests 77 → 85, all pass. Browser checked at desktop and 390px (used port 8001: something else was already running on 8000).

**Deploy note for Bunny:** back up MySQL, pull, `migrate` (0024), `collectstatic`, reload.

**Next**
- Bunny: review Phase 6; send eval questions for 5b; decide the contact section placement.
- Then Phase 7.

## 2026-10-12 — Session 6: history cleanup, Phase 4 committed, Phase 5a implemented

**History:** removed the "Co-Authored-By: Claude" trailer from all branch commits (filter-branch; backup branch `backup/before-coauthor-removal`), force-pushed `redesign/phase-0`. Phase 4 committed as `63e409f` (local, not pushed).

**Phase 5 critique:** shared and approved; Phase 5 split into 5a (now) and 5b (after Bunny's eval questions).

**Phase 5a:** done locally, waiting for review.
- Chat helper rebuilt: parked robot button, console-style dialog, chips from `SuggestedQuestion`, links in answers, `{reply, links, chips}` API.
- `chatbot.py`: third person, data-only replies; 16 story replies kept verbatim but not served (pending review); old static claim texts kept as `_review_reply_*` for 5b. Keyword table and matching code copied verbatim (checked byte for byte); only change: extra phrasings for the honest "is this AI" intent.
- `ChatQuery` log with scrubbing, no IP, 90-day purge. Rate limit via `X-Real-IP` (confirmed on PythonAnywhere's help page) or `REMOTE_ADDR`.
- Fixed while testing: legacy submit-button CSS overrode the chat Send button; long contact values overflowed their panel on phones.
- Tests 63 → 77, all pass. Browser checks done; test chat logs deleted afterwards.

**Deploy note for Bunny:** back up MySQL, pull, `migrate` (0022, 0023), `collectstatic`, reload.

**Next**
- Bunny: review 5a; send 30 to 50 eval questions for 5b.

## 2026-10-12 — Session 5: Phase 3 committed, Phase 4 implemented

**Phase 3:** committed as `337bcf9` on `redesign/phase-0`.

**Phase 4:** done locally, waiting for review.

**Decision from Bunny:** the replay validator also blocks obvious leaks (emails, token-like strings, public IPs).

**Done**
- `ProjectReplay` model (migration 0021), shared validator `portfolio/replays.py`, admin JSON upload, `import_replay` command, player `static/replay.js`, `partials/replay_player.html`.
- Homepage Replay section (featured first + switcher), case file Replay section, Replay nav link when a replay is published.
- `docs/REPLAY_FORMAT.md` + illustrative `docs/examples/replay-example.json`. `ADMIN_GUIDE.md` section 12.
- Tests 43 → 63, all pass.
- Browser: imported the example on two local projects, checked playback/pause/2x/switcher/reduced motion/390px, then deleted them. The preview pane does not fire `requestAnimationFrame` while hidden, so timed playback was verified with a timer stand-in; a capped frame step now stops a backgrounded tab from dumping all remaining lines at once.
- Not built: optional `tools/` log converter.

**Deploy note for Bunny:** back up MySQL, pull, `migrate` (0021), `collectstatic`, reload. JSONField needs MySQL 5.7.8+ (PythonAnywhere's MySQL 8 is fine).

**Next**
- Bunny: review Phase 4; prepare sanitized SOC Copilot and TARS runs.
- Then the "Before Phase 5" critique pass, and wait for Bunny's OK.

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
