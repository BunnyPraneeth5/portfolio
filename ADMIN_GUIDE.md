# Admin Panel Guide

## ✅ Admin Dashboard Overview

All models (**Site Settings**, **Site Appearance**, **About**, **Skills**, **Projects**, **Blog Posts**, **Contact Messages**, **Education**, **Experience**, **Events**, **What I Do**, **Additional Certifications**) are fully functional in the Django Admin panel.

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
  - `Profile image`: Upload image for homepage hero.
  - `Resume`: Upload resume PDF linked across navbar/footer.
  - `Hero name display`: Display name shown in hero.
  - `Hero roles`: Multiline string (one role per line, rotates in hero animation).
  - `Hero description`: Short intro paragraph.
  - `Hero CTA primary/secondary`: Custom button labels and target URLs (`/about/`, `/projects/`).
  - `Social URLs`: GitHub, LinkedIn, Kaggle, HackerRank, LeetCode.
  - `Contact Info`: Email, Location, Tagline, and `Contact form active` toggle switch.
  - `SEO Meta`: Meta title & Meta description.

### 2. Site Appearance (Singleton)
- **Purpose**: Controls site CSS theme accent colors dynamically across all templates.
- **Fields**:
  - `Primary color` (Hex color picker, default `#3b82f6`)
  - `Secondary color` (Hex color picker, default `#8b5cf6`)
  - `Accent color` (Hex color picker, default `#06b6d4`)

### 3. About Section
- **Purpose**: Powers personal bio and key performance metric counters on the `/about/` page.
- **Fields**:
  - `Title`: Header text.
  - `Subtitle`: Professional tagline.
  - `Bio Paragraphs 1, 2, 3`: Separate bio text blocks.
  - `Stat Metrics`: `stat_accuracy`, `stat_agents`, `stat_teams`, `stat_projects` and their respective labels.

### 4. Skills
- **Purpose**: Categorized skill matrix displayed on `/skills/` page and featured on homepage.
- **Fields**:
  - `Name`: Skill title (e.g., "Django", "PyTorch").
  - `Category`: `Agentic AI & MCP`, `ML & Data`, `Web & APIs`, `Languages`, `Security`, `Tools`, `Soft Skills`.
  - `Is featured`: Checkbox to show skill on homepage.
  - `Order`: Sorting position.
- **Inline Editing**: Category, Is Featured, and Order can be edited directly in the list view.

### 5. Projects
- **Purpose**: Featured showcase, secondary cards, and project archive on `/projects/` page and homepage hero.
- **Fields**:
  - `Title`
  - `Short description`: Card summary.
  - `Long description`: Extended case study text.
  - `Thumbnail`: Upload project image.
  - `Tech tags`: Comma-separated tags (e.g., `Python, Django, MCP`).
  - `Live demo URL` & `GitHub URL`
  - `Is featured` & `Is published`
  - `Order`: Display priority (lower number appears first).
  - `Metric kickers & values`: Small kicker labels and key stats (e.g. 99.88% Detection Accuracy).

### 6. Education Entries
- **Purpose**: Education timeline on `/about/` page.
- **Fields**: `Degree`, `Field of study`, `Institution`, `Year range`, `Bullet 1`, `Bullet 2`, `Order`.

### 7. Experience Entries
- **Purpose**: Two-column professional experience timeline on `/about/` page.
- **Fields**: `Organization`, `Role`, `Year label`, `Side` (left/right column), `Tags` (comma-separated), `Certificate file` uploads 1 & 2, `Order`.

### 8. Events & Leadership Entries
- **Purpose**: Cards for hackathons, events, and leadership roles.
- **Fields**: `Title`, `Role`, `Year`, `Location`, `Description`, `Stats 1-3` (value & label), `Order`.

### 9. Additional Certifications
- **Purpose**: Certification badge grid with direct PDF downloads.
- **Fields**: `Title`, `Icon class` (FontAwesome, e.g., `fab fa-aws`), `Icon color` (Tailwind class), `Certificate file`, `Order`.

### 10. What I Do
- **Purpose**: Checklist items under "What I Do" section on `/about/` page.

### 11. Blog Posts
- **Purpose**: Technical articles on `/blog/` and `/blog/<slug>/`.
- **Fields**: `Title`, `Slug` (auto-generated), `Event date`, `Content` (HTML supported), `Excerpt`, `Image`, `Published`.

### 12. Contact Messages
- **Purpose**: Read-only log of visitor messages submitted via the `/contact/` form.

---

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

