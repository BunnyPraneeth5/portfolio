# Admin Panel Guide

## ✅ Admin Dashboard Overview

All models (**Site Settings**, **About**, **Skills**, **Projects**, **Blog Posts**, **Contact Messages**, **Education**, **Professional Experience**, **Events**, **What I Do**, **Certifications**) are fully functional in the Django Admin panel.

Admin Header: **KP Portfolio Administration**  
Admin Title: **KP Admin**

---

## Quick Start

### 1. Start Local Server
```bash
python manage.py runserver
```

Or double-click: `run_local.bat`

### 2. Access Admin
Open browser: http://127.0.0.1:8000/admin/

### 3. Login
Use your superuser credentials.

---

## Admin Model Reference

### 1. Site Settings (Singleton)
- **Purpose**: Manages hero text, rotating titles, profile image, resume download link, social media profiles, and contact page settings.
- **Fields**:
  - `Profile image`: Portrait shown on the About page.
  - `Resume`: Upload resume PDF linked from the hero, contact section and footer.
  - `Hero name display`: Display name shown in the homepage hero.
  - `Hero roles`: One role per line, shown in the hero as one line joined with " · ".
  - `Hero description`: The one-line pitch under the name. Keep it short.
  - `Hero CTA primary/secondary`: Not used on the homepage since the Phase 2 rebuild (buttons are View agents, Resume, Contact).
  - `Job search mode` (one switch for the whole site):
    - **Open**: homepage shows the teal "Open to roles · <location>" line, notice period, "Open to remote" and "Looking for"; the chat helper answers availability, notice period, remote and internship questions from these fields.
    - **Quiet** (recommended while employed): all of that is hidden, availability chips are hidden, and the chat helper answers those questions with the "Quiet reply" (default: "For opportunities, please contact Bunny directly at ..."). It never says "available".
    - **Not looking**: same, with the "Not looking reply".
    - `Availability last updated` is set automatically when the mode, notice period or preferences change. Check it when you change jobs.
    - Your own texts (hero description, About bio, resume PDF) are not changed by the mode: keep them consistent with it.
  - `Social URLs`: GitHub, LinkedIn, Kaggle, HackerRank, LeetCode. Shown in the 30-second view, contact section and footer.
  - `Contact Info`: Email, Location, Tagline (used as the contact section heading on every page), and `Contact form active` toggle switch.
  - `SEO Meta`: Meta title & Meta description.

### 2. About Section
- **Purpose**: Powers personal bio and key performance metric counters on the `/about/` page.
- **Fields**:
  - `Title`: Header text.
  - `Subtitle`: Professional tagline.
  - `Bio Paragraphs 1, 2, 3`: Separate bio text blocks.
  - `Stat Metrics`: `stat_accuracy`, `stat_agents`, `stat_teams`, `stat_projects` and their respective labels.

### 3. Skills
- **Purpose**: Categorized skill matrix displayed on `/skills/` page and featured on homepage.
- **Fields**:
  - `Name`: Skill title (e.g., "Django", "PyTorch").
  - `Category`: `Agentic AI & MCP`, `ML & Data`, `Web & APIs`, `Languages`, `Security`, `Tools`, `Soft Skills`.
  - `Is featured`: Shown as "Core stack" in the homepage 30-second view (first 8).
  - `Order`: Sorting position.
- **Inline Editing**: Category, Is Featured, and Order can be edited directly in the list view.

### 4. Projects
- **Purpose**: Case files on `/projects/` and the homepage agent roster (every published project, by `Order`).
- **Fields**:
  - `Title`
  - `Short description`: Card summary.
  - `Long description`: Extended case study text.
  - `Thumbnail`: Upload project image.
  - `Tech tags`: Comma-separated tags (e.g., `Python, Django, MCP`).
  - `Live demo URL` & `GitHub URL`
  - `Is featured` & `Is published`
  - `Order`: Display priority (lower number appears first).
  - `Status`: Flagship, Live, Benchmarking or Archived. Shown as a badge in the roster; empty hides it. The Flagship project is the "Best work" link in the 30-second view (otherwise the first featured project).
  - `Metric kickers & values`: Small kicker labels and key stats (e.g. 99.88% Detection Accuracy). Metric 1 is the "Key metric" column in the roster.
  - `Case file` (project page `/projects/<slug>/`; each section only shows when it has content):
    - `Case number`: shown as CASE FILE NO. 00X and in the CASES / 00X breadcrumb. Empty hides the number.
    - `Brief`: the Brief section. While empty, the `Long description` is shown instead.
    - `Architecture notes`: the Investigation section.
    - `Open leads`: one per line.
  - `Status` also sets the stamp on the case file: Flagship = "Flagship · Active", Live = "Case closed · Shipped", Benchmarking = "Active · Benchmarking", Archived = "Case closed · Archived".
  - **Case decisions** (inline, below the project form): `Code` (e.g. D-01), `Decision`, `Trade-off`, `Order`.
  - **Case incidents** (inline): `Symptom`, `Root cause`, `Fix`, `Order`.
  - No thumbnail: the page and the /projects/ card show a styled "Case file" placeholder.

### 5. Education Entries
- **Purpose**: Education timeline on `/about/` page.
- **Fields**: `Degree`, `Field of study`, `Institution`, `Year range`, `Bullet 1`, `Bullet 2`, `Order`.

### 6. Professional Experience
- **Purpose**: Real roles only (internships, jobs, contracts). Shown in the "Professional Experience" timeline on `/about/`. The newest role also appears on the homepage as "Recent: <role> at <organization>". The chat widget uses it for experience questions.
- **Fields**:
  - Role: `Organization`, `Role`, `Employment type` (Internship, Part-time, Full-time, Contract, Freelance)
  - Dates: `Start date` (required), `End date`, `Is current` (shows "Present"; leave end date empty)
  - Details: `Location`, `Is remote`, `Summary` (1 to 2 lines), `Highlights` (one bullet per line, shown in a collapsible "Highlights" list), `Tags` (comma-separated), `Order`
  - Links: `Related project` (optional; adds a "See the project →" link)
- **Order**: lower `Order` first; equal values are sorted newest first.
- Certificates do not go here. Use **Certifications**.

### 7. Events & Leadership Entries
- **Purpose**: Cards for hackathons, events, and leadership roles.
- **Fields**: `Title`, `Role`, `Year`, `Location`, `Description`, `Stats 1-3` (value & label), `Order`.

### 8. Certifications
- **Purpose**: All certificates (courses, virtual internships, badges). Shown in the "Certifications" list on `/about/` and in the chat widget.
- **Fields**: `Title`, `Issuer`, `Category` (optional group label, e.g. Virtual Internship), `Issued date`, `Certificate file`, `Certificate file 2` (optional), `Credential URL` (optional), `Order`.

### 9. What I Do
- **Purpose**: Checklist items under "What I Do" section on `/about/` page.

### 10. Blog Posts (shown as "Logs")
- **Purpose**: The Logs page (`/blog/`, nav label "Logs") and the homepage "From the logs" section (latest 3).
- **Fields**: `Title`, `Slug`, `Log type` (Decision, Incident, Build log, Note; default Note), `Event date` (logs are sorted by this, newest first), `Content` (HTML allowed), `Excerpt`, `Image`, `Published`.
- **Filter**: the Logs page shows a filter for each type that has published posts (e.g. `/blog/?type=decision`).

### 11. Contact Messages
- **Purpose**: Read-only log of visitor messages submitted via the `/contact/` form.

---

### 12. Project Replays
- **Purpose**: Recorded agent runs played back like a terminal on the homepage (Replay section) and on each project's case file. Never live.
- **Add one**: pick the project, upload a sanitized `.json` file, save. Title and duration fill from the file if empty. Format and rules: `docs/REPLAY_FORMAT.md`.
- **Checks on upload**: format, kinds (`info`, `tool_call`, `result`, `error`), max 300 steps, max 500 characters per step, and obvious leaks (emails, keys/tokens, public IPs). Errors name the step and the fix.
- **Fields**: `Project`, `Replay file` (upload), `Title`, `Duration (s)`, `Order`, `Is published` (off by default; turn on after the sanitization checklist), `Is featured on home` (plays first on the homepage; only one at a time), `Steps` (filled from the file).
- **Nav**: the Replay link appears in the header once at least one replay is published.
- **Backup path**: `python manage.py import_replay <project_slug> <path.json> [--publish] [--feature-on-home] [--title ...] [--order N]`.

### 13. Suggested Questions (chat helper chips)
- **Purpose**: Clickable chips shown when the chat helper opens and after an unrecognised question.
- **Fields**: `Text`, `Order`, `Is active`. The first 6 active ones are shown.

### 14. Chat Queries (read-only)
- **Purpose**: Questions visitors asked the chat helper, to spot gaps. Filter by `Was fallback` to see what it could not answer.
- **Privacy**: emails and phone numbers are replaced with [email] / [phone] before saving; no IP addresses are stored; rows older than 90 days are deleted automatically.

### 15. Chat Answers (everything the chat helper says)
- **One row per topic** (65 seeded). Edit any of them; changes apply on the next message, no deploy.
- **Answer comes from** (column): *Your text* (the Answer field), *Live site data* (built from your projects, skills, experience, settings), or *Nothing yet* (shows "no approved answer yet").
- **Fields**:
  - `Keywords`: phrases that point to the topic, one per line. Case, punctuation and small typos are ignored; longer, more specific phrases win.
  - `Synonyms`: shorthand rewrites applied to every question, one per line as `short = meaning` (e.g. `np = notice period`, `wfh = work from home`, `ctc = salary`).
  - `Answer`: your text. Leave empty to use live data. Placeholders: `{name}`, `{contact_email}`, `{location}`, `{notice_period}`, `{looking_for}`, `{resume_url}`.
  - `Link label` + `Link URL`: an extra link under the answer (`/contact/` or `https://...`).
  - `Priority`: breaks ties between topics that match equally well.
  - `Is active`: off = topic ignored. `Needs review`: on = matched but not shown. `Follows job search mode`: on = Quiet / Not looking reply when not Open.
- **Stories and personal topics start with Needs review on** (26 rows: hardest bug, conflict, deadlines, weakness, failure, why AI, career goals, backlogs, bond, shifts, languages, open source, etc.). The 16 old ones contain the original text: check each, edit it to be true, then untick Needs review. The 10 new ones are empty: write your answer, then untick.
- **Neutral topics** (salary, visa / work authorization, other offers, leading questions) answer "please contact Bunny directly". Keep them that way.
- **Try a question** (button on the Chat answers list): type any question to see how it is read, which topic it matches and the exact reply. Nothing is logged.
- **Chat queries → "Create a chat answer from the selected questions"**: turns missed questions into a new topic with those questions as keywords.
- **Eval set**: `portfolio/chat_eval.py` (readable copy in `docs/CHATBOT_EVAL_QUESTIONS.md`) holds 259 recruiter phrasings the tests check.

**Chat helper notes**
- The helper is rule-based (not AI) and answers in the third person from data on this site.
- Limit: 20 messages per minute per visitor.

## Common Administrative Tasks

### Feature a Project on Homepage
1. Go to **Projects**.
2. Check the **Is featured** box for the target project.
3. Save.

### Add a New Skill
1. Go to **Skills** → **Add Skill**.
2. Name: "MCP (Model Context Protocol)".
3. Category: Select `Agentic AI & MCP`.
4. Check **Is featured** if you want it on the homepage.
5. Save.

### Update Profile Picture or Resume
1. Go to **Site Settings**.
2. Upload new **Profile image** or **Resume PDF**.
3. Save.

---

## Troubleshooting

### Changes Not Showing?
1. Clear browser cache (`Ctrl + Shift + R`).
2. Verify item is checked as **Is published** / **Is featured**.

### Admin Static Styling Looks Unstyled?
Run `collectstatic`:
```bash
python manage.py collectstatic --noinput
```

