from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0002_contactmessage_alter_blogpost_image_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='skill',
            options={'ordering': ['category', 'order', 'name']},
        ),
        migrations.AddField(
            model_name='skill',
            name='category',
            field=models.CharField(
                choices=[
                    ('agentic', 'Agentic AI & MCP'),
                    ('ml', 'ML & Data'),
                    ('web', 'Web & APIs'),
                    ('languages', 'Languages'),
                    ('security', 'Security'),
                    ('tools', 'Tools'),
                    ('soft', 'Soft Skills'),
                ],
                default='tools',
                max_length=30,
            ),
        ),
        migrations.CreateModel(
            name='SiteAppearance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_name', models.CharField(default='Karu Praneeth Kumar', max_length=120)),
                ('hero_title', models.CharField(default='Karu Praneeth Kumar', max_length=160)),
                ('typewriter_phrases', models.TextField(default='Agentic AI Engineer\nMCP Systems Builder\nML & Full-Stack Developer', help_text='One phrase per line. These appear in the homepage typewriter.')),
                ('hero_description', models.TextField(default='Building agentic AI systems, MCP pipelines, and intelligent automation tools. Final-year B.Tech CSE-AI @ SJCET Bengaluru. Open to agentic AI engineering roles and startup internships.')),
                ('primary_color', models.CharField(default='#3b82f6', help_text='Hex color, for example #3b82f6', max_length=7)),
                ('secondary_color', models.CharField(default='#8b5cf6', help_text='Hex color, for example #8b5cf6', max_length=7)),
                ('accent_color', models.CharField(default='#06b6d4', help_text='Hex color, for example #06b6d4', max_length=7)),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to='appearance/')),
                ('resume', models.FileField(blank=True, null=True, upload_to='resume/')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Site Appearance',
                'verbose_name_plural': 'Site Appearance',
            },
        ),
    ]
