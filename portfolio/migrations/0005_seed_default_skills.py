from django.db import migrations


def seed_default_skills(apps, schema_editor):
    Skill = apps.get_model('portfolio', 'Skill')
    skills = [
        ('MCP / Agentic AI', 85, 'fas fa-robot', 'agentic', 1),
        ('N8N Automation', 75, 'fas fa-project-diagram', 'agentic', 2),
        ('Scikit-Learn', 90, 'fas fa-chart-line', 'ml', 1),
        ('Pandas / NumPy', 90, 'fas fa-table', 'ml', 2),
        ('TensorFlow', 80, 'fas fa-brain', 'ml', 3),
        ('Django / DRF', 82, 'fab fa-python', 'web', 1),
        ('FastAPI', 82, 'fas fa-bolt', 'web', 2),
        ('HTML/CSS', 90, 'fab fa-html5', 'web', 3),
        ('Python', 90, 'fab fa-python', 'languages', 1),
        ('SQL', 85, 'fas fa-database', 'languages', 2),
        ('SOC L1 / SIEM', 75, 'fas fa-shield-alt', 'security', 1),
        ('Threat Intelligence', 70, 'fas fa-search', 'security', 2),
        ('Git & GitHub', 90, 'fab fa-git-alt', 'tools', 1),
        ('PyQt6', 75, 'fas fa-desktop', 'tools', 2),
        ('Jupyter', 88, 'fas fa-book', 'tools', 3),
    ]

    for name, percentage, icon, category, order in skills:
        Skill.objects.update_or_create(
            name=name,
            defaults={
                'percentage': percentage,
                'icon': icon,
                'category': category,
                'order': order,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0004_seed_siteappearance_and_skill_categories'),
    ]

    operations = [
        migrations.RunPython(seed_default_skills, migrations.RunPython.noop),
    ]
