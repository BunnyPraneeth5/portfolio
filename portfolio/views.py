from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import About, Skill, Project, BlogPost, ContactMessage

def index(request):
    about = About.objects.first()
    skills = Skill.objects.all()
    projects = Project.objects.filter(featured=True)[:3]
    return render(request, 'index.html', {'about': about, 'skills': skills, 'projects': projects})

def about_view(request):
    about = About.objects.first()
    return render(request, 'about.html', {'about': about})

def skills_view(request):
    skills = Skill.objects.all()
    return render(request, 'skills.html', {'skills': skills})

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
