from collections import OrderedDict

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import About, Skill, Project, BlogPost, ContactMessage

def index(request):
    about = About.objects.first()
    skills = Skill.objects.all()
    projects = Project.objects.filter(featured=True)[:3]
    return render(request, 'index.html', {'about': about, 'skills': skills, 'projects': projects})

def about_view(request):
    from .models import (About, WhatIDo, EducationEntry,
                         ExperienceEntry, EventEntry,
                         AdditionalCertification)
    about = About.objects.first()
    what_i_do = WhatIDo.objects.all()
    education = EducationEntry.objects.all()
    
    # Split experience by side for paired timeline rendering
    experience_entries = ExperienceEntry.objects.all()
    
    # Group experience into pairs for the two-column timeline
    # Each pair = (left_entry, right_entry) — either can be None
    experience_left = experience_entries.filter(side='left')
    experience_right = experience_entries.filter(side='right')
    experience_all = ExperienceEntry.objects.all().order_by('order')
    
    events = EventEntry.objects.all()
    certifications = AdditionalCertification.objects.all()
    
    return render(request, 'about.html', {
        'about': about,
        'what_i_do': what_i_do,
        'education': education,
        'experience_left': experience_left,
        'experience_right': experience_right,
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
    projects = Project.objects.all()
    return render(request, 'projects.html', {'projects': projects})

def blog_view(request):
    posts = BlogPost.objects.filter(published=True)
    return render(request, 'blog.html', {'posts': posts})

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, published=True)
    return render(request, 'blog_detail.html', {'post': post})

def contact_view(request):
    if request.method == 'POST':
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
