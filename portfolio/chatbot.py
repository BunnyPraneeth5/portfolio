"""Rule-based chat helper for the portfolio (no LLM, no external calls).

Topics, keywords, shorthands and answer text live in the ChatAnswer table (admin).
Answers marked "live data" are built here from the site's own data, in the third person.
Rows with needs_review=True are matched but not shown until Bunny approves them.
get_reply() returns {reply, links, chips, intent, fallback}.
"""

import difflib
import re
from collections import OrderedDict

from django.core.cache import cache
from django.db.models import Q
from django.urls import reverse

from .context_processors import get_resume_url
from .models import (
    Certification, ChatAnswer, EducationEntry, EventEntry, ExperienceEntry, Project,
    ProjectReplay, Skill, SiteSettings, SuggestedQuestion,
)


def _word_pattern(term):
    return re.compile(r'\b' + re.escape(term) + r'(?:s|es|ing|ed)?\b')


def _keyword_hit(term, text):
    if ' ' in term:
        return term in text
    return _word_pattern(term).search(text) is not None


def _matching_project(text):
    """Return the first published Project whose title or tags match."""
    projects = list(Project.objects.filter(is_published=True))
    for project in projects:
        title = project.title.strip().lower()
        if title and title in text:
            return project
        for tag in project.tech_tags_list:
            if tag.lower() and len(tag) > 2 and _keyword_hit(tag.lower(), text):
                return project
        words = title.split()
        for i in range(len(words) - 1):
            phrase = f'{words[i]} {words[i + 1]}'
            if phrase in text:
                return project
        if len(words) == 1 and len(words[0]) > 3 and words[0] in text:
            return project
    return None


def _settings():
    return SiteSettings.load()


def _full_name():
    return _settings().hero_name_display or 'Bunny'


def _case_links(project):
    """Case file link, plus the replay when a published one exists."""
    url = reverse('project_detail', args=[project.slug])
    links = [(f'{project.title} case file', url)]
    if project.replays.filter(is_published=True).exists():
        links.append(('Play the replay', url + '#replay'))
    return links


def _published_projects():
    return list(Project.objects.filter(is_published=True).order_by('order', 'id'))


def _find_project(*phrases):
    for project in _published_projects():
        title = project.title.lower()
        if project.slug in phrases or any(phrase in title for phrase in phrases):
            return project
    return None


def _project_reply(project):
    lines = [f"{project.title}"]
    summary = project.short_description or project.brief_text
    if summary:
        lines.append(summary)
    if project.metrics:
        lines.append('Metrics: ' + ' · '.join(f"{m['value']} {m['label']}".strip() for m in project.metrics))
    if project.tech_tags_list:
        lines.append('Stack: ' + ', '.join(project.tech_tags_list))
    links = _case_links(project)
    if project.github_url:
        links.append(('Code', project.github_url))
    if project.live_demo_url:
        links.append(('Live demo', project.live_demo_url))
    return '\n\n'.join(lines), links


def _reply_who_is_bunny(text):
    settings = _settings()
    lines = [f"{_full_name()} goes by Bunny."]
    lines.append('Roles: ' + ', '.join(settings.hero_roles_list))
    education = EducationEntry.objects.first()
    if education:
        detail = f"{education.degree}, {education.field_of_study}" if education.field_of_study else education.degree
        lines.append(f"Education: {detail}, {education.institution} ({education.year_range})")
    if settings.contact_location:
        lines.append(f"Based in {settings.contact_location}.")
    if settings.hero_description:
        lines.append(f"In Bunny's words: “{' '.join(settings.hero_description.split())}”")
    return '\n\n'.join(lines), [('About page', reverse('about'))]


def _reply_why_hire(text):
    settings = _settings()
    lines = ["Here is what Bunny's portfolio shows:"]
    links = []
    projects = _published_projects()
    flagship = next((p for p in projects if p.status == 'flagship'), None) or \
        next((p for p in projects if p.is_featured), projects[0] if projects else None)
    if flagship:
        line = f"• Flagship work: {flagship.title}"
        if flagship.metric_1_value:
            line += f" ({flagship.metric_1_value} {flagship.metric_1_label})".rstrip()
        lines.append(line)
        links += _case_links(flagship)
    if projects:
        lines.append(f"• {len(projects)} published projects")
        links.append(('All case files', reverse('projects')))
    recent = ExperienceEntry.newest_first().first()
    if recent:
        lines.append(f"• Recent role: {recent.role} at {recent.organization}")
    event = EventEntry.objects.first()
    if event:
        lines.append(f"• {event.title} ({event.role}, {event.year})")
    if settings.is_job_hunting:
        lines.append(f"• Open to roles{f', notice period: {settings.notice_period}' if settings.notice_period else ''}")
    links.append(('Resume', get_resume_url(settings)))
    return '\n'.join(lines), links


def _reply_availability(text):
    settings = _settings()
    lines = ["Bunny is open to new roles."]
    if settings.looking_for:
        lines.append(f"Looking for: {settings.looking_for}")
    if settings.notice_period:
        lines.append(f"Notice period: {settings.notice_period}")
    lines.append('Open to remote: yes' if settings.open_to_remote else 'Open to remote: not marked')
    if settings.contact_email:
        lines.append(f"Email: {settings.contact_email}")
    return '\n'.join(lines), [('Contact page', reverse('contact')), ('Resume', get_resume_url(settings))]


def _reply_internship(text):
    settings = _settings()
    if settings.open_to_internship:
        reply = "Yes, Bunny is open to internships."
        if settings.looking_for:
            reply += f"\n\nLooking for: {settings.looking_for}"
    else:
        reply = "Bunny isn't marked as open to internships right now."
    if settings.contact_email:
        reply += f"\n\nEmail: {settings.contact_email}"
    return reply, [('Contact page', reverse('contact'))]


def _reply_remote(text):
    settings = _settings()
    reply = "Yes, Bunny is open to remote work." if settings.open_to_remote else \
        "Bunny hasn't marked remote work as an option."
    if settings.contact_location:
        reply += f" Based in {settings.contact_location}."
    return reply, [('Contact page', reverse('contact'))]


def _reply_notice_period(text):
    settings = _settings()
    if settings.notice_period:
        return f"Bunny's notice period: {settings.notice_period}.", [('Contact page', reverse('contact'))]
    return "Bunny hasn't listed a notice period yet.", [('Contact page', reverse('contact'))]


def _reply_education(text):
    entries = list(EducationEntry.objects.all())
    if not entries:
        return "Education details aren't listed here yet.", [('About page', reverse('about'))]
    parts = []
    for e in entries:
        line = f"• {e.degree}" + (f" in {e.field_of_study}" if e.field_of_study else '')
        line += f"\n  {e.institution} ({e.year_range})"
        parts.append(line)
    return "Bunny's education:\n\n" + "\n\n".join(parts), [('About page', reverse('about'))]


def _reply_resume(text):
    return "Bunny's resume is linked below.", [('Resume', get_resume_url(_settings())), ('About page', reverse('about'))]


def _reply_contact(text):
    settings = _settings()
    lines = []
    if settings.contact_email:
        lines.append(f"Email: {settings.contact_email}")
    if settings.contact_location:
        lines.append(f"Location: {settings.contact_location}")
    links = [('Contact page', reverse('contact'))]
    for label, url in (('GitHub', settings.github_url), ('LinkedIn', settings.linkedin_url),
                       ('Kaggle', settings.kaggle_url), ('LeetCode', settings.leetcode_url)):
        if url:
            links.append((label, url))
    reply = "How to reach Bunny:\n\n" + "\n".join(lines) if lines else "Use the contact page to reach Bunny."
    return reply, links


def _skill_reply(label, terms):
    query = Q()
    for term in terms:
        if ' ' in term:
            query |= Q(name__icontains=term)
        else:
            query |= Q(name__iregex=_word_pattern(term).pattern)
    names = sorted({s.name for s in Skill.objects.filter(query)})
    projects = [p for p in _published_projects()
                if any(_keyword_hit(term, ' '.join(p.tech_tags_list).lower()) for term in terms)]
    if not names and not projects:
        return f"Bunny hasn't listed {label} skills here yet.", [('Skills page', reverse('skills'))]
    lines = []
    if names:
        lines.append(f"Bunny's listed {label} skills: {', '.join(names)}.")
    links = []
    if projects:
        lines.append('Projects tagged with it: ' + ', '.join(p.title for p in projects[:4]) + '.')
        for project in projects[:2]:
            links += _case_links(project)
    links.append(('Skills page', reverse('skills')))
    return '\n\n'.join(lines), links


def _reply_skill_python(text):
    return _skill_reply('Python', ['python'])


def _reply_skill_django(text):
    return _skill_reply('Django', ['django', 'drf'])


def _reply_skill_ml(text):
    return _skill_reply('Machine Learning & AI', ['machine learning', 'tensorflow', 'scikit', 'pytorch', 'ml', 'deep learning', 'neural network'])


def _reply_skill_agentic(text):
    return _skill_reply('Agentic AI & MCP', ['mcp', 'agentic', 'agent'])


def _reply_skill_security(text):
    return _skill_reply('security', ['security', 'soc', 'siem', 'threat', 'intrusion'])


def _reply_skill_web(text):
    return _skill_reply('Web & API', ['django', 'fastapi', 'rest', 'api', 'react', 'html', 'css', 'javascript'])


def _reply_skills_general(text):
    skills = Skill.objects.all()
    if not skills.exists():
        return "Skills aren't listed here yet.", [('Skills page', reverse('skills'))]
    category_labels = dict(Skill.CATEGORY_CHOICES)
    grouped = OrderedDict()
    for skill in skills:
        grouped.setdefault(category_labels.get(skill.category, skill.category), []).append(skill.name)
    parts = [f"• {label}: {', '.join(names)}" for label, names in grouped.items()]
    return "Bunny's listed skills:\n\n" + "\n".join(parts), [('Skills page', reverse('skills'))]


def _named_project_reply(*phrases):
    project = _find_project(*phrases)
    if not project:
        return "That project isn't published here yet.", [('All case files', reverse('projects'))]
    return _project_reply(project)


def _reply_soc_copilot(text):
    return _named_project_reply('soc-copilot', 'soc copilot')


def _reply_car_sales(text):
    return _named_project_reply('car sales', 'car price')


def _reply_gate_pass(text):
    return _named_project_reply('gate pass')


def _reply_specific_project(text):
    project = _matching_project(text)
    if not project:
        return _reply_projects_general(text)
    return _project_reply(project)


def _reply_projects_general(text):
    projects = _published_projects()
    if not projects:
        return "No projects are published here yet.", [('All case files', reverse('projects'))]
    lines = []
    for p in projects[:5]:
        summary = p.short_description or p.brief_text
        if summary and len(summary) > 140:
            summary = summary[:139].rstrip() + '…'
        lines.append(f"• {p.title}" + (f": {summary}" if summary else ''))
    links = []
    for p in projects[:3]:
        links.append((f'{p.title} case file', reverse('project_detail', args=[p.slug])))
    links.append(('All case files', reverse('projects')))
    return "Bunny's published projects:\n\n" + "\n\n".join(lines), links


def _reply_experience(text):
    roles = list(ExperienceEntry.newest_first()[:3])
    events = list(EventEntry.objects.all()[:2])
    if not roles and not events:
        return "Bunny hasn't added professional experience here yet.", [('About page', reverse('about'))]
    sections = []
    if not roles:
        sections.append("Bunny hasn't added professional experience here yet.")
    if roles:
        lines = []
        for index, e in enumerate(roles):
            details = ", ".join(filter(None, [e.get_employment_type_display(), e.date_range_label]))
            line = f"• {e.role} @ {e.organization}" + (f" ({details})" if details else "")
            if index == 0 and e.summary:
                line += f"\n  {e.summary}"
            lines.append(line)
        sections.append("Bunny's professional experience:\n\n" + "\n".join(lines))
    if events:
        lines = [f"• {ev.title} ({ev.role}, {ev.year})" for ev in events]
        sections.append("Hackathons and leadership:\n\n" + "\n".join(lines))
    return "\n\n".join(sections), [('About page', reverse('about'))]


def _reply_certifications(text):
    certs = list(Certification.objects.all())
    if not certs:
        return "Bunny hasn't listed certifications here yet.", [('About page', reverse('about'))]
    shown = certs[:6]
    lines = [f"• {c.title}" + (f" ({c.issuer})" if c.issuer else "") for c in shown]
    if len(certs) > len(shown):
        lines.append(f"• …and {len(certs) - len(shown)} more")
    return "Bunny's certifications:\n\n" + "\n".join(lines), [('About page', reverse('about'))]




# ---------------------------------------------------------------------------
# New data-driven topics (Phase 5b). Built only from site data.
# ---------------------------------------------------------------------------

def _flagship_project():
    projects = _published_projects()
    return next((p for p in projects if p.status == 'flagship'), None) or \
        next((p for p in projects if p.is_featured), projects[0] if projects else None)


def _reply_flagship(text):
    project = _flagship_project()
    if not project:
        return "No projects are published here yet.", [('All case files', reverse('projects'))]
    reply, links = _project_reply(project)
    return "Bunny's flagship project:\n\n" + reply, links


def _reply_replay(text):
    replays = list(ProjectReplay.objects.filter(is_published=True, project__is_published=True)
                   .select_related('project').order_by('-is_featured_on_home', 'order', 'id'))
    if not replays:
        return "No recorded agent runs are published here yet.", [('All case files', reverse('projects'))]
    lines = ["Recorded agent runs (played back, not live):"]
    links = []
    for replay in replays[:3]:
        lines.append(f"• {replay.title} ({replay.project.title})")
        links.append((f'Replay: {replay.project.title}',
                      reverse('project_detail', args=[replay.project.slug]) + '#replay'))
    return '\n'.join(lines), links


def _reply_fresher_or_experienced(text):
    roles = list(ExperienceEntry.newest_first())
    lines = []
    if roles:
        lines.append(f"Bunny has {len(roles)} role{'s' if len(roles) != 1 else ''} listed:")
        for e in roles[:3]:
            details = ", ".join(filter(None, [e.get_employment_type_display(), e.date_range_label]))
            lines.append(f"• {e.role} @ {e.organization}" + (f" ({details})" if details else ""))
    else:
        lines.append("No professional roles are listed on this site yet.")
    education = EducationEntry.objects.first()
    if education:
        lines.append(f"Education: {education.degree} ({education.year_range})")
    return '\n'.join(lines), [('About page', reverse('about'))]


def _reply_current_role(text):
    current = ExperienceEntry.objects.filter(is_current=True).order_by('order', '-start_date').first()
    if not current:
        return "No current role is listed on this site.", [('About page', reverse('about'))]
    details = ", ".join(filter(None, [current.get_employment_type_display(), current.date_range_label]))
    reply = f"Current role: {current.role} @ {current.organization}" + (f" ({details})" if details else "")
    if current.summary:
        reply += f"\n\n{current.summary}"
    return reply, [('About page', reverse('about'))]


def _reply_coding_profiles(text):
    settings = _settings()
    links = [(label, url) for label, url in (('LeetCode', settings.leetcode_url),
                                             ('HackerRank', settings.hackerrank_url),
                                             ('Kaggle', settings.kaggle_url)) if url]
    if not links:
        return "No coding profiles are listed on this site yet.", [('Contact page', reverse('contact'))]
    return "Bunny's coding profiles are linked below.", links


def _reply_research_kaggle(text):
    settings = _settings()
    links = [('Kaggle', settings.kaggle_url)] if settings.kaggle_url else []
    reply = "Bunny's Kaggle profile is linked below." if links else "No Kaggle profile is listed on this site."
    reply += " No research papers are listed on this site."
    return reply, links + [('All case files', reverse('projects'))]


def _reply_schedule_interview(text):
    settings = _settings()
    reply = "To set up a call or interview, contact Bunny"
    reply += f" at {settings.contact_email}." if settings.contact_email else " through the contact page."
    return reply, [('Contact page', reverse('contact'))]


LIVE_BUILDERS = {
    'who_is_bunny': _reply_who_is_bunny,
    'why_hire': _reply_why_hire,
    'availability': _reply_availability,
    'internship': _reply_internship,
    'remote': _reply_remote,
    'notice_period': _reply_notice_period,
    'education': _reply_education,
    'resume': _reply_resume,
    'contact': _reply_contact,
    'certifications': _reply_certifications,
    'experience': _reply_experience,
    'skills_general': _reply_skills_general,
    'skill_python': _reply_skill_python,
    'skill_django': _reply_skill_django,
    'skill_ml': _reply_skill_ml,
    'skill_agentic': _reply_skill_agentic,
    'skill_security': _reply_skill_security,
    'skill_web': _reply_skill_web,
    'projects_general': _reply_projects_general,
    'specific_project': _reply_specific_project,
    'soc_copilot': _reply_soc_copilot,
    'car_sales': _reply_car_sales,
    'gate_pass': _reply_gate_pass,
    'flagship': _reply_flagship,
    'replay': _reply_replay,
    'fresher_or_experienced': _reply_fresher_or_experienced,
    'current_role': _reply_current_role,
    'coding_profiles': _reply_coding_profiles,
    'research_kaggle': _reply_research_kaggle,
    'schedule_interview': _reply_schedule_interview,
}


# ---------------------------------------------------------------------------
# Matching (Phase 5b): answers, keywords and shorthands come from ChatAnswer rows in admin.
# ---------------------------------------------------------------------------

CACHE_KEY = 'chat-answers-v1'
CACHE_SECONDS = 60
FUZZY_MIN_LEN = 5
FUZZY_CUTOFF = 0.82          # words under 9 letters, e.g. pyhton -> python
FUZZY_CUTOFF_LONG = 0.88     # longer words need a closer match (instructions != introduction)
TITLE_PRIORITY = 6   # a published project's title found in the question
TAG_PRIORITY = 2     # one of its tech tags found in the question
SPECIAL_INTENTS = {'fallback', 'pending_review'}
DEFAULT_TEXTS = {
    'fallback': "Sorry, I didn't catch that. Try one of these topics:",
    'pending_review': "There's no approved answer for that yet. Here are topics this helper can answer:",
}
_NON_WORD = re.compile(r"[^a-z0-9]+")


def normalize(text):
    """Lowercase, drop apostrophes, turn every other non-alphanumeric into a space."""
    text = (text or '').lower().replace("’", "'").replace("'", '')
    return _NON_WORD.sub(' ', text).split()


def _parse_synonyms(raw):
    pairs = []
    for line in raw.splitlines():
        if '=' not in line:
            continue
        short, meaning = line.split('=', 1)
        short, meaning = normalize(short), normalize(meaning)
        if short and meaning:
            pairs.append((short, meaning))
    return pairs


def _load_answers():
    data = cache.get(CACHE_KEY)
    if data is not None:
        return data
    answers, synonyms, vocabulary = [], [], set()
    for row in ChatAnswer.objects.all():
        entry = {
            'intent': row.intent,
            'answer': row.answer,
            'link': (row.link_label, row.link_url) if row.link_label and row.link_url else None,
            'priority': row.priority,
            'is_active': row.is_active,
            'needs_review': row.needs_review,
            'follows_mode': row.follows_job_search_mode,
            'phrases': [normalize(k) for k in row.keyword_list if normalize(k)],
        }
        answers.append(entry)
        if row.is_active:
            synonyms.extend(_parse_synonyms(row.synonyms))
            for phrase in entry['phrases']:
                vocabulary.update(phrase)
    synonyms.sort(key=lambda pair: len(pair[0]), reverse=True)
    for _, meaning in synonyms:
        vocabulary.update(meaning)
    data = {'answers': answers, 'synonyms': synonyms, 'vocabulary': sorted(vocabulary)}
    cache.set(CACHE_KEY, data, CACHE_SECONDS)
    return data


def clear_cache(**kwargs):
    cache.delete(CACHE_KEY)


def _apply_synonyms(tokens, synonyms):
    out, i = [], 0
    while i < len(tokens):
        for short, meaning in synonyms:
            if tokens[i:i + len(short)] == short:
                out.extend(meaning)
                i += len(short)
                break
        else:
            out.append(tokens[i])
            i += 1
    return out


def _correct_typos(tokens, vocabulary):
    known = set(vocabulary)
    long_words = [w for w in vocabulary if len(w) >= FUZZY_MIN_LEN]
    corrected = []
    for token in tokens:
        if len(token) >= FUZZY_MIN_LEN and token not in known and not token.isdigit():
            cutoff = FUZZY_CUTOFF if len(token) < 9 else FUZZY_CUTOFF_LONG
            match = difflib.get_close_matches(token, long_words, n=1, cutoff=cutoff)
            corrected.append(match[0] if match else token)
        else:
            corrected.append(token)
    return corrected


def _word_matches(keyword_word, token):
    if token == keyword_word:
        return True
    # Plural forms only for words of 3+ letters, so "hi" never matches "his".
    return len(keyword_word) >= 3 and token in (keyword_word + 's', keyword_word + 'es')


def _phrase_span(phrase, tokens):
    """(start, end) of the first place the phrase appears in tokens, or None."""
    n = len(phrase)
    for start in range(len(tokens) - n + 1):
        if all(_word_matches(phrase[k], tokens[start + k]) for k in range(n)):
            return (start, start + n)
    return None


def _phrase_in(phrase, tokens):
    return _phrase_span(phrase, tokens) is not None


def prepare(message):
    data = _load_answers()
    tokens = _apply_synonyms(normalize(message), data['synonyms'])
    return _correct_typos(tokens, data['vocabulary'])


def _project_candidate(tokens):
    """Best published project whose title (or a tech tag) appears in the question."""
    best = None
    for project in _published_projects():
        title = normalize(project.title)
        if title and _phrase_in(title, tokens):
            score = (len(title), 1, TITLE_PRIORITY)
        else:
            tag_hits = [normalize(tag) for tag in project.tech_tags_list
                        if len(tag) > 2 and _phrase_in(normalize(tag), tokens)]
            if not tag_hits:
                continue
            score = (max(len(t) for t in tag_hits), len(tag_hits), TAG_PRIORITY)
        if best is None or score > best[0]:
            best = (score, project)
    return best


def match(tokens, include_projects=True):
    """Return (answer_entry, project) for the best-matching active topic, or (None, None)."""
    best_score, best_entry, best_project = None, None, None
    for entry in _load_answers()['answers']:
        if not entry['is_active'] or entry['intent'] in SPECIAL_INTENTS or entry['intent'] == 'specific_project':
            continue
        spans = {span for span in (_phrase_span(p, tokens) for p in entry['phrases']) if span}
        if not spans:
            continue
        # Score: longest matched phrase, then how many separate places matched, then priority.
        # Overlapping keywords on the same words (e.g. "agent" and "agents") count once.
        distinct = {span for span in spans if not any(o != span and o[0] <= span[0] and span[1] <= o[1] for o in spans)}
        score = (max(end - start for start, end in spans), len(distinct), entry['priority'])
        if best_score is None or score > best_score:
            best_score, best_entry, best_project = score, entry, None
    project_entry = _entry('specific_project') if include_projects else None
    if project_entry and project_entry['is_active']:
        candidate = _project_candidate(tokens)
        if candidate and (best_score is None or candidate[0] > best_score):
            best_entry, best_project = project_entry, candidate[1]
    return best_entry, best_project


def _entry(intent):
    return next((e for e in _load_answers()['answers'] if e['intent'] == intent), None)


def _special_text(intent):
    entry = _entry(intent)
    return (entry['answer'] if entry and entry['answer'].strip() else DEFAULT_TEXTS[intent])


_PLACEHOLDER = re.compile(r'\{(\w+)\}')


def fill_placeholders(text):
    settings = _settings()
    values = {
        'name': _full_name(),
        'contact_email': settings.contact_email or '',
        'location': settings.contact_location or '',
        'notice_period': settings.notice_period or '',
        'looking_for': settings.looking_for or '',
        'resume_url': get_resume_url(settings),
    }
    # Unknown {words} are left as they are, so stray braces never break a reply.
    return _PLACEHOLDER.sub(lambda m: values.get(m.group(1), m.group(0)), text)


def greeting_text():
    entry = _entry('greeting')
    return fill_placeholders(entry['answer']) if entry and entry['answer'].strip() else ''


def mode_reply():
    settings = _settings()
    text = settings.not_looking_reply if settings.job_search_mode == 'not_looking' else settings.quiet_reply
    return fill_placeholders(text), [('Contact page', reverse('contact'))]


MAX_CHIPS = 6


def _chip_follows_mode(chip):
    entry, _ = match(prepare(chip), include_projects=False)
    return bool(entry and entry['follows_mode'])


def suggested_chips():
    chips = list(SuggestedQuestion.objects.filter(is_active=True).values_list('text', flat=True))
    if not _settings().is_job_hunting:
        # Hide chips that would only get the Quiet / Not looking reply.
        chips = [chip for chip in chips if not _chip_follows_mode(chip)]
    return chips[:MAX_CHIPS]


def _response(intent, text, links, chips=False, fallback=False):
    return {
        'reply': text,
        'links': [{'label': label, 'url': url} for label, url in links],
        'chips': suggested_chips() if chips else [],
        'intent': intent,
        'fallback': fallback,
    }


def _fallback_search(message):
    """Last resort before giving up: a skill or project whose name appears in the question."""
    text = (message or '').strip()
    if not text:
        return None
    matching_skills = Skill.objects.filter(name__icontains=text)
    if matching_skills.exists():
        names = ", ".join(s.name for s in matching_skills)
        return f"Bunny lists these skills: {names}.", [('Skills page', reverse('skills'))]
    matching_projects = Project.objects.filter(
        Q(title__icontains=text) | Q(tech_tags__icontains=text) | Q(short_description__icontains=text),
        is_published=True,
    )
    if matching_projects.exists():
        return _project_reply(matching_projects.first())
    return None


def get_reply(message):
    tokens = prepare(message)
    if not tokens:
        if (message or '').strip():  # only symbols, e.g. "????"
            return _response('fallback', _special_text('fallback'), [], chips=True, fallback=True)
        return _response('greeting', greeting_text(), [], chips=True)

    entry, project = match(tokens)
    if entry is None:
        found = _fallback_search(message)
        if found:
            return _response('fallback_search', *found)
        return _response('fallback', _special_text('fallback'), [], chips=True, fallback=True)

    intent = entry['intent']
    if entry['needs_review']:
        return _response(intent, _special_text('pending_review'), [], chips=True, fallback=True)
    if entry['follows_mode'] and not _settings().is_job_hunting:
        return _response(intent, *mode_reply())

    extra = [entry['link']] if entry['link'] else []
    if entry['answer'].strip():
        return _response(intent, fill_placeholders(entry['answer']), extra, chips=intent == 'greeting')
    builder = LIVE_BUILDERS.get(intent)
    if builder is None:
        return _response(intent, _special_text('pending_review'), [], chips=True, fallback=True)
    try:
        reply, links = _project_reply(project) if project is not None else builder(' '.join(tokens))
    except Exception:
        return _response('fallback', _special_text('fallback'), [], chips=True, fallback=True)
    return _response(intent, reply, links + extra)
