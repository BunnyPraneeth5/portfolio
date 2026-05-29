from django.db import migrations


def seed_siteappearance_and_skill_categories(apps, schema_editor):
    SiteAppearance = apps.get_model('portfolio', 'SiteAppearance')
    Skill = apps.get_model('portfolio', 'Skill')

    if not SiteAppearance.objects.exists():
        SiteAppearance.objects.create()

    category_map = {
        'Python': 'languages',
        'SQL': 'languages',
        'Django': 'web',
        'Django / DRF': 'web',
        'FastAPI': 'web',
        'HTML5 & CSS3': 'web',
        'HTML/CSS': 'web',
        'Tailwind CSS': 'web',
        'MCP / Agentic AI': 'agentic',
        'N8N Automation': 'agentic',
        'Scikit-Learn': 'ml',
        'Scikit-learn / Pandas / NumPy': 'ml',
        'Pandas / NumPy': 'ml',
        'TensorFlow': 'ml',
        'Git & GitHub': 'tools',
        'PyQt6': 'tools',
        'Jupyter': 'tools',
        'SOC L1 / SIEM': 'security',
        'Threat Intelligence': 'security',
    }

    for skill in Skill.objects.all():
        category = category_map.get(skill.name)
        if category and skill.category != category:
            skill.category = category
            skill.save(update_fields=['category'])


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0003_siteappearance_alter_skill_options_skill_category'),
    ]

    operations = [
        migrations.RunPython(seed_siteappearance_and_skill_categories, migrations.RunPython.noop),
    ]
