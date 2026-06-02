from datetime import date

from django.db import models

class About(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='about/', blank=True, null=True)
    resume = models.FileField(upload_to='resume/', blank=True, null=True)
    bio_paragraph_1 = models.TextField(blank=True)
    bio_paragraph_2 = models.TextField(blank=True)
    bio_paragraph_3 = models.TextField(blank=True)
    stat_accuracy = models.CharField(max_length=20, default='99.88%')
    stat_accuracy_label = models.CharField(max_length=50, default='Detection Accuracy')
    stat_agents = models.CharField(max_length=20, default='4')
    stat_agents_label = models.CharField(max_length=50, default='MCP Agents Built')
    stat_teams = models.CharField(max_length=20, default='25+')
    stat_teams_label = models.CharField(max_length=50, default='Teams at TechTrotter 2K25')
    stat_projects = models.CharField(max_length=20, default='3')
    stat_projects_label = models.CharField(max_length=50, default='Major Projects')
    subtitle = models.CharField(
        max_length=200,
        default='Agentic AI Engineer · B.Tech CSE-AI · Kurnool, India'
    )
    
    class Meta:
        verbose_name_plural = "About"
    
    def __str__(self):
        return self.title

class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('agentic', 'Agentic AI & MCP'),
        ('ml', 'ML & Data'),
        ('web', 'Web & APIs'),
        ('languages', 'Languages'),
        ('security', 'Security'),
        ('tools', 'Tools'),
        ('soft', 'Soft Skills'),
    ]

    name = models.CharField(max_length=100)
    percentage = models.IntegerField(default=0)
    icon = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='tools')
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['category', 'order', 'name']
    
    def __str__(self):
        return self.name

class SiteAppearance(models.Model):
    site_name = models.CharField(max_length=120, default='Karu Praneeth Kumar')
    hero_title = models.CharField(max_length=160, default='Karu Praneeth Kumar')
    typewriter_phrases = models.TextField(
        default='Agentic AI Engineer\nMCP Systems Builder\nML & Full-Stack Developer',
        help_text='One phrase per line. These appear in the homepage typewriter.'
    )
    hero_description = models.TextField(
        default='Building agentic AI systems, MCP pipelines, and intelligent automation tools. Final-year B.Tech CSE-AI @ SJCET Bengaluru. Open to agentic AI engineering roles and startup internships.'
    )
    primary_color = models.CharField(max_length=7, default='#3b82f6', help_text='Hex color, for example #3b82f6')
    secondary_color = models.CharField(max_length=7, default='#8b5cf6', help_text='Hex color, for example #8b5cf6')
    accent_color = models.CharField(max_length=7, default='#06b6d4', help_text='Hex color, for example #06b6d4')
    profile_image = models.ImageField(upload_to='appearance/', blank=True, null=True)
    resume = models.FileField(upload_to='resume/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site Appearance'
        verbose_name_plural = 'Site Appearance'

    def __str__(self):
        return self.site_name

    def typewriter_list(self):
        phrases = [phrase.strip() for phrase in self.typewriter_phrases.splitlines() if phrase.strip()]
        return phrases or ['Agentic AI Engineer', 'MCP Systems Builder', 'ML & Full-Stack Developer']

class SiteSettings(models.Model):
    profile_image = models.ImageField(
        upload_to='appearance/',
        blank=True,
        null=True,
        help_text='Profile image used in the homepage hero.'
    )
    resume = models.FileField(
        upload_to='resume/',
        blank=True,
        null=True,
        help_text='Resume PDF linked from the site.'
    )
    hero_name_display = models.CharField(
        max_length=100,
        default='Karu Praneeth Kumar'
    )
    hero_roles = models.TextField(
        help_text='One role per line. These rotate in the hero.',
        default='Agentic AI Engineer\nML Practitioner\nFull Stack Developer'
    )
    hero_description = models.TextField(
        help_text='Short paragraph shown below the title.',
        default='Building agentic AI systems, MCP pipelines, and intelligent automation tools. Final-year B.Tech CSE-AI @ SJCET Bengaluru. Open to agentic AI engineering roles and startup internships.'
    )
    hero_cta_primary_label = models.CharField(
        max_length=50,
        default='Begin the Story'
    )
    hero_cta_primary_url = models.CharField(
        max_length=200,
        default='/about/'
    )
    hero_cta_secondary_label = models.CharField(
        max_length=50,
        default='View the Work'
    )
    hero_cta_secondary_url = models.CharField(
        max_length=200,
        default='/projects/'
    )

    github_url = models.URLField(blank=True, default='https://github.com/BunnyPraneeth5')
    linkedin_url = models.URLField(blank=True, default='https://linkedin.com/in/karu-praneeth-kumar')
    kaggle_url = models.URLField(blank=True, default='https://www.kaggle.com/bunnypraneeth5')
    hackerrank_url = models.URLField(blank=True, default='https://hackerrank.com/profile/karu_praneeth')
    leetcode_url = models.URLField(blank=True, default='https://leetcode.com/u/praneethkumar_/')

    contact_email = models.EmailField(default='karupraneethkumar@gmail.com')
    contact_location = models.CharField(max_length=100, default='Andhra Pradesh, India')
    contact_tagline = models.CharField(
        max_length=200,
        default='A quiet place for the next conversation.'
    )
    contact_form_active = models.BooleanField(
        default=True,
        help_text='Uncheck to hide the form and show email link only.'
    )

    meta_title = models.CharField(max_length=100, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def hero_roles_list(self):
        roles = [role.strip() for role in self.hero_roles.splitlines() if role.strip()]
        return roles or ['Agentic AI Engineer', 'ML Practitioner', 'Full Stack Developer']

    def __str__(self):
        return 'Site Settings'

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    short_description = models.TextField(
        blank=True,
        help_text='Shown in the project card.'
    )
    long_description = models.TextField(
        blank=True,
        help_text='Optional extended case study text.'
    )
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    thumbnail = models.ImageField(
        upload_to='projects/',
        null=True,
        blank=True
    )
    live_url = models.URLField(blank=True)
    live_demo_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    technologies = models.CharField(max_length=300, blank=True, default='')
    tech_tags = models.CharField(
        max_length=500,
        blank=True,
        help_text='Comma-separated. e.g. Python, MCP, PyQt6'
    )
    featured = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(
        default=0,
        help_text='Lower number appears first.'
    )
    metric_kicker = models.CharField(
        max_length=50,
        blank=True,
        help_text='Small label above metrics, e.g. MCP PIPELINE.'
    )
    secondary_kicker = models.CharField(
        max_length=50,
        blank=True,
        help_text='Small label above non-featured project titles.'
    )
    metric_1_value = models.CharField(
        max_length=20,
        blank=True,
        help_text='e.g. 99.88%'
    )
    metric_1_label = models.CharField(
        max_length=50,
        blank=True,
        help_text='e.g. Detection Accuracy'
    )
    metric_2_value = models.CharField(max_length=20, blank=True)
    metric_2_label = models.CharField(max_length=50, blank=True)
    metric_3_value = models.CharField(max_length=20, blank=True)
    metric_3_label = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']

    @property
    def tech_tags_list(self):
        source = self.tech_tags or self.technologies
        return [tag.strip() for tag in source.split(',') if tag.strip()]

    @property
    def card_description(self):
        return self.short_description or self.description

    @property
    def card_image(self):
        return self.thumbnail or self.image

    @property
    def primary_live_url(self):
        return self.live_demo_url or self.live_url

    def save(self, *args, **kwargs):
        if not self.description and self.short_description:
            self.description = self.short_description
        if not self.technologies and self.tech_tags:
            self.technologies = self.tech_tags
        if not self.live_url and self.live_demo_url:
            self.live_url = self.live_demo_url
        if self.is_featured and not self.featured:
            self.featured = True
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    event_date = models.DateField(default=date.today)
    content = models.TextField()
    excerpt = models.TextField(max_length=300)
    image = models.ImageField(upload_to='blog/', blank=True, null=True)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"

class WhatIDo(models.Model):
    item = models.CharField(max_length=200)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'What I Do Item'
        verbose_name_plural = 'What I Do Items'
    
    def __str__(self):
        return self.item

class EducationEntry(models.Model):
    year_range = models.CharField(max_length=20)
    degree = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200)
    institution = models.CharField(max_length=300)
    bullet_1 = models.CharField(max_length=300, blank=True)
    bullet_2 = models.CharField(max_length=300, blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Education Entry'
        verbose_name_plural = 'Education Entries'
    
    def __str__(self):
        return f"{self.degree} - {self.institution}"

class ExperienceEntry(models.Model):
    SIDE_CHOICES = [('left', 'Left'), ('right', 'Right')]
    
    year_label = models.CharField(max_length=50)
    organization = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    tags = models.CharField(
        max_length=500, blank=True,
        help_text='Comma-separated tags e.g. Python,MCP,AI')
    certificate_file = models.FileField(
        upload_to='certificates/', blank=True, null=True)
    certificate_file_2 = models.FileField(
        upload_to='certificates/', blank=True, null=True,
        help_text='Second certificate file if needed')
    icon_class = models.CharField(
        max_length=100, default='fas fa-certificate',
        help_text='Font Awesome icon class e.g. fas fa-trophy')
    icon_color = models.CharField(
        max_length=50, default='text-blue-400',
        help_text='Tailwind color class e.g. text-blue-400')
    side = models.CharField(
        max_length=10, choices=SIDE_CHOICES, default='left')
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Experience / Certification Entry'
        verbose_name_plural = 'Experience / Certification Entries'
    
    def get_tags_list(self):
        if self.tags:
            return [t.strip() for t in self.tags.split(',')]
        return []
    
    def __str__(self):
        return f"{self.organization} - {self.role}"

class EventEntry(models.Model):
    title = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    year = models.CharField(max_length=20)
    location = models.CharField(max_length=200)
    description = models.TextField()
    stat_1_value = models.CharField(max_length=50, blank=True)
    stat_1_label = models.CharField(max_length=100, blank=True)
    stat_2_value = models.CharField(max_length=50, blank=True)
    stat_2_label = models.CharField(max_length=100, blank=True)
    stat_3_value = models.CharField(max_length=50, blank=True)
    stat_3_label = models.CharField(max_length=100, blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Event / Leadership Entry'
        verbose_name_plural = 'Events / Leadership Entries'
    
    def __str__(self):
        return self.title

class AdditionalCertification(models.Model):
    title = models.CharField(max_length=200)
    icon_class = models.CharField(
        max_length=100, default='fas fa-certificate',
        help_text='Font Awesome icon class')
    icon_color = models.CharField(
        max_length=50, default='text-blue-400',
        help_text='Tailwind color class e.g. text-blue-400')
    certificate_file = models.FileField(
        upload_to='certificates/', blank=True, null=True)
    see_experience_note = models.CharField(
        max_length=100, blank=True,
        help_text='If no file, show this note e.g. (See Experience)')
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Additional Certification'
        verbose_name_plural = 'Additional Certifications'
    
    def __str__(self):
        return self.title
