import json
from collections import OrderedDict

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from . import chatbot
from .models import (
    About, Skill, Project, BlogPost, ContactMessage, SiteSettings,
    EducationEntry, ExperienceEntry,
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
        # Filled in Phase 4 (ProjectReplay); the section stays hidden until then.
        'replay_preview': None,
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
    
    return render(request, 'about.html', {
        'about': about,
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
    posts = BlogPost.objects.filter(published=True)
    return render(request, 'blog.html', {'posts': posts})

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
        # Filled in Phase 4 (ProjectReplay); the Replay section stays hidden until then.
        'replay': None,
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

@require_POST
def chat_reply(request):
    message = request.POST.get('message', '')
    if not message and request.body:
        try:
            payload = json.loads(request.body)
            message = payload.get('message', '')
        except (ValueError, AttributeError):
            message = ''
    reply = chatbot.get_reply(message)
    return JsonResponse({'reply': reply})
