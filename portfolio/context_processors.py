from django.templatetags.static import static

from .models import About, SiteAppearance, SiteSettings


def site_appearance(request):
    appearance = SiteAppearance.objects.first()
    typewriter_phrases = appearance.typewriter_list() if appearance else [
        'Agentic AI Engineer',
        'MCP Systems Builder',
        'ML & Full-Stack Developer',
    ]

    return {
        'site_appearance': appearance,
        'typewriter_phrases': typewriter_phrases,
    }


def site_settings(request):
    settings = SiteSettings.load()
    appearance = SiteAppearance.objects.first()
    about = About.objects.first()

    profile_image_url = static('assets/images/portrait.png')
    if about and about.image:
        profile_image_url = about.image.url
    if appearance and appearance.profile_image:
        profile_image_url = appearance.profile_image.url
    if settings.profile_image:
        profile_image_url = settings.profile_image.url

    resume_url = static('assets/resume/Karu_Praneeth_Kumar.pdf')
    if about and about.resume:
        resume_url = about.resume.url
    if appearance and appearance.resume:
        resume_url = appearance.resume.url
    if settings.resume:
        resume_url = settings.resume.url

    return {
        'site_settings': settings,
        'profile_image_url': profile_image_url,
        'resume_url': resume_url,
    }
