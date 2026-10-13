from django.templatetags.static import static
from django.utils.html import strip_tags

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

    description = settings.meta_description or ' '.join(strip_tags(settings.hero_description).split())
    if len(description) > 160:
        description = description[:157].rstrip() + '...'

    return {
        'site_settings': settings,
        'profile_image_url': profile_image_url,
        'absolute_profile_image_url': request.build_absolute_uri(profile_image_url),
        'default_meta_description': description,
        'resume_url': resume_url,
        # Shows the Replay nav link once at least one replay is public.
        'has_replays': ProjectReplay.objects.filter(is_published=True, project__is_published=True).exists(),
    }


def chat_helper(request):
    from .chatbot import greeting_text, suggested_chips  # chatbot imports this module

    return {
        'chat_greeting': greeting_text(),
        'chat_chips': suggested_chips(),
    }
