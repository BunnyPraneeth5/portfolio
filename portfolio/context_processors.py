from .models import SiteAppearance


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
