# User Manual

How to run, update and fill this portfolio. Written for Bunny, the only person who deploys and edits it.

Field-by-field reference for every admin screen: `ADMIN_GUIDE.md`. Replay file format: `docs/REPLAY_FORMAT.md`. How the code fits together: `ARCHITECTURE.md`.

---

## 1. Where everything on the site comes from

Every visible piece of the site is edited in the Django admin at `/admin/`. Nothing needs a code change.

| On the site | Admin section | Notes |
| --- | --- | --- |
| Name, roles, pitch, "Currently:" line, social links, email, location, resume, portrait, meta description | **Site Settings** | One row only. Save it once after every deploy. |
| Job search mode (Open, Quiet, Not looking) | **Site Settings** | Controls "Open to roles" on Home and the chat helper's availability replies. |
| Home roster (Agents) | **Projects** with **Is featured** ticked | Shows featured projects only; with none featured, the first 4. |
| Case board (`/projects/`) | **Projects** | Featured = big rows. Everything else = archive table. |
| Case file page | **Projects** (+ Case decisions, Case incidents inlines) | Each section only shows when filled. |
| Replay player | **Project replays** | Must be published. Shown on Home, the case file and "Watch the run". |
| Logs | **Blog posts** | Only **Published** posts show. |
| About page | **About**, **Professional Experience**, **Education Entries**, **Events / Leadership Entries**, **Certifications**, **What I Do Items** | Empty cards are hidden. |
| Skills (Toolkit) | **Skills** | "Used in" is matched automatically from project tech tags. |
| Chat helper answers | **Chat answers**, **Suggested questions** | Use "Try a question" to test. |
| Messages from the contact form | **Contact messages** | Read only. |
| Questions visitors asked the chat helper | **Chat queries** | Read only. Deleted after 90 days. |

---

## 2. Content rules (apply to everything you type)

- No made-up or unverifiable numbers. If you cannot prove a metric, leave the field empty.
- No vague hero text, no filler, no lorem ipsum, no emoji icons.
- No em dashes (—) in site text. Use a comma, a full stop or "·".
- Keep your bio consistent with your job search mode (do not write "actively seeking" while in Quiet mode).
- Never put passwords, API keys or private emails in replays, logs or chat answers.

---

## 3. First production setup after the Phase 8 deploy

Do these once, in this order.

### 3.1 Back up first

In a PythonAnywhere **Bash console**:

```bash
cd ~
mysqldump -u bunnypraneeth -h bunnypraneeth.mysql.pythonanywhere-services.com --set-gtid-purged=OFF --no-tablespaces 'bunnypraneeth$default' > backup-$(date +%F).sql
zip -r media-backup-$(date +%F).zip portfolio/media
```

This is PythonAnywhere's own backup command (help page "Backing up (and restoring) MySQL databases"). No password prompt: PythonAnywhere keeps it in `~/.my.cnf`. If it complains about column statistics, add `--column-statistics=0`. Check the database name on the **Databases** tab; the line above uses the name from `config/settings.py`.

To restore a backup (this **replaces** the current data):

```bash
mysql -u bunnypraneeth -h bunnypraneeth.mysql.pythonanywhere-services.com 'bunnypraneeth$default' < backup-YYYY-MM-DD.sql
```

### 3.2 Update the code (one-time switch to environment variables)

Since this update, `config/settings.py` picks the database from environment variables (`DB_ENGINE`), so it never needs hand edits again. The first time only:

1. **Write down your MySQL details** from the **Databases** tab (database name, username, host). If your current production `config/settings.py` has the MySQL password typed into it, copy the password now.
2. **Create or edit `~/portfolio/.env`** in the **Files** tab (never commit this file; `.gitignore` already excludes it):

```env
DEBUG=False
SECRET_KEY=<your existing production secret key>
ALLOWED_HOSTS=bunnypraneeth.pythonanywhere.com
DB_ENGINE=mysql
DB_NAME=bunnypraneeth$default
DB_USER=bunnypraneeth
DB_PASSWORD=<your MySQL password>
DB_HOST=bunnypraneeth.mysql.pythonanywhere-services.com
DB_PORT=3306
```

   Both the web app and every `python manage.py ...` command in the console read this file. If your WSGI file already sets some of these with `os.environ[...]`, those values win; keep them identical or remove them from the WSGI file.

3. **Drop the old hand edit and pull:**

```bash
cd ~/portfolio
git checkout -- config/settings.py
git pull origin redesign/phase-0
```

4. **Check it reads MySQL** before migrating:

```bash
python manage.py shell -c "from django.db import connection; print(connection.vendor)"
```

   It must print `mysql`. If it shows an error about `DB_ENGINE`, the `.env` file is missing or incomplete; production refuses to run on SQLite by accident.

### 3.3 Migrate, collect static files, reload

```bash
cd ~/portfolio
python manage.py migrate
python manage.py collectstatic --noinput
```

Then **Web** tab → **Reload**. Open the site and press `Ctrl + Shift + R` (static files are not versioned yet, so your browser can keep the old stylesheet).

### 3.4 Admin password

If you do not know the admin password on production:

```bash
python manage.py changepassword <your-admin-username>
```

In **Users**, untick **Active** on any admin account you do not use.

### 3.5 Save Site Settings once

Open **Site Settings** and click **Save**. This sets the "availability last updated" date and the footer's "Last updated" date.

---

## 4. Content checklist (recommended order)

Tick these off in production admin.

1. **Remove test data.** Projects "fgdsjkcj", "xcvbnm", "Test Project" (×3); logs with test text; About description "-----"; test summary and highlights on the Cyrene AI role. Untick **Is published** if you want to keep a row but hide it.
2. **Site Settings.** Hero name, roles (one per line), pitch, **Currently** line, links, email, location, resume PDF, portrait, meta title and description, job search mode.
3. **About.** Subtitle, bio paragraphs (the first non-empty paragraph shows on the Story card; the rest sit behind "Read the full story"), **Off duty**, **Pull quote** (a line from your own bio).
4. **Professional Experience.** Real roles only. Tick **Is current** for your current job so About shows "Now" and the "Current" badge. Highlights: one per line.
5. **Education Entries, Events / Leadership Entries, What I Do Items.** The Order field controls the order.
6. **Certifications.** Tick **Is featured** on the 2 or 3 you want as big cards. Upload the certificate file or add a credential URL, otherwise no "View" link appears.
7. **Skills.** Tick **Is featured** for your core stack. Name skills so they match your project tags (see 5.4).
8. **Projects.** For each real project:
   - Title, short description (the Case board shows the first 2 lines), tech tags (comma separated).
   - **Is featured** for your best 3 or 4; **Status**; **Case number**.
   - **Case board** fields: Role, Year, Project type, One-liner (Home roster), Personal note (shown as "Field note" on the case file).
   - **Case file** fields: Brief, Architecture notes, Open leads (one per line), and the Decisions and Incidents inlines.
   - Metrics only if you can prove them.
9. **Replays.** Upload sanitized runs (see 5.2). Remove or unpublish the illustrative example if it ever reaches production.
10. **Logs.** Write real posts. Link each one to its project with **Related project**.
11. **Chat answers.** Filter **Needs review: Yes** (26 topics). Edit each to be true, then untick Needs review. Use **Try a question** to check.
12. **Suggested questions.** The first 6 active chips show when the chat opens.

---

## 5. How to do common tasks

### 5.1 Add a new project as a case file
1. **Projects → Add project.** Fill Title (the slug fills itself), short description, tech tags, thumbnail.
2. Tick **Is published**. Tick **Is featured** if it belongs on the Case board and Home roster.
3. Fill the Case board fields and the Case file fields you have. Leave the rest empty.
4. Add decisions (code like D-01, the decision, the trade-off) and incidents (symptom, root cause, fix) in the inlines at the bottom.
5. Save, then open `/projects/<slug>/` to check.

### 5.2 Add a replay
1. Record or write the run as JSON (format: `docs/REPLAY_FORMAT.md`). Remove emails, keys, tokens, real IPs and anything private.
2. **Project replays → Add.** Pick the project, upload the file, save. The upload is checked and errors name the step to fix.
3. Tick **Is published** only after reading it once more. Tick **Is featured on home** to play it first on Home.
4. Command line alternative: `python manage.py import_replay <project-slug> <file.json> --publish`.

### 5.3 Write a log
1. **Blog posts → Add.** Title, Log type (Decision, Incident, Build log, Note), Event date (sorting uses this), Excerpt, Content.
2. **Related project**: pick the case it belongs to. The log then shows "Filed under Case 00X" and appears under "Logs on this case" on that case file.
3. Tick **Published**.

### 5.4 Make "Used in" work on the Skills page
"Used in" is automatic. A skill name is split on `/` and `&` and each part must equal a project tag exactly (capital letters do not matter).

| Skill name | Matches projects tagged |
| --- | --- |
| Python | Python |
| Django / DRF | Django or DRF |
| MCP / Agentic AI | MCP or Agentic AI |
| N8N Automation | N8N Automation only (not N8N) |

If a skill shows "No case file yet" but you used it, either add that exact tag to the project or rename the skill.

### 5.5 Change job search mode
**Site Settings → Job search mode.**
- **Open**: Home shows "Open to roles", notice period and remote; the chat helper answers availability questions.
- **Quiet** (default) and **Not looking**: those are hidden; the chat helper gives the reply text you set below the switch.

### 5.6 Feature a certificate
**Certifications**: tick **Is featured** in the list view. Featured ones are big cards on About, the rest are chips.

### 5.7 See what the chat helper could not answer
**Chat queries → filter Was fallback: Yes.** Select the questions that belong together → action **Create a chat answer from the selected questions** → write the answer.

### 5.8 Read contact messages
**Contact messages.** To stop the form, untick **Contact form active** in Site Settings.

---

## 6. Moving a lot of content at once (local to production)

You can fill everything on your own computer and copy it to PythonAnywhere in one go with Django's `dumpdata` and `loaddata`. Read the warnings first.

**Warnings**
- `loaddata` writes rows by their id. A row with the same id in production is **overwritten**; production rows that are not in your file are **kept**. If production already has content with different ids, you can end up with duplicates.
- Uploaded files (images, PDFs, certificates) are not inside the JSON. Copy the `media/` folder too, keeping the same paths.
- Back up production first (section 3.1).
- Clean your local test data before exporting.

**On your computer** (export only content, never contact messages or chat logs):

```bash
python manage.py dumpdata portfolio.SiteSettings portfolio.About portfolio.WhatIDo portfolio.EducationEntry portfolio.ExperienceEntry portfolio.EventEntry portfolio.Certification portfolio.Skill portfolio.Project portfolio.CaseDecision portfolio.CaseIncident portfolio.ProjectReplay portfolio.BlogPost portfolio.SuggestedQuestion portfolio.ChatAnswer --indent 2 -o content.json
```

Zip your `media/` folder.

**On PythonAnywhere**
1. **Files** tab: upload `content.json` and the media zip into `~/portfolio/`.
2. Bash console:

```bash
cd ~/portfolio
unzip -o media.zip
python manage.py loaddata content.json
```

3. **Web → Reload.** Check every page.

If production should exactly match your computer, the cleanest way is: back up, delete the content rows in production admin, then `loaddata`. For small changes, editing directly in production admin is simpler and safer.

---

## 7. Routine updates

**Changing content:** production admin only. No deploy needed.

**Updating code** (after a new commit is pushed):
1. Back up (3.1).
2. `cd ~/portfolio && git pull`.
3. `python manage.py migrate` and `python manage.py collectstatic --noinput`.
4. **Web → Reload**, then `Ctrl + Shift + R`.

**Backups:** run 3.1 before every deploy and once a month. Download the `.sql` and zip files from the **Files** tab and keep them off PythonAnywhere.

---

## 8. Troubleshooting

| Problem | Fix |
| --- | --- |
| New design not showing | `collectstatic`, Reload, then `Ctrl + Shift + R`. |
| Error page after a pull | Check the **Web** tab error log. Usually a missing `migrate`, or `.env` missing `DB_ENGINE` and the MySQL values (3.2). |
| "DB_ENGINE is not set while DEBUG is False" | `.env` is missing or not in `~/portfolio/` (3.2). |
| `git pull` refuses | A file was edited on the server. `git status` shows which; `git checkout -- <file>` drops the edit. |
| A project is missing from Home | It is not ticked **Is featured**, or not **Is published**. |
| A skill says "No case file yet" | Tag mismatch: see 5.4. |
| Replay does not show | Not **Is published**, or its project is not published. |
| Chat gives the wrong answer | **Chat answers → Try a question** shows which topic matched and why. |
| Admin looks unstyled | `collectstatic`, then Reload. |

---

## 9. Known gaps (not fixed yet)

- Static files are not versioned (`ManifestStaticFilesStorage`), so browsers can keep an old stylesheet after a deploy.
- `SECURE_PROXY_SSL_HEADER` is not set, so share links (Open Graph) may use `http://`.
- Text compression is a server setting.
