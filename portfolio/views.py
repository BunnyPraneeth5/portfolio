import hashlib
import json
import re
from collections import OrderedDict
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.db.models import Count, Prefetch, Q
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
    published = list(Project.objects.filter(is_published=True).order_by('order'))
    featured = [p for p in published if p.is_featured]
    # Roster shows featured agents only; with none featured, the first four.
    roster = featured or published[:4]
    flagship = next((p for p in published if p.status == 'flagship'), None)
    if flagship is None:
        flagship = next((p for p in published if p.is_featured), published[0] if published else None)
    return render(request, 'index.html', {
        'recent_experience': ExperienceEntry.newest_first().first(),
        'education': EducationEntry.objects.first(),
        'core_stack': Skill.objects.filter(is_featured=True)[:8],
        'roster': roster,
        'roster_is_featured': bool(featured),
        'case_total': len(published),
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
    experience = list(ExperienceEntry.newest_first().select_related('related_project'))
    certifications = list(Certification.objects.all())
    paragraphs = []
    if about:
        paragraphs = [text for text in (about.description, about.bio_paragraph_1,
                                        about.bio_paragraph_2, about.bio_paragraph_3) if text.strip()]

    return render(request, 'about.html', {
        'about': about,
        # Story card: first paragraph shown, the rest behind "Read the full story".
        'story_lead': paragraphs[:1],
        'story_more': paragraphs[1:],
        'recent_role': experience[0] if experience else None,
        'what_i_do': list(WhatIDo.objects.all()),
        'education': list(EducationEntry.objects.all()),
        'experience_all': experience,
        'events': list(EventEntry.objects.all()),
        'featured_certs': [cert for cert in certifications if cert.is_featured],
        'other_certs': [cert for cert in certifications if not cert.is_featured],
        'cert_total': len(certifications),
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

    # "Used in": published projects whose tech tags exactly match a part of the skill name
    # ("Django / DRF" matches the tags Django or DRF). Same-title projects are folded together.
    tagged = [(p, {tag.casefold() for tag in p.tech_tags_list})
              for p in Project.objects.filter(is_published=True).order_by('order', 'id')]
    for skill in skills:
        parts = {part.strip().casefold() for part in re.split(r'[/&]', skill.name) if part.strip()}
        cases = OrderedDict()
        for project, tags in tagged:
            if parts & tags:
                cases.setdefault(project.title, {'project': project, 'count': 0})['count'] += 1
        skill.used_in = list(cases.values())
        skill.used_in_total = sum(case['count'] for case in skill.used_in)

    return render(request, 'skills.html', {
        'skills': skills,
        'core_skills': [skill for skill in skills if skill.is_featured],
        # Bigger areas first so the card grid fills evenly (stable for equal sizes).
        'grouped_skills': sorted(grouped_skills.values(), key=lambda group: -len(group['items'])),
    })

def projects_view(request):
    published = Project.objects.filter(is_published=True).order_by('order', 'id')
    # Featured projects are the case board; everything else goes to the archive table.
    featured = list(
        published.filter(is_featured=True)
        .annotate(decision_count=Count('decisions', distinct=True), incident_count=Count('incidents', distinct=True))
        .prefetch_related(Prefetch(
            'replays',
            queryset=ProjectReplay.objects.filter(is_published=True).select_related('project'),
            to_attr='published_replays',
        ))
    )
    archive = list(published.filter(is_featured=False))
    return render(request, 'projects.html', {
        'featured_cases': featured,
        'archive_projects': archive,
        'archive_has_year': any(project.year for project in archive),
        'total_count': len(featured) + len(archive),
        'board_has_replays': any(case.published_replays for case in featured),
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
    posts = posts.select_related('related_project').order_by('-event_date', '-created_at', '-pk')
    return render(request, 'blog.html', {
        'posts': posts,
        'filters': filters,
        'active_type': active_type,
        'active_label': labels.get(active_type, ''),
        'total_count': sum(counts.values()),
    })

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost.objects.select_related('related_project'), slug=slug, published=True)
    published = BlogPost.objects.filter(published=True).exclude(pk=post.pk)
    same_day = Q(event_date=post.event_date)
    same_time = same_day & Q(created_at=post.created_at)
    # Same order as the index: event date, then creation time, then id (ties happen on Windows clocks).
    older = (published.filter(Q(event_date__lt=post.event_date) | (same_day & Q(created_at__lt=post.created_at))
                              | (same_time & Q(pk__lt=post.pk)))
             .order_by('-event_date', '-created_at', '-pk').first())
    newer = (published.filter(Q(event_date__gt=post.event_date) | (same_day & Q(created_at__gt=post.created_at))
                              | (same_time & Q(pk__gt=post.pk)))
             .order_by('event_date', 'created_at', 'pk').first())
    return render(request, 'blog_detail.html', {'post': post, 'older_post': older, 'newer_post': newer})

def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug, is_published=True)
    published = list(Project.objects.filter(is_published=True).order_by('order', 'id').only('pk', 'slug', 'title', 'case_number'))
    index = next(i for i, p in enumerate(published) if p.pk == project.pk)
    return render(request, 'project_detail.html', {
        'project': project,
        'decisions': list(project.decisions.all()),
        'incidents': list(project.incidents.all()),
        'replays': list(project.replays.filter(is_published=True).select_related('project')),
        'case_logs': list(project.logs.filter(published=True)),
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
