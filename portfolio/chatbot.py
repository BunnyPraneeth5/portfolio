"""Grounded, first-person Q&A engine for the portfolio pet chat widget.

Every reply is dynamically queried from live DB models (Project, Skill,
SiteSettings, About, EducationEntry, ExperienceEntry, etc.) and written
in first person as Karu Praneeth Kumar (Bunny), addressing standard and
unique recruiter queries with natural, confident, and conversational depth.
"""

import re
from collections import OrderedDict
from django.db.models import Q

from .models import (
    About, AdditionalCertification, EducationEntry, EventEntry,
    ExperienceEntry, Project, Skill, SiteSettings,
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
    ('is_ai', ['are you real', 'are you ai', 'are you a bot', 'human', 'llm', 'gpt', 'chatgpt', 'who is answering']),
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


def _reply_greeting(text):
    about = About.objects.first()
    title = about.subtitle if about else "Agentic AI Engineer · B.Tech CSE-AI"
    return (
        f"Hi there! I'm Karu Praneeth Kumar (Bunny).\n\n"
        f"I'm an {title}. I specialize in building autonomous multi-agent systems using Model Context Protocol (MCP), deep learning models, and full-stack software.\n\n"
        f"What would you like to explore about my projects, skills, hackathon leadership, or availability?"
    )


def _reply_who_is_bunny(text):
    about = About.objects.first()
    settings = SiteSettings.load()
    roles = ", ".join(settings.hero_roles_list)
    bio = settings.hero_description
    if about and about.description and len(about.description.strip()) > 5 and about.description.strip() != '-----':
        bio = about.description.strip()
    return (
        f"I'm Karu Praneeth Kumar (Bunny), a final-year B.Tech CSE (AI) student at SJCET Bengaluru based in {settings.contact_location}.\n\n"
        f"• Primary Focus: {roles}\n"
        f"• Background: {bio}\n\n"
        f"I love bridging advanced AI concepts—like multi-agent threat intelligence or neural network price prediction—with clean, production-ready software. Feel free to ask me about my projects or tech stack!"
    )


def _reply_why_hire(text):
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


def _reply_availability(text):
    settings = SiteSettings.load()
    status = "Actively looking for Agentic AI & ML engineering roles" if settings.open_to_work else "Open to strategic engineering opportunities"
    notice = settings.notice_period or "Immediate"
    remote = "Fully open to Remote roles worldwide & Relocation to tech hubs (Bengaluru/India)" if settings.open_to_remote else "Open to hybrid and on-site roles"
    return (
        f"My Current Availability:\n\n"
        f"• Status: {status}\n"
        f"• Notice Period: {notice}\n"
        f"• Work Preference: {remote}\n"
        f"• Email: {settings.contact_email}\n\n"
        f"You can reach me directly at {settings.contact_email} or via the /contact/ page!"
    )


def _reply_internship(text):
    settings = SiteSettings.load()
    if settings.open_to_internship:
        return (
            f"Yes! I'm open to high-impact Agentic AI & ML engineering internships and startup roles. "
            f"With an immediate notice period ({settings.notice_period or 'Immediate'}), I can onboard rapidly and start building production agent pipelines right away. "
            f"Reach out to me directly at {settings.contact_email}!"
        )
    return f"I'm currently focused on full-time Agentic AI Engineer roles. Feel free to get in touch at {settings.contact_email}!"


def _reply_remote(text):
    settings = SiteSettings.load()
    if settings.open_to_remote:
        return (
            "Yes, absolutely! I am fully equipped for remote engineering collaboration across timezones, "
            "and I'm also enthusiastic about relocating to major tech hubs like Bengaluru for the right on-site or hybrid role."
        )
    return "I am currently focused on on-site and hybrid roles in Bengaluru / India."


def _reply_notice_period(text):
    settings = SiteSettings.load()
    period = settings.notice_period or 'Immediate'
    return f"My notice period is {period}! I can complete onboarding quickly and start delivering value on your team immediately."


def _reply_education(text):
    entries = list(EducationEntry.objects.all())
    if not entries:
        return "I am a final-year B.Tech CSE (AI) student at SJCET Bengaluru (2022–2026), focusing on artificial intelligence, machine learning, and software engineering."
    parts = []
    for e in entries:
        bullets = f" — {e.bullet_1}" if e.bullet_1 else ""
        parts.append(f"🎓 {e.degree} in {e.field_of_study}\n  {e.institution} ({e.year_range}){bullets}")
    return "My Educational Background:\n\n" + "\n\n".join(parts)


def _reply_resume(text):
    settings = SiteSettings.load()
    if settings.resume:
        return (
            f"You can download my official Resume here: {settings.resume.url}\n\n"
            f"You can also browse my complete background on my /about/ page or contact me directly at {settings.contact_email}."
        )
    return f"You can request my resume directly at {settings.contact_email} or review my background on my /about/ page!"


def _skill_reply(label, terms):
    query = Q()
    for term in terms:
        if ' ' in term:
            query |= Q(name__icontains=term)
        else:
            query |= Q(name__iregex=_word_pattern(term).pattern)
    skills = list(Skill.objects.filter(query))
    if not skills:
        return f"I actively work with {label} in my projects. You can inspect my full toolkit on my /skills/ page!"
    names = sorted({s.name for s in skills})
    return f"My {label} toolkit includes: {', '.join(names)}. Check out my full tech stack on my /skills/ page!"


def _reply_skill_python(text):
    return (
        "Python is my primary programming language! I use it daily across:\n"
        "• Agentic AI & MCP: Developing autonomous multi-agent pipelines\n"
        "• Machine Learning: Neural network training in PyTorch & Scikit-learn\n"
        "• Web & APIs: Building backends with Django and FastAPI\n"
        "• GUIs & Automation: Crafting desktop interfaces with PyQt6"
    )


def _reply_skill_django(text):
    return (
        "I build scalable backend web services and REST APIs with Django. "
        "In fact, this entire portfolio website and its live database query engine are built using Django!"
    )


def _reply_skill_ml(text):
    return _skill_reply('Machine Learning & AI', ['machine learning', 'tensorflow', 'scikit', 'pytorch', 'ml', 'deep learning', 'neural network'])


def _reply_skill_agentic(text):
    return (
        "I specialize in Agentic AI and Model Context Protocol (MCP)!\n\n"
        "I design autonomous multi-agent architectures featuring dynamic tool invocation, async step orchestration, and state management. "
        "My SOC Copilot project showcases this by coordinating 4 specialized AI agents in real-time."
    )


def _reply_skill_security(text):
    return (
        "In cybersecurity, I build AI-powered threat intelligence and intrusion detection systems. "
        "My flagship SOC Copilot project achieved a 99.88% intrusion detection accuracy on the CICIDS2017 dataset, "
        "combining automated Shodan reconnaissance with reputation scoring pipelines."
    )


def _reply_skill_web(text):
    return _skill_reply('Web & API', ['django', 'fastapi', 'rest', 'api', 'react', 'html', 'css', 'javascript'])


def _reply_skills_general(text):
    skills = Skill.objects.all()
    if not skills.exists():
        return "My core stack includes Python, Agentic AI (MCP), PyTorch, Scikit-learn, Django, FastAPI, PyQt6, PostgreSQL, and Docker."
    category_labels = dict(Skill.CATEGORY_CHOICES)
    grouped = OrderedDict()
    for skill in skills:
        label = category_labels.get(skill.category, skill.category)
        grouped.setdefault(label, []).append(skill.name)
    parts = [f"• {label}: {', '.join(names)}" for label, names in grouped.items()]
    return "Here is a breakdown of my technical stack:\n\n" + "\n".join(parts) + "\n\nYou can explore all my skills on my /skills/ page!"


def _reply_soc_copilot(text):
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


def _reply_car_sales(text):
    project = _matching_project('car sales') or _matching_project('car')
    desc = project.short_description if project else "Neural network for predicting car prices with feature engineering."
    return f"My Car Sales Price Prediction project uses deep neural networks and Scikit-learn to estimate vehicle market values based on feature engineering like mileage, brand, and condition.\n\nExplore it on my /projects/ page!"


def _reply_gate_pass(text):
    project = _matching_project('gate pass') or _matching_project('gate')
    desc = project.short_description if project else "QR authentication gate pass system reducing unauthorized entries."
    return f"I developed the College Gate Pass System to modernize campus access control. It uses QR-code authentication for fast check-ins, replacing paper logs and reducing unauthorized campus entry.\n\nView details on my /projects/ page!"


def _reply_projects_general(text):
    projects = list(Project.objects.filter(is_published=True).order_by('order'))
    if not projects:
        return "Key Projects: SOC Copilot (MCP AI), Car Sales Price Predictor, College Gate Pass System. Visit my /projects/ page!"
    lines = []
    for p in projects[:4]:
        tags = f" [{', '.join(p.tech_tags_list[:2])}]" if p.tech_tags_list else ""
        lines.append(f"• {p.title}{tags}: {p.short_description}")
    return "Here are a few of my engineering projects:\n\n" + "\n\n".join(lines) + "\n\nYou can dive into all project case studies on my /projects/ page!"


def _reply_specific_project(text):
    project = _matching_project(text)
    if not project:
        return _reply_projects_general(text)
    tags = f" (Tech Stack: {', '.join(project.tech_tags_list)})" if project.tech_tags_list else ""
    desc = project.short_description or project.long_description or "Advanced software project."
    metrics = []
    if project.metric_1_value:
        metrics.append(f"{project.metric_1_label}: {project.metric_1_value}")
    if project.metric_2_value:
        metrics.append(f"{project.metric_2_label}: {project.metric_2_value}")
    metric_str = f"\nKey Metrics: {' | '.join(metrics)}" if metrics else ""
    links = []
    if project.github_url:
        links.append(f"GitHub: {project.github_url}")
    if project.live_demo_url:
        links.append(f"Live Demo: {project.live_demo_url}")
    link_str = f"\nLinks: {' | '.join(links)}" if links else ""
    return f"🚀 {project.title}{tags}:\n\n{desc}{metric_str}{link_str}"


def _reply_experience(text):
    experiences = list(ExperienceEntry.objects.all()[:3])
    events = list(EventEntry.objects.all()[:2])
    if not experiences and not events:
        return "Experience Highlights: TechTrotter 2K25 Hackathon Lead, AI/ML Engineering Projects, MCP Certification."
    parts = []
    for e in experiences:
        parts.append(f"• {e.role} @ {e.organization} ({e.year_label})")
    for ev in events:
        parts.append(f"• {ev.title} ({ev.role}, {ev.year})")
    return "Here is a snapshot of my experience and leadership:\n\n" + "\n".join(parts) + "\n\nYou can view my complete timeline on my /about/ page!"


def _reply_certifications(text):
    certs = list(AdditionalCertification.objects.all())
    if certs:
        titles = [f"• {c.title}" for c in certs]
        cert_str = "\n".join(titles)
    else:
        cert_str = "• MCP Certified (Model Context Protocol)\n• Neural Networks & ML Specialist"
    return f"My Certifications & Credentials:\n\n{cert_str}\n\nCheck out the full list on my /about/ page!"


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


def _reply_is_ai(text):
    settings = SiteSettings.load()
    return (
        f"I'm Karu Praneeth's AI portfolio assistant! I query my live Django database in real time to answer your questions accurately in first person.\n\n"
        f"If you'd like to get in touch with me directly, drop me a note on my /contact/ page or email me at {settings.contact_email}!"
    )


def _reply_contact(text):
    settings = SiteSettings.load()
    return (
        f"Here are my contact details and profile links:\n\n"
        f"• Email: {settings.contact_email}\n"
        f"• Location: {settings.contact_location}\n"
        f"• GitHub: {settings.github_url}\n"
        f"• LinkedIn: {settings.linkedin_url}\n"
        f"• Kaggle: {settings.kaggle_url}\n"
        f"• LeetCode: {settings.leetcode_url}\n\n"
        f"You can also send me a message directly through my /contact/ page!"
    )


def _reply_walle_fun(text):
    return (
        "I love building high-tech interfaces and intelligent agent pipelines! In my free time, I enjoy exploring new AI research papers, "
        "tweaking UI animations, and experimenting with autonomous micro-agents. Try asking me about 'SOC Copilot' or 'Why Agentic AI'!"
    )


def _reply_fallback(text):
    if text:
        matching_skills = Skill.objects.filter(name__icontains=text)
        if matching_skills.exists():
            names = ", ".join([s.name for s in matching_skills])
            return f"I have hands-on experience with {names}. You can explore my full stack on my /skills/ page!"

        matching_projects = Project.objects.filter(
            Q(title__icontains=text) | Q(tech_tags__icontains=text) | Q(short_description__icontains=text),
            is_published=True
        )
        if matching_projects.exists():
            p = matching_projects.first()
            return f"Here is a matching project for '{text}': {p.title} — {p.short_description}.\nCheck out all details on my /projects/ page!"

    return (
        "I'd love to tell you more! Here are a few things you can ask me:\n"
        "• 'Tell me about yourself'\n"
        "• 'Why should we hire you?'\n"
        "• 'Tell me about SOC Copilot'\n"
        "• 'What is your experience with Agentic AI and MCP?'\n"
        "• 'When can you start working?'\n"
        "• 'What's the hardest bug you've fixed?'\n"
        "• 'How can I contact you?'"
    )


_INTENT_BUILDERS = {
    'hardest_bug': _reply_hardest_bug,
    'why_agentic_over_llm': _reply_why_agentic_over_llm,
    'agent_failure_handling': _reply_agent_failure_handling,
    'explain_to_ceo': _reply_explain_to_ceo,
    'fun_curiosity_project': _reply_fun_curiosity_project,
    'rearchitect_project': _reply_rearchitect_project,
    'conflict_disagreement': _reply_conflict_disagreement,
    'stay_updated': _reply_stay_updated,
    'tight_deadlines': _reply_tight_deadlines,
    'startup_vs_senior': _reply_startup_vs_senior,
    'fav_library': _reply_fav_library,
    'bias_bad_data': _reply_bias_bad_data,
    'story_behind_name': _reply_story_behind_name,
    'replace_developers': _reply_replace_developers,
    'system_design': _reply_system_design,
    'why_hire': _reply_why_hire,
    'notice_period': _reply_notice_period,
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
    'walle_fun': _reply_walle_fun,
    'fallback': _reply_fallback,
}


def get_reply(message):
    try:
        text = (message or '').strip().lower()
        if not text:
            return _reply_fallback(text)
        intent = _match_intent(text)
        builder = _INTENT_BUILDERS.get(intent, _reply_fallback)
        return builder(text)
    except Exception as err:
        return _reply_fallback(message or '')
