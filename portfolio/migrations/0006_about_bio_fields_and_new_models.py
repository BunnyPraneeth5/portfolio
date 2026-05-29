from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0005_seed_default_skills'),
    ]

    operations = [
        migrations.AddField(
            model_name='about',
            name='bio_paragraph_1',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='about',
            name='bio_paragraph_2',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='about',
            name='bio_paragraph_3',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='about',
            name='stat_accuracy',
            field=models.CharField(default='99.88%', max_length=20),
        ),
        migrations.AddField(
            model_name='about',
            name='stat_accuracy_label',
            field=models.CharField(default='Detection Accuracy', max_length=50),
        ),
        migrations.AddField(
            model_name='about',
            name='stat_agents',
            field=models.CharField(default='4', max_length=20),
        ),
        migrations.AddField(
            model_name='about',
            name='stat_agents_label',
            field=models.CharField(default='MCP Agents Built', max_length=50),
        ),
        migrations.AddField(
            model_name='about',
            name='stat_teams',
            field=models.CharField(default='25+', max_length=20),
        ),
        migrations.AddField(
            model_name='about',
            name='stat_teams_label',
            field=models.CharField(default='Teams at TechTrotter 2K25', max_length=50),
        ),
        migrations.AddField(
            model_name='about',
            name='stat_projects',
            field=models.CharField(default='3', max_length=20),
        ),
        migrations.AddField(
            model_name='about',
            name='stat_projects_label',
            field=models.CharField(default='Major Projects', max_length=50),
        ),
        migrations.AddField(
            model_name='about',
            name='subtitle',
            field=models.CharField(default='Agentic AI Engineer · B.Tech CSE-AI · Kurnool, India', max_length=200),
        ),
        migrations.CreateModel(
            name='WhatIDo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.CharField(max_length=200)),
                ('order', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'What I Do Item',
                'verbose_name_plural': 'What I Do Items',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='EducationEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year_range', models.CharField(max_length=20)),
                ('degree', models.CharField(max_length=200)),
                ('field_of_study', models.CharField(max_length=200)),
                ('institution', models.CharField(max_length=300)),
                ('bullet_1', models.CharField(blank=True, max_length=300)),
                ('bullet_2', models.CharField(blank=True, max_length=300)),
                ('order', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Education Entry',
                'verbose_name_plural': 'Education Entries',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='ExperienceEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year_label', models.CharField(max_length=50)),
                ('organization', models.CharField(max_length=200)),
                ('role', models.CharField(max_length=200)),
                ('tags', models.CharField(blank=True, help_text='Comma-separated tags e.g. Python,MCP,AI', max_length=500)),
                ('certificate_file', models.FileField(blank=True, null=True, upload_to='certificates/')),
                ('certificate_file_2', models.FileField(blank=True, help_text='Second certificate file if needed', null=True, upload_to='certificates/')),
                ('icon_class', models.CharField(default='fas fa-certificate', help_text='Font Awesome icon class e.g. fas fa-trophy', max_length=100)),
                ('icon_color', models.CharField(default='text-blue-400', help_text='Tailwind color class e.g. text-blue-400', max_length=50)),
                ('side', models.CharField(choices=[('left', 'Left'), ('right', 'Right')], default='left', max_length=10)),
                ('order', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Experience / Certification Entry',
                'verbose_name_plural': 'Experience / Certification Entries',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='EventEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('role', models.CharField(max_length=200)),
                ('year', models.CharField(max_length=20)),
                ('location', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('stat_1_value', models.CharField(blank=True, max_length=50)),
                ('stat_1_label', models.CharField(blank=True, max_length=100)),
                ('stat_2_value', models.CharField(blank=True, max_length=50)),
                ('stat_2_label', models.CharField(blank=True, max_length=100)),
                ('stat_3_value', models.CharField(blank=True, max_length=50)),
                ('stat_3_label', models.CharField(blank=True, max_length=100)),
                ('order', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Event / Leadership Entry',
                'verbose_name_plural': 'Events / Leadership Entries',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='AdditionalCertification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('icon_class', models.CharField(default='fas fa-certificate', help_text='Font Awesome icon class', max_length=100)),
                ('icon_color', models.CharField(default='text-blue-400', help_text='Tailwind color class e.g. text-blue-400', max_length=50)),
                ('certificate_file', models.FileField(blank=True, null=True, upload_to='certificates/')),
                ('see_experience_note', models.CharField(blank=True, help_text='If no file, show this note e.g. (See Experience)', max_length=100)),
                ('order', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Additional Certification',
                'verbose_name_plural': 'Additional Certifications',
                'ordering': ['order'],
            },
        ),
    ]
