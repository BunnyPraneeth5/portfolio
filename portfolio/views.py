import hashlib
import json
import re
from collections import OrderedDict
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from . import chatbot
from .models import (
    About, Skill, Project, BlogPost, ContactMessage, SiteSettings,
    EducationEntry, ExperienceEntry, ProjectReplay, ChatQuery,
)

def index(request):
    roster = list(Project.objects.filter(is_published=True).order_by('order'))
    flagship = next((p for p in roster if p.status == 'flagship'), None)
    if flagship is None:
        flagship = next((p for p in roster if p.is_featured), roster[0] if roster else None)
    return render(request, 'index.html', {
        'recent_experience': ExperienceEntry.newest_first().first(),
        'education': EducationEntry.objects.first(),
        'core_stack': Skill.objects.filter(is_featured=True)[:8],
        'roster': roster,
        'flagship': flagship,
        'latest_posts': BlogPost.objects.filter(published=True)[:3],
        # Featured replay first; the switcher offers the rest.
        'replays': list(
            ProjectReplay.objects.filter(is_published=True, project__is_published=True)
            .select_related('project')
            .order_by('-is_featured_on_home', 'order', 'id')
        ),
    })

def about_view(request):
    from .models import (About, WhatIDo, EducationEntry,
                         ExperienceEntry, EventEntry,
                         Certification)
    about = About.objects.first()
    what_i_do = WhatIDo.objects.all()
    education = EducationEntry.objects.all()
    experience_all = ExperienceEntry.objects.select_related('related_project')
    events = EventEntry.objects.all()
    certifications = Certification.objects.all()
    stats = []
    if about:
        for field in ('accuracy', 'agents', 'teams', 'projects'):
            value = getattr(about, f'stat_{field}')
            if value:
                stats.append({'value': value, 'label': getattr(about, f'stat_{field}_label')})

    return render(request, 'about.html', {
        'about': about,
        'stats': stats,
        'what_i_do': what_i_do,
        'education': education,
        'experience_all': experience_all,
        'events': events,
        'certifications': certifications,
    })

def skills_view(request):
    seen_skill_names = set()
    skills = []
    for skill in Skill.objects.all():
        normalized_name = skill.name.strip().casefold()
        if normalized_name in seen_skill_names:
            continue
        seen_skill_names.add(normalized_name)
        skills.append(skill)

    grouped_skills = OrderedDict()
    category_labels = dict(Skill.CATEGORY_CHOICES)
    for skill in skills:
        grouped_skills.setdefault(skill.category, {
            'label': category_labels.get(skill.category, skill.category),
            'items': [],
        })
        grouped_skills[skill.category]['items'].append(skill)

    return render(request, 'skills.html', {'skills': skills, 'grouped_skills': grouped_skills.values()})

def projects_view(request):
    featured = Project.objects.filter(
        is_featured=True,
        is_published=True
    ).order_by('order').first()

    other_projects = Project.objects.filter(is_published=True)
    if featured:
        other_projects = other_projects.exclude(pk=featured.pk)
    other_projects = other_projects.order_by('order')

    secondary_projects = other_projects[:2]
    archive_projects = other_projects[2:]

    return render(request, 'projects.html', {
        'featured_project': featured,
        'other_projects': other_projects,
        'secondary_projects': secondary_projects,
        'archive_projects': archive_projects,
        'all_projects': Project.objects.filter(is_published=True).order_by('order'),
    })

def blog_view(request):
    published = BlogPost.objects.filter(published=True)
    labels = dict(BlogPost.LOG_TYPE_CHOICES)
    active_type = request.GET.get('type', '')
    if active_type not in labels:
        active_type = ''
    counts = {row['log_type']: row['n'] for row in published.order_by().values('log_type').annotate(n=Count('id'))}
    filters = [
        {'value': value, 'label': label, 'count': counts[value]}
        for value, label in BlogPost.LOG_TYPE_CHOICES if counts.get(value)
    ]
    posts = published.filter(log_type=active_type) if active_type else published
    return render(request, 'blog.html', {
        'posts': posts,
        'filters': filters,
        'active_type': active_type,
        'active_label': labels.get(active_type, ''),
        'total_count': sum(counts.values()),
    })

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, published=True)
    return render(request, 'blog_detail.html', {'post': post})

def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug, is_published=True)
    published = list(Project.objects.filter(is_published=True).order_by('order', 'id').only('pk', 'slug', 'title', 'case_number'))
    index = next(i for i, p in enumerate(published) if p.pk == project.pk)
    return render(request, 'project_detail.html', {
        'project': project,
        'decisions': list(project.decisions.all()),
        'incidents': list(project.incidents.all()),
        'replays': list(project.replays.filter(is_published=True).select_related('project')),
        'previous_case': published[index - 1] if index > 0 else None,
        'next_case': published[index + 1] if index + 1 < len(published) else None,
    })

def contact_view(request):
    site_settings = SiteSettings.load()
    if request.method == 'POST':
        if not site_settings.contact_form_active:
            messages.info(request, 'The contact form is currently unavailable. Please email directly.')
            return redirect('contact')

        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('contact')
    
    return render(request, 'contact.html')

CHAT_RATE_LIMIT = 20          # messages
CHAT_RATE_WINDOW_S = 60       # per this many seconds, per visitor
CHAT_MAX_MESSAGE = 300

_EMAIL_RE = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
_PHONE_RE = re.compile(r'\+?\(?\d[\d\s().-]{6,}\d')


def scrub_question(text):
    """Remove emails and phone numbers before a question is stored."""
    text = _EMAIL_RE.sub('[email]', text)
    text = _PHONE_RE.sub('[phone]', text)
    return text[:CHAT_MAX_MESSAGE]


def _client_key(request):
    # PythonAnywhere puts the visitor's address in X-Real-IP (REMOTE_ADDR is its load balancer).
    ip = request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR', '')
    digest = hashlib.sha256(f'{settings.SECRET_KEY}:{ip}'.encode()).hexdigest()[:32]
    return f'chat-rate:{digest}'


def _rate_limited(request):
    key = _client_key(request)
    cache.add(key, 0, CHAT_RATE_WINDOW_S)
    try:
        count = cache.incr(key)
    except ValueError:  # expired between add and incr
        cache.set(key, 1, CHAT_RATE_WINDOW_S)
        count = 1
    return count > CHAT_RATE_LIMIT


@require_POST
def chat_reply(request):
    if _rate_limited(request):
        return JsonResponse({
            'reply': "You're sending messages quickly. Please wait a minute and try again.",
            'links': [],
            'chips': [],
        }, status=429)

    message = request.POST.get('message', '')
    if not message and request.body:
        try:
            payload = json.loads(request.body)
            message = payload.get('message', '')
        except (ValueError, AttributeError):
            message = ''
    if not isinstance(message, str):
        message = ''
    message = message.strip()[:CHAT_MAX_MESSAGE]

    result = chatbot.get_reply(message)
    if message:
        ChatQuery.objects.create(
            question=scrub_question(message),
            matched_intent=result['intent'],
            was_fallback=result['fallback'],
        )
        ChatQuery.objects.filter(
            created_at__lt=timezone.now() - timedelta(days=ChatQuery.RETENTION_DAYS)
        ).delete()
    return JsonResponse({'reply': result['reply'], 'links': result['links'], 'chips': result['chips']})
