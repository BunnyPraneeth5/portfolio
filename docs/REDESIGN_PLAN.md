# Portfolio Redesign Plan: Ops Console x Case Files

Handoff plan for Claude Code. Repo: https://github.com/BunnyPraneeth5/portfolio
Live site: https://bunnypraneeth.pythonanywhere.com

---

## 0. How to use this plan (read first, Claude Code)

- Work **one phase at a time**. Stop at the end of each phase. Summarize what changed and wait for my go before the next phase.
- Run `python manage.py test` before and after each phase. Nothing ships with failing tests.
- One migration set per phase. Name migrations clearly.
- **Do not deploy.** I deploy to PythonAnywhere myself.
- **Never read, print, create or edit `.env`** or any secret. Never hardcode keys, emails or passwords. Use existing settings and `SiteSettings`.
- Do not invent content about me (projects, bugs, decisions, metrics). Where content is needed, leave a clear `[TODO: Bunny]` placeholder or an empty admin field.
- Keep Django 5, plain templates, vanilla JS and the single `static/styles.css` approach. No React, no build step, no new heavy dependencies.
- If something in this plan conflicts with what you find in the code, stop and ask. Don't guess.

---

## 1. Context

**Stack today**
- Django 5, app `portfolio`, project `config`
- Local: SQLite. Production: MySQL on PythonAnywhere free plan
- Templates in `templates/`, styles in `static/styles.css` (~2.5k lines), JS in `static/script.js`
- Pet widget: `templates/pet_widget.html` (SVG character, roams via `setInterval`, click opens chat)
- Chat backend: `portfolio/chatbot.py` (rule-based keyword intents) + `views.chat_reply` at `/api/chat/`

**Already done (don't redo)**
- Project slugs, `/projects/<slug>/` detail pages, legacy Project field cleanup (migrations up to 0014)
- Security/env config, dynamic homepage, admin wiring

**Known issues found in review**
- Three visual styles fight each other: luxury serif, terminal mono, pixel robot
- Opening splash delays content
- Robot roams over text and project tags
- Big empty gaps between homepage sections, duplicated "Selected Work" label + heading
- Skills section looks thin (one pill per category)
- Homepage has no contact section or footer
- TARS and AutoValue have no images
- `SiteAppearance` injects blue/purple/cyan CSS vars into `about.html` and `blog.html`, which clash with the gold theme
- Chatbot says "I'm Karu Praneeth's AI portfolio assistant". It is not AI. Must be honest
- Leftover file `portfolio/_tmp_widget_smoke.py`

---

## 2. Locked decisions

| Area | Decision |
|---|---|
| Theme | Ops console shell (homepage, nav, chat) + case file layout (project detail pages) |
| Structure | Stay multi-page. Homepage = 30-second view. Project pages = depth |
| Palette | Black/charcoal ground, gold accent `#c9a84c`, one teal status color `#5fb3a1` |
| Fonts | Cormorant Garamond (display), JetBrains Mono (labels, console), IBM Plex Sans (body) |
| Robot | Stays. Parked in a corner, no roaming over content. Tap opens console chat |
| Robot brain | **Rule-based only. No LLM.** Improve coverage instead |
| Replay | Recorded runs from existing SOC Copilot and TARS logs, played back like a terminal. Not live |
| Blog | Restyled as "logs": decisions, incidents, build logs |
| Out of scope | JD match, LLM chat, any live agent execution on the site |

Reference mockup: Design canvas "Portfolio Redesign: Ops Console x Case Files" (homepage, SOC Copilot case file, phone view). Bunny can share screenshots.

---

## 3. Phases

### Phase 0: Split Experience and Certifications (ship before the redesign)

Goal: get the latest internship live quickly and stop real experience being labelled "Credential". Uses the **current** styling. Do not start redesign work here.

**Problem today**
- `ExperienceEntry` mixes real roles and certificates. Every card renders a hardcoded "Credential" badge in `about.html`.
- `ExperienceEntry` has no description field, so a role can't explain what was done.
- Certificates live in two places: `ExperienceEntry` and `AdditionalCertification`.

**Model changes**
1. Reshape `ExperienceEntry` into pure professional experience. Add:
   - `employment_type` choices: `internship`, `part_time`, `full_time`, `contract`, `freelance`
   - `start_date` (date), `end_date` (date, optional), `is_current` (bool)
   - `location` (char, optional), `is_remote` (bool)
   - `summary` (text, 1 to 2 lines)
   - `highlights` (text, one bullet per line)
   - `related_project` (optional FK to `Project`, `on_delete=SET_NULL`)
   - Keep `organization`, `role`, `tags`, `order`. Keep `year_label` only if still needed for display, otherwise derive from dates.
   - **No slug, no detail page.**
2. New single `Certification` model: `title`, `issuer`, `issued_date` (optional), `certificate_file` (optional), `credential_url` (optional), `order`.
3. Data migration:
   - Move every existing `AdditionalCertification` into `Certification`.
   - For existing `ExperienceEntry` rows: **do not guess** which are certificates vs real roles. List them for Bunny first and ask. Move the ones he marks as certificates (with their files) into `Certification`, then delete them from `ExperienceEntry`.
   - Remove `AdditionalCertification` and the certificate file fields from `ExperienceEntry` only after the move is confirmed.
   - Keep uploaded files in place. Don't delete media.
4. Drop the Font Awesome / Tailwind `icon_class` and `icon_color` fields only if nothing else uses them. Otherwise leave them for the redesign.

**Admin**
- `ExperienceEntry` admin: grouped fieldsets (Role, Dates, Details, Links), `list_display` with organization, role, type, dates, current flag.
- `Certification` admin: title, issuer, date, has file.
- Rename admin labels to "Professional Experience" and "Certifications". Update `ADMIN_GUIDE.md`.

**About page**
1. "Professional Experience" timeline: company, role, type badge (Internship, Part-time...), date range ("Present" when current), location/remote, summary.
2. Highlights shown in an expandable card (`<details>`/`<summary>` or accessible toggle). Closed by default on phone.
3. If `related_project` is set, show a "See the project →" link to its page.
4. Remove the hardcoded "Credential" badge.
5. New "Certifications" section: one clean list/grid with issuer, date and "View certificate" link.
6. Homepage: one line in the hero area, e.g. "Recent: <role> at <organization>", from the latest `ExperienceEntry` by `start_date`. Hide if none.

**Chatbot**
- Update the `experience` and `certifications` replies to read from the new models (latest role first, then others; certifications as a short list). Keep wording style the same.

**Decisions confirmed by Bunny (2026-10-12)**
- All 5 existing `ExperienceEntry` rows are certificates. Data migration moves ALL `ExperienceEntry` and ALL `AdditionalCertification` rows into `Certification`. No ID matching.
- `Certification` gets `certificate_file` + optional `certificate_file_2`, and an optional `category` (filled from old `year_label`). No splitting.
- Drop `ExperienceEntry.side`, `icon_class`, `icon_color`, `year_label`, the certificate file fields, and `see_experience_note`. Remove unused `experience_left`/`experience_right` from `about_view`.
- Dates nullable in DB; the `ExperienceEntry` admin form requires `start_date`.
- Chatbot: "open to internships" stays on the `internship` intent; past-work questions ("your internship", "where did you work", "work experience") go to `experience`. Events listed after roles under "Hackathons and leadership". No hardcoded fallback content: if tables are empty, say so and point to /about/.
- Migrations database-neutral (RunPython only, no raw SQL).
- Also in Phase 0: delete `portfolio/_tmp_widget_smoke.py`, make `test_projects_view` create its own projects, fix the broken ✓ in `about.html` education bullets.

**Content rule**
- Only public, non-confidential details about internship work. No internal company info (funding, product plans, rollout status). Bunny writes the text.

**Done when**
- Bunny can add the internship in admin with summary and highlights, and it shows correctly on About and the homepage line
- No real role shows "Credential"
- All old certificates appear under Certifications with working files
- Migrations run clean on SQLite and MySQL
- Tests cover the new models, the About page sections and the chatbot replies

---

### Phase 1: Cleanup and design system

**Tasks**
0. Convert all public templates to extend `base.html` (today every page is a standalone HTML document; `base.html` is unused and loads a different Tailwind CDN). Move shared head, nav, mobile menu, scripts and the pet widget include into `base.html`. Do this first: tasks 3 and 4 and the Phase 2 footer depend on it.
   - Note: `SiteAppearance` CSS vars are injected into all 8 public templates (index, about, skills, projects, project_detail, blog, blog_detail, contact), not only about/blog. The admin header also links to it ("Appearance" shortcut).
   - Note: fonts today: `styles.css` `@import`s Cormorant Garamond, Outfit and JetBrains Mono; templates also load Orbitron and Space Grotesk. IBM Plex Sans is not loaded anywhere. Body font is Outfit.
1. ~~Delete `portfolio/_tmp_widget_smoke.py`.~~ Moved to Phase 0.
2. Create design tokens at the top of `static/styles.css` as CSS variables:
   - `--bg #0b0c0d`, `--panel #121416`, `--panel-deep #070808`, `--line #24282c`, `--line-soft #1c1f22`
   - `--text #ece8df`, `--text-2 #c9c5bc`, `--muted #9a9790`
   - `--gold #c9a84c`, `--gold-hover #e2c77a`, `--teal #5fb3a1`
   - `--font-display 'Cormorant Garamond'`, `--font-mono 'JetBrains Mono'`, `--font-body 'IBM Plex Sans'`
   - Spacing scale and radius (4px buttons, 6px panels)
3. Load the three fonts once in `base.html` via Google Fonts.
4. Remove the blue/purple/cyan overrides from `about.html` and `blog.html`. Decide with me whether to delete `SiteAppearance` entirely (model, admin, context processor, migration) or repoint it to the new tokens. Default proposal: delete it.
5. Build reusable CSS components: `.btn-primary`, `.btn-ghost`, `.panel`, `.label-mono`, `.status-dot`, `.stat-tile`, `.section-head`.
6. Audit `styles.css` for dead selectors after the change. Remove only what is clearly unused.
7. Restyle the admin panel (`static/admin.css`, `templates/admin/base_site.html`) with the same tokens and fonts. Today it uses old blue/purple/cyan and Orbitron. Goal: admin looks like a backstage version of the ops console. Keep Django admin usable and readable (contrast, form fields, tables).
8. If `SiteAppearance` is deleted, also remove its link from `templates/admin/base_site.html` and its section from `ADMIN_GUIDE.md`.

**Done when**
- All pages render with the new tokens, no leftover blue/purple/cyan
- Tests pass
- No visual regressions on phone width (390px) and desktop (1440px)

---

### Phase 2: Homepage rebuild (ops console)

**Tasks**
1. Remove the opening splash, or cut it to under 1 second and skip it on repeat visits.
2. Header: `KP` + `OPS://BUNNY` label, nav (Agents, Cases, Replay, Logs, Contact). Mobile menu stays.
3. Hero:
   - Status line with teal dot: `OPEN TO ROLES · <location>` driven by `SiteSettings.open_to_work` and location
   - Name, role line, one-line pitch (from `SiteSettings` hero fields)
   - Buttons: View agents, Resume, Contact
4. **30-second view** panel beside the hero: looking for, degree, core stack, location, notice period, links. Pull from `SiteSettings`, `EducationEntry`, featured `Skill`. Add fields to `SiteSettings` only if missing (e.g. `looking_for`).
5. **Agent roster**: table of published projects ordered by `order`. Columns: agent (title + short description), stack (`tech_tags`), key metric (`metric_1_value` + label), status. Each row links to the project page. Horizontal scroll on phone.
   - Add `Project.status` choices: `flagship`, `live`, `benchmarking`, `archived`.
6. **Replay preview** section (shell only in this phase; player arrives in Phase 4).
7. **From the logs**: latest 3 published blog posts.
8. **Contact section + footer** on every page via `base.html`.
9. Fix spacing: no huge empty gaps, one heading per section.

**Decisions confirmed by Bunny (2026-10-12)**
- Nav: Agents (homepage roster), Cases (/projects/), Logs (/blog/), About, Contact. Replay joins the nav in Phase 4. Skills page stays, reachable by link.
- Replay preview: built as a hidden shell (`templates/partials/replay_preview.html`), rendered only once a replay exists (Phase 4).
- Portrait removed from the homepage; it stays on About.
- Homepage skills section removed; featured skills show as "Core stack" in the 30-second view.

**Done when**
- Homepage answers "who, what role, best work, how to contact" without scrolling on desktop
- Works at 390px with no horizontal page scroll
- Tests updated for new context vars

---

### Phase 3: Case file project pages

**Model changes**
- `Project`: add `case_number` (int), `brief` (text), `architecture_notes` (text), `open_leads` (text). All optional.
- New `CaseDecision`: `project` FK, `code` (e.g. D-01), `decision` (text), `tradeoff` (text), `order`.
- New `CaseIncident`: `project` FK, `symptom`, `root_cause`, `fix`, `order`.
- Register all in admin as inlines on Project.

**Template: `project_detail.html` rebuilt as a case file**
1. Header: back to roster, breadcrumb `CASES / 00X`.
2. Title block: `CASE FILE NO. 00X`, title, short description, status stamp (`CASE CLOSED · SHIPPED`, `ACTIVE`, etc. from `status`).
3. Evidence strip: metric tiles from `metric_1..3`, stack, code/demo links.
4. Section nav (sticky on desktop, inline on phone): Brief, Investigation, Decisions, Incidents, Replay, Open leads.
5. Each section renders only if it has content. No empty headings.
6. Footer: previous/next case by `order`.
7. Fix missing thumbnails: show a styled fallback if `thumbnail` is empty.

**Decisions confirmed by Bunny (2026-10-12)**
- Brief shows `brief`, falling back to the existing `long_description` while brief is empty. Investigation = `architecture_notes`.
- Status stamps: Flagship → FLAGSHIP · ACTIVE; Live → CASE CLOSED · SHIPPED; Benchmarking → ACTIVE · BENCHMARKING; Archived → CASE CLOSED · ARCHIVED; no status → no stamp.
- Empty `case_number` hides the number (no auto-numbering).

**Done when**
- SOC Copilot page renders fully once content is filled in admin
- Empty sections hide cleanly
- Tests cover the detail view with and without decisions/incidents

**Content needed from Bunny (not Claude Code):** brief, architecture notes, 2 to 3 decisions, 1 to 2 incidents per project, open leads. Real only.

---

### Phase 4: Replay feature

**Data format** (one JSON file per run):
```json
{
  "title": "SOC Copilot investigates a suspicious IP",
  "duration_s": 42,
  "steps": [
    {"t": 0, "actor": "orchestrator", "kind": "info", "text": "received alert"},
    {"t": 2, "actor": "orchestrator", "kind": "info", "text": "dispatching 4 agents"},
    {"t": 5, "actor": "recon", "kind": "tool_call", "text": "lookup_ip"},
    {"t": 9, "actor": "recon", "kind": "result", "text": "finding summary"}
  ]
}
```
`kind` is one of `info`, `tool_call`, `result`, `error`.

**Tasks**
1. New model `ProjectReplay`: `project` FK, `title`, `duration_s`, `steps` (JSONField), `is_published`, `is_featured_on_home` (only one can be true at a time), `order`.
2. Shared validator: checks schema, rejects unknown `kind`, caps steps (e.g. 300), clear error messages.
3. **Admin upload**: a JSON file upload field on the `ProjectReplay` admin form. On save it runs the shared validator and fills `steps`. Bunny adds replays from the browser, no terminal needed.
4. Management command `import_replay <project_slug> <path.json>` as a backup path, using the same validator.
5. Converter scripts are **not** part of the site. Optional helper in `tools/` (git-ignored if it touches raw logs) to turn raw log lines into the JSON format. Raw logs never get committed.
6. Player (vanilla JS, `static/replay.js`):
   - Play/pause, restart, progress bar, speed 1x/2x
   - Steps type out in order, colored by `kind`
   - Respects `prefers-reduced-motion` (show all steps instantly)
   - Text inserted with `textContent`, never `innerHTML`
7. Show the player on the project page (Replay section) and on the homepage preview (the replay marked `is_featured_on_home` loads first, with an agent switcher).

**Sanitization checklist (Bunny runs this before import)**
- No API keys, tokens, file paths, usernames, real IPs, emails or private data
- Shorten long tool outputs to one-line summaries

**Decisions confirmed by Bunny (2026-10-12)**
- The shared validator also blocks obvious leaks as a safety net: emails, token-looking strings, public IPv4 (private and documentation ranges allowed). Manual checklist still applies.
- Optional `tools/` log converter not built in this phase (raw logs never enter the repo).

**Done when**
- One SOC Copilot and one TARS replay play on the site
- Import command rejects malformed files with a clear error
- Tests cover the import command and the player data endpoint/context

---

### Phase 5: Robot companion upgrade (rule-based)

**Behavior**
1. Park the robot in the bottom corner. Remove the roaming walk that crosses content. Keep small idle animations (blink, bob). Respect `prefers-reduced-motion`.
2. Tap or keyboard Enter opens a console-styled chat panel. Esc closes. Focus moves into the input. Panel is a real dialog with `aria-label`.
3. **Suggested question chips** on open: projects, skills, availability, resume, contact, "how does SOC Copilot work". Chips are admin-editable via a new `SuggestedQuestion` model (`text`, `order`, `is_active`).
4. Every answer that references a project includes a link to its case file.
5. A chip or question about a project with a replay can offer "Play the replay" which links to the replay section.

**Flashcards move into admin**
1. New model `ChatAnswer`: `intent` (slug, unique), `keywords` (text, one per line), `synonyms` (text, one per line), `answer` (text), `link_label`, `link_url`, `priority` (int, higher wins ties), `is_active`.
2. Data migration: move every hardcoded intent and reply from `chatbot.py` into `ChatAnswer` rows, unchanged. Keep the story replies flagged for Bunny's review (see Honesty fixes).
3. Answers that need live data (notice period, email, resume, project list, skills) stay as small Python builders, but their keywords also come from `ChatAnswer`. Use placeholders in `answer` like `{notice_period}`, `{contact_email}`, `{resume_url}` filled from `SiteSettings` at reply time.
4. Admin: list filter by `is_active`, search on keywords and answer, a short help text explaining keywords vs synonyms.
5. From the `ChatQuery` admin (below), an action "Create answer from this question" that pre-fills a new `ChatAnswer`.
6. Cache active answers and clear the cache on save, so the bot isn't hitting the DB on every message.

**Matching improvements in `chatbot.py`**
1. Normalize input: lowercase, strip punctuation, collapse spaces.
2. Expand synonyms per intent (e.g. containers ↔ docker, backend ↔ django/fastapi/api).
3. Fuzzy match with `difflib` (stdlib) for typos, with a sensible cutoff.
4. Better fallback: say it didn't catch that, then return chips for the main topics. Never a dead end.
5. Return JSON `{reply, links, chips}` from `/api/chat/` instead of only `reply`. Update the widget to render links and chips.

**Honesty fixes**
- Replace the "AI portfolio assistant" reply with an honest one, e.g. "I'm Bunny's scripted helper. I answer from his real portfolio data."
- Every story reply (hardest bug, conflict, deadlines, re-architect, etc.) gets migrated with `is_active = False` and a `needs_review` flag. Do not change their content. Bunny reviews each in admin and switches it on only if it's true.

**Logging and abuse protection**
- New model `ChatQuery`: `question` (truncated to 300 chars), `matched_intent`, `was_fallback`, `created_at`. No IP storage.
- Admin list filter on `was_fallback` so Bunny can review missed questions weekly.
- Simple rate limit on `/api/chat/` using Django cache (e.g. 20 requests per minute per session). Return a friendly message when limited.
- Keep CSRF protection on the endpoint.

**Decisions confirmed by Bunny (2026-10-12) after the critique pass**
- Split into 5a (robot, dialog, chips, links, `{reply, links, chips}`, honesty, logging, rate limit) and 5b (eval baseline from Bunny's 30 to 50 questions first, then `ChatAnswer` in admin, synonyms, fuzzy match).
- Voice: third person ("Bunny built..."); the helper says it is scripted, not AI and not Bunny.
- All 16 static story/opinion replies are pending review (not served); the old static skill/why-hire/project texts were replaced by data-driven replies and kept in code for review.
- Robot parked bottom-right, 72px desktop / 56px phone; footer reserves a bottom strip. On 1360px+ screens it sits in the gutter beside content; on narrower screens it can still pass over content while scrolling.
- Rate limit: 20/min per visitor, keyed by a salted hash of `X-Real-IP` (PythonAnywhere) or `REMOTE_ADDR`, stored only in the cache.
- `ChatQuery`: emails/phones scrubbed, no IP, 90-day retention.

**5b decisions confirmed by Bunny (2026-10-12)**
- Eval set: 74 topics / 259 phrasings (researched recruiter, fresher, AI-engineering and logistics questions, plus 12 added after review), stored in `portfolio/chat_eval.py` and run by the tests.
- Job search mode (Open / Quiet / Not looking) replaces "Open to work"; default and current setting: Quiet.
- Salary, work authorization, other offers and leading questions always get a neutral "please contact Bunny directly".
- Everything the helper says is editable in admin (ChatAnswer), with a "Try a question" page.

**Done when**
- Robot never covers text while idle
- Chips work, links work, fallback offers chips
- Unknown questions are logged and visible in admin
- Bunny can add or edit a flashcard in admin and the bot uses it immediately, no deploy
- Existing answers behave the same after the data migration
- Tests cover intent matching, synonyms, fuzzy match, fallback, rate limit, DB-backed answers and placeholder filling

---

### Phase 6: Blog as "logs"

**Tasks**
1. Add `BlogPost.log_type` choices: `decision`, `incident`, `build_log`, `note` (default `note`).
2. Restyle `blog.html` as a log index: mono label `DECISION · <date>` + serif title.
3. Restyle `blog_detail.html` to match case file typography.
4. Filter by log type on the index.
5. Rename nav label to "Logs". Keep the `/blog/` URL so old links don't break.

**Decisions confirmed by Bunny (2026-10-12)**
- Removed the three hardcoded "Coming Soon" cards (invented titles); empty state says "No logs published yet."
- Logs sorted by event date, newest first (ties by creation time), on the Logs page and homepage.

**Done when**
- Existing posts display correctly with default type
- Filters work
- Tests updated

---

### Phase 7: Polish and launch checks

1. Lighthouse pass on homepage and one project page (performance, accessibility, SEO). Fix the obvious ones.
2. Meta title/description per page, Open Graph tags for project pages (good for sharing case file links in outreach).
3. Check every page at 390px and 1440px.
4. Check color contrast (body text at least 4.5:1).
5. Update `README.md` and `ARCHITECTURE.md` for new models and the replay import flow.
6. Write a short deploy note for Bunny: migrations to run on PythonAnywhere, collectstatic, reload, DB backup first.

---

## 4. Bunny's homework (content, can run in parallel)

- [ ] Phase 0: tell Claude Code which current experience entries are real roles vs certificates
- [ ] Phase 0: internship dates, summary and 3 to 4 highlights (public details only)
- [ ] Case file content for SOC Copilot first, then TARS, Venue Copilot, AutoValue
- [ ] Images for TARS and AutoValue
- [ ] One clean log from SOC Copilot and one from TARS, sanitized
- [ ] Review every chatbot story in admin (`needs_review`) and switch on only the true ones
- [ ] TARS BigCodeBench score for the roster (or leave the metric out)
- [ ] 2 to 3 first "logs" posts (one decision, one incident)

---

## 5. Later (not in this plan)

- JD match mode
- LLM-backed chat
- Extra replays per project
- Slugs and detail pages for experience entries (revisit once there are 2 to 3 roles)
