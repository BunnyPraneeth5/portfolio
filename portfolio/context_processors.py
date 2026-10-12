from django.templatetags.static import static

from .models import ProjectReplay, SiteSettings


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
        # Shows the Replay nav link once at least one replay is public.
        'has_replays': ProjectReplay.objects.filter(is_published=True, project__is_published=True).exists(),
    }
