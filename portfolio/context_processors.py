from django.templatetags.static import static

from .models import SiteSettings


def site_settings(request):
    settings = SiteSettings.load()

    profile_image_url = static('assets/images/portrait.png')
    if settings.profile_image:
        profile_image_url = settings.profile_image.url

    resume_url = static('assets/resume/Karu_Praneeth_Kumar.pdf')
    if settings.resume:
        resume_url = settings.resume.url

    return {
        'site_settings': settings,
        'profile_image_url': profile_image_url,
        'resume_url': resume_url,
    }
