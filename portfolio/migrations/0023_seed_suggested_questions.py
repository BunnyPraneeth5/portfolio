from django.db import migrations

# Default chips for the chat helper (editable in admin). Questions only, no claims.
DEFAULT_CHIPS = [
    'What projects has Bunny built?',
    "What are Bunny's core skills?",
    'Is Bunny open to roles?',
    'Can I see the resume?',
    'How can I contact Bunny?',
]
SOC_CHIP = 'How does SOC Copilot work?'


def seed(apps, schema_editor):
    SuggestedQuestion = apps.get_model('portfolio', 'SuggestedQuestion')
    Project = apps.get_model('portfolio', 'Project')
    if SuggestedQuestion.objects.exists():
        return
    chips = list(DEFAULT_CHIPS)
    if Project.objects.filter(slug='soc-copilot').exists():
        chips.append(SOC_CHIP)
    for order, text in enumerate(chips):
        SuggestedQuestion.objects.create(text=text, order=order)


def unseed(apps, schema_editor):
    SuggestedQuestion = apps.get_model('portfolio', 'SuggestedQuestion')
    SuggestedQuestion.objects.filter(text__in=DEFAULT_CHIPS + [SOC_CHIP]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0022_chat_helper'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
