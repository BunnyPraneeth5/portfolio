"""Rule-based chat helper for the portfolio (no LLM, no external calls).

Replies are written in the third person and built only from data on this site.
Story replies that make claims about Bunny are kept below unchanged but are not
served: they wait for Bunny's review (Phase 5b moves them into admin with a
needs_review flag). get_reply() returns {reply, links, chips, intent, fallback}.
"""

import re
from collections import OrderedDict

from django.db.models import Q
from django.urls import reverse

from .context_processors import get_resume_url
from .models import (
    Certification, EducationEntry, EventEntry, ExperienceEntry, Project,
    Skill, SiteSettings, SuggestedQuestion,
)

INTENT_KEYWORDS = OrderedDict([
    # High-priority specific recruiter scenario & trick questions
    ('hardest_bug', ['hardest bug', 'challenging bug', 'hardest problem', 'tough bug', 'difficult bug', 'debugging', 'obstacle', 'challenge']),
    ('why_agentic_over_llm', ['why agentic', 'agentic vs llm', 'why mcp', 'why agents', 'chatbot vs agent', 'traditional chatbot', 'fine-tuned llm', 'static prompt']),
    ('agent_failure_handling', ['agent stuck', 'agent error', 'agent fail', 'hallucination', 'infinite loop', 'fallback', 'guardrail', 'error handling']),
    ('explain_to_ceo', ['explain to non-technical', 'explain to ceo', 'layman terms', 'simple terms', 'non technical', 'explain soc copilot']),
    ('fun_curiosity_project', ['fun project', 'curiosity', 'side project', 'weekend project', 'pet project']),
    ('rearchitect_project', ['re-architect', 'rearchitect', 'do differently', 'what would you change', 'improve project']),
    ('conflict_disagreement', ['disagreement', 'conflict', 'differing opinion', 'team argument', 'collaborate', 'disagree']),
    ('stay_updated', ['stay updated', 'keep up', 'learn new', 'latest ai', 'research papers', 'trends']),
    ('tight_deadlines', ['tight deadline', 'pressure', 'under pressure', 'fast paced', 'quick turn', 'fast turn']),
    ('startup_vs_senior', ['startup vs senior', 'why junior', 'why fresh', 'fresh graduate vs', 'senior engineer']),
    ('fav_library', ['favorite library', 'fav library', 'favorite framework', 'fav framework', 'tool of choice']),
    ('bias_bad_data', ['dataset bias', 'bad data', 'imbalanced data', 'data quality', 'cleaning data', 'pre-processing', 'smote']),
    ('story_behind_name', ['why bunny', 'nickname', 'meaning of bunny']),
    ('replace_developers', ['replace developers', 'replace humans', 'take our jobs', 'ai replacing']),
    ('system_design', ['system design', 'architecture', 'scalability', 'scalable', 'microservices']),

    # Core hiring & availability logistics
    ('why_hire', ['why should we hire', 'why hire', 'why you', 'strengths', 'superpower', 'secret sauce', 'what sets you apart', 'competitive advantage', 'why choose', 'value proposition']),
    ('notice_period', ['notice period', 'when can you start', 'start date', 'join date', 'immediate', 'how soon']),
    # Past work goes to the experience reply; must come before 'internship' (availability)
    ('past_work', ['your experience', 'your internship', 'your internships', 'past internship', 'previous internship', 'internship experience',
                   'where did you work', 'where have you worked', 'where do you work', 'worked at', 'work experience',
                   'work history', 'internship history', 'professional experience', 'previous role', 'current role']),
    ('internship', ['internship', 'intern', 'stipend', 'trainee']),
    ('remote', ['remote', 'relocate', 'relocation', 'location work', 'hybrid', 'on-site', 'onsite', 'timezone']),
    ('availability', ['looking for job', 'hiring', 'available', 'open to work', 'opportunities', 'hiring status', 'full time', 'roles', 'openings']),
    ('who_is_bunny', ['who is bunny', 'who is karu', 'tell me about yourself', 'background', 'bio', 'elevator pitch', 'introduction', 'about you', 'who made you', 'author', 'creator']),
    ('resume', ['resume', 'cv', 'download resume', 'get cv', 'pdf']),
    ('contact', ['contact', 'email', 'reach you', 'linkedin', 'github url', 'kaggle', 'leetcode', 'phone', 'location', 'address', 'bengaluru', 'kurnool']),
    ('education', ['college', 'university', 'degree', 'study', 'education', 'gpa', 'major', 'sjcet', 'btech', 'cse', 'coursework', 'academic']),
    ('certifications', ['certification', 'certificate', 'certified', 'mcp certified', 'credentials']),
    ('experience', ['experience', 'internship history', 'work history', 'hackathon', 'event', 'led', 'leadership', 'techtrotter']),

    # Projects & Skills
    ('soc_copilot', ['soc copilot', 'soc', 'cicids', 'cicids2017', 'shodan', 'intrusion', 'threat intelligence', 'cyber security project', 'security pipeline']),
    ('car_sales', ['car sales', 'car price', 'price prediction', 'neural network project']),
    ('gate_pass', ['gate pass', 'qr code', 'college gate', 'access control']),
    ('skill_agentic', ['agentic', 'mcp', 'agent', 'model context protocol', 'multi-agent', 'multi agent', 'autonomous agent', 'tool use']),
    ('skill_ml', ['machine learning', 'ml', 'tensorflow', 'scikit', 'pytorch', 'keras', 'deep learning', 'nlp', 'neural network', 'model training', 'feature engineering']),
    ('skill_python', ['python']),
    ('skill_django', ['django', 'backend']),
    ('skill_security', ['security', 'cybersecurity', 'penetration', 'vulnerability', 'threat', 'intrusion']),
    ('skill_web', ['web', 'frontend', 'api', 'rest', 'react', 'fastapi', 'html', 'css', 'javascript', 'fullstack', 'full stack']),
    ('skills_general', ['skills', 'tech stack', 'languages', 'technologies', 'what do you know', 'tools', 'frameworks', 'database', 'postgres', 'docker', 'git']),
    ('specific_project', []),  # Dynamically matched against Project titles & tech tags
    ('projects_general', ['projects', 'built', 'portfolio project', 'github', 'work', 'case studies', 'recent work']),

    # Conversational & meta
    ('is_ai', ['are you real', 'are you ai', 'are you an ai', 'is this ai', 'is this an ai', 'is this a bot', 'are you a robot', 'are you a bot', 'human', 'llm', 'gpt', 'chatgpt', 'who is answering']),
    ('greeting', ['hi', 'hello', 'hey', 'greetings', 'help', 'who are you', 'good morning', 'good afternoon']),
    ('walle_fun', ['directive', 'eva', 'plant', 'solar', 'garbage', 'trash', 'favorite movie', 'movie']),
])


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


def _match_intent(text):
    for intent, keywords in INTENT_KEYWORDS.items():
        if intent == 'specific_project':
            if _matching_project(text):
                return intent
            continue
        if any(_keyword_hit(keyword, text) for keyword in keywords):
            return intent
    return 'fallback'


FALLBACK_TEXT = "Sorry, I didn't catch that. Try one of these topics:"

# ---------------------------------------------------------------------------
# Replies. Third person, built only from data on this site (no invented claims).
# Each builder returns (text, links) where links is a list of (label, url).
# ---------------------------------------------------------------------------

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


def _reply_greeting(text):
    return (
        f"Hi! This is a scripted helper for {_full_name()} (Bunny)'s portfolio. "
        "It answers from the data on this site and is not an AI. Pick a topic below or type a question."
    ), []


def _reply_is_ai(text):
    settings = _settings()
    reply = (
        "This is a scripted helper: not an AI and not Bunny in person. It matches keywords in your "
        "question and answers from Bunny's portfolio data on this site."
    )
    if settings.contact_email:
        reply += f"\n\nTo reach Bunny directly: {settings.contact_email}"
    return reply, [('Contact page', reverse('contact'))]


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
    if settings.open_to_work:
        lines.append(f"• Open to roles{f', notice period: {settings.notice_period}' if settings.notice_period else ''}")
    links.append(('Resume', get_resume_url(settings)))
    return '\n'.join(lines), links


def _reply_availability(text):
    settings = _settings()
    if not settings.open_to_work:
        reply = "Bunny isn't marked as looking for a role right now."
        if settings.contact_email:
            reply += f" You can still get in touch: {settings.contact_email}"
        return reply, [('Contact page', reverse('contact'))]
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


def _reply_pending_review(text):
    return ("There's no approved answer for that yet. Here are topics this helper can answer:"), []


def _reply_fallback(text):
    if text:
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
    return FALLBACK_TEXT, []


# ---------------------------------------------------------------------------
# Pending review: served as "no approved answer yet" until Bunny approves them.
# Text below is unchanged from the original helper.
# ---------------------------------------------------------------------------

PENDING_REVIEW_INTENTS = (
    'hardest_bug',
    'why_agentic_over_llm',
    'agent_failure_handling',
    'explain_to_ceo',
    'fun_curiosity_project',
    'rearchitect_project',
    'conflict_disagreement',
    'stay_updated',
    'tight_deadlines',
    'startup_vs_senior',
    'fav_library',
    'bias_bad_data',
    'story_behind_name',
    'replace_developers',
    'system_design',
    'walle_fun',
)

def _reply_hardest_bug(text):
    return (
        "The hardest bug I encountered was managing async state synchronization and preventing deadlocks in SOC Copilot's 4-agent MCP pipeline. "
        "Because multiple agents (Recon, Reputation, Shodan) were returning data concurrently, updating the PyQt6 GUI directly caused race conditions. "
        "I resolved it by designing a thread-safe signal dispatcher and decoupling task execution into an async queue with strict state locking."
    )


def _reply_why_agentic_over_llm(text):
    return (
        "Traditional LLMs and static chatbots generate single-shot text predictions, making them prone to hallucinations when tackling complex tasks. "
        "Agentic AI with Model Context Protocol (MCP) gives models agency—allowing them to dynamically select tools, query databases, invoke APIs (like Shodan), and self-correct across steps. "
        "It transforms an AI model from a passive text box into an active software agent."
    )


def _reply_agent_failure_handling(text):
    return (
        "To prevent AI agents from looping or getting stuck, I implement deterministic guardrails: maximum step limits, strict Pydantic/JSON schema validation on tool calls, "
        "and fallback exception handlers. If an agent receives unparseable API output, it catches the error gracefully, injects context-specific correction prompts, or escalates to a human-in-the-loop callback."
    )


def _reply_explain_to_ceo(text):
    return (
        "If I were explaining SOC Copilot to a non-technical executive, I'd say: Imagine having a digital security squad of 4 specialized AI analysts working 24/7. "
        "One watches the door, one investigates suspicious IPs, one checks global vulnerability threat feeds, and one writes concise executive briefings—giving you instant security triage in seconds."
    )


def _reply_fun_curiosity_project(text):
    return (
        "One of my favorite curiosity projects was building an interactive desktop companion widget in PyQt6 with custom vector animations. "
        "I wanted to see how seamlessly I could bridge desktop OS events with dynamic web APIs and local LLM micro-agents."
    )


def _reply_rearchitect_project(text):
    return (
        "If I were re-architecting SOC Copilot from scratch today, I would upgrade the agent communication layer from local thread queues to an event-driven Redis pub/sub message broker with WebSocket streaming. "
        "That would allow individual MCP agents to scale horizontally across distributed cloud containers rather than running on a single host."
    )


def _reply_conflict_disagreement(text):
    return (
        "During TechTrotter 2K25, when team members had conflicting ideas on technical architecture under tight hackathon deadlines, "
        "I brought everyone together to build rapid 15-minute benchmarks and test assumptions with real sample inputs. "
        "Data-driven evidence quickly resolved opinions and kept the team focused on building the best solution."
    )


def _reply_stay_updated(text):
    return (
        "I stay ahead of rapid AI developments by regularly reading arXiv preprints, following the Model Context Protocol (MCP) and multi-agent open-source ecosystems on GitHub, "
        "building hands-on weekend prototypes, and competing in ML challenges on Kaggle."
    )


def _reply_tight_deadlines(text):
    return (
        "I thrive under tight deadlines! Leading TechTrotter 2K25 taught me how to ruthlessly prioritize core MVP capabilities, delegate effectively, "
        "and deliver reliable, high-performing software on tight schedules without compromising code architecture."
    )


def _reply_startup_vs_senior(text):
    return (
        "Why hire me for a startup? I bring specialized, hands-on expertise in bleeding-edge technologies like Agentic AI and MCP—frameworks that emerged very recently—with zero legacy debt mindset. "
        "I'm agile, build full-stack prototypes fast, and am ready to start immediately with maximum drive."
    )


def _reply_fav_library(text):
    return (
        "My favorite Python libraries are PyTorch and Django. PyTorch offers total flexibility for designing dynamic ML computational graphs, "
        "while Django provides a clean, battery-included architecture for shipping secure production web backends rapidly."
    )


def _reply_bias_bad_data(text):
    return (
        "In domain datasets like intrusion detection (CICIDS2017), normal network traffic vastly outnumbers attack records. "
        "I handle data imbalance and noise using SMOTE oversampling, feature normalization, stratification, and evaluating models with Precision-Recall AUC and Confusion Matrices rather than relying on misleading raw accuracy."
    )


def _reply_story_behind_name(text):
    return (
        "My full legal name is Karu Praneeth Kumar, and 'Bunny' is my developer handle and nickname across GitHub (BunnyPraneeth5), Kaggle, and tech communities. "
        "Feel free to call me Karu or Bunny!"
    )


def _reply_replace_developers(text):
    return (
        "AI agents won't replace software engineers; they are massive productivity multipliers! "
        "Agents eliminate repetitive boilerplate, manual log inspection, and routine triage, allowing engineers to focus on high-level system architecture, creative problem solving, and product strategy."
    )


def _reply_system_design(text):
    return (
        "My approach to system design centers on modularity, clean interface boundaries, and single-responsibility components. "
        "Whether building an MCP multi-agent pipeline or a Django REST backend, I decouple data storage, business logic, and API presentation to ensure long-term scalability and easy testing."
    )


def _reply_walle_fun(text):
    return (
        "I love building high-tech interfaces and intelligent agent pipelines! In my free time, I enjoy exploring new AI research papers, "
        "tweaking UI animations, and experimenting with autonomous micro-agents. Try asking me about 'SOC Copilot' or 'Why Agentic AI'!"
    )



# Original static replies replaced by data-driven ones above (kept for review, not served).
def _review_reply_why_hire(text):
    about = About.objects.first()
    settings = SiteSettings.load()
    acc = about.stat_accuracy if about else "99.88%"
    agents = about.stat_agents if about else "4"
    teams = about.stat_teams if about else "25+"
    notice = settings.notice_period or "Immediate"
    return (
        f"Here is why I'd be a strong addition to your engineering team:\n\n"
        f"1. Cutting-Edge Agentic AI Expertise: I've built autonomous {agents}-agent MCP pipelines achieving {acc} intrusion detection accuracy on the CICIDS2017 dataset.\n"
        f"2. End-to-End Execution: I don't just train ML models; I build complete products with Django backends, PyQt6 GUIs, and REST APIs.\n"
        f"3. Leadership & Ownership: As Hackathon Lead for TechTrotter 2K25, I mentored and organized {teams} competing teams under tight deadlines.\n"
        f"4. Rapid Onboarding: I have an {notice} notice period and am ready to make an impact on Day 1."
    )


def _review_reply_skill_python(text):
    return (
        "Python is my primary programming language! I use it daily across:\n"
        "• Agentic AI & MCP: Developing autonomous multi-agent pipelines\n"
        "• Machine Learning: Neural network training in PyTorch & Scikit-learn\n"
        "• Web & APIs: Building backends with Django and FastAPI\n"
        "• GUIs & Automation: Crafting desktop interfaces with PyQt6"
    )


def _review_reply_skill_django(text):
    return (
        "I build scalable backend web services and REST APIs with Django. "
        "In fact, this entire portfolio website and its live database query engine are built using Django!"
    )


def _review_reply_skill_agentic(text):
    return (
        "I specialize in Agentic AI and Model Context Protocol (MCP)!\n\n"
        "I design autonomous multi-agent architectures featuring dynamic tool invocation, async step orchestration, and state management. "
        "My SOC Copilot project showcases this by coordinating 4 specialized AI agents in real-time."
    )


def _review_reply_skill_security(text):
    return (
        "In cybersecurity, I build AI-powered threat intelligence and intrusion detection systems. "
        "My flagship SOC Copilot project achieved a 99.88% intrusion detection accuracy on the CICIDS2017 dataset, "
        "combining automated Shodan reconnaissance with reputation scoring pipelines."
    )


def _review_reply_soc_copilot(text):
    project = _matching_project('soc copilot') or _matching_project('soc')
    desc = project.short_description if project else "Autonomous 4-agent MCP security pipeline (Recon, Reputation, Shodan, Report)."
    metrics = ""
    if project and project.metric_1_value:
        metrics = f"\nAccuracy Metric: {project.metric_1_value} {project.metric_1_label}"
    return (
        f"SOC Copilot is one of my key projects!\n\n"
        f"{desc}{metrics}\n\n"
        f"Key Highlights: 4-agent MCP architecture, PyQt6 GUI, automated Shodan threat intelligence, and 99.88% accuracy on CICIDS2017. "
        f"You can read the full case study on my /projects/ page!"
    )


def _review_reply_car_sales(text):
    project = _matching_project('car sales') or _matching_project('car')
    desc = project.short_description if project else "Neural network for predicting car prices with feature engineering."
    return f"My Car Sales Price Prediction project uses deep neural networks and Scikit-learn to estimate vehicle market values based on feature engineering like mileage, brand, and condition.\n\nExplore it on my /projects/ page!"


def _review_reply_gate_pass(text):
    project = _matching_project('gate pass') or _matching_project('gate')
    desc = project.short_description if project else "QR authentication gate pass system reducing unauthorized entries."
    return f"I developed the College Gate Pass System to modernize campus access control. It uses QR-code authentication for fast check-ins, replacing paper logs and reducing unauthorized campus entry.\n\nView details on my /projects/ page!"



_INTENT_BUILDERS = {
    'why_hire': _reply_why_hire,
    'notice_period': _reply_notice_period,
    'past_work': _reply_experience,
    'internship': _reply_internship,
    'remote': _reply_remote,
    'availability': _reply_availability,
    'who_is_bunny': _reply_who_is_bunny,
    'resume': _reply_resume,
    'contact': _reply_contact,
    'education': _reply_education,
    'certifications': _reply_certifications,
    'experience': _reply_experience,
    'soc_copilot': _reply_soc_copilot,
    'car_sales': _reply_car_sales,
    'gate_pass': _reply_gate_pass,
    'skill_agentic': _reply_skill_agentic,
    'skill_ml': _reply_skill_ml,
    'skill_python': _reply_skill_python,
    'skill_django': _reply_skill_django,
    'skill_security': _reply_skill_security,
    'skill_web': _reply_skill_web,
    'skills_general': _reply_skills_general,
    'specific_project': _reply_specific_project,
    'projects_general': _reply_projects_general,
    'is_ai': _reply_is_ai,
    'greeting': _reply_greeting,
    'fallback': _reply_fallback,
}

CHIP_INTENTS = {'greeting', 'fallback'}
MAX_CHIPS = 6


def suggested_chips():
    return list(SuggestedQuestion.objects.filter(is_active=True).values_list('text', flat=True)[:MAX_CHIPS])


def _response(intent, text, links, chips=False, fallback=False):
    return {
        'reply': text,
        'links': [{'label': label, 'url': url} for label, url in links],
        'chips': suggested_chips() if chips else [],
        'intent': intent,
        'fallback': fallback,
    }


def get_reply(message):
    text = (message or '').strip().lower()
    if not text:
        return _response('greeting', *_reply_greeting(text), chips=True)
    intent = _match_intent(text)
    if intent in PENDING_REVIEW_INTENTS:
        return _response(intent, *_reply_pending_review(text), chips=True, fallback=True)
    builder = _INTENT_BUILDERS.get(intent, _reply_fallback)
    try:
        reply, links = builder(text)
    except Exception:
        intent = 'fallback'
        reply, links = _reply_fallback('')
    is_fallback = intent == 'fallback' and reply == FALLBACK_TEXT
    return _response(intent, reply, links, chips=intent in CHIP_INTENTS and (intent == 'greeting' or is_fallback),
                     fallback=is_fallback)
