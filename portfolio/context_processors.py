from django.templatetags.static import static

from .models import ProjectReplay, SiteSettings


def get_resume_url(settings):
    if settings.resume:
        return settings.resume.url
    return static('assets/resume/Karu_Praneeth_Kumar.pdf')


def site_settings(request):
    settings = SiteSettings.load()

    profile_image_url = static('assets/images/portrait.png')
    if settings.profile_image:
        profile_image_url = settings.profile_image.url

    resume_url = get_resume_url(settings)

    return {
        'site_settings': settings,
        'profile_image_url': profile_image_url,
        'resume_url': resume_url,
        # Shows the Replay nav link once at least one replay is public.
        'has_replays': ProjectReplay.objects.filter(is_published=True, project__is_published=True).exists(),
    }


def chat_helper(request):
    from .chatbot import _reply_greeting, suggested_chips  # chatbot imports this module

    return {
        'chat_greeting': _reply_greeting('')[0],
        'chat_chips': suggested_chips(),
    }
