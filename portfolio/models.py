from datetime import date

from django.db import models

class About(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
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
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='tools')
    is_featured = models.BooleanField(default=False, help_text='Show on homepage')
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['category', 'order', 'name']
    
    def __str__(self):
        return self.name

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

    open_to_work = models.BooleanField(default=True, help_text='Show as actively looking on the pet chat')
    open_to_remote = models.BooleanField(default=True)
    open_to_internship = models.BooleanField(default=True)
    notice_period = models.CharField(max_length=100, blank=True, default='Immediate')
    looking_for = models.CharField(
        max_length=200,
        blank=True,
        help_text='Shown in the homepage 30-second view, e.g. the kind of roles you want. Hidden when empty.'
    )

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
    STATUS_CHOICES = [
        ('flagship', 'Flagship'),
        ('live', 'Live'),
        ('benchmarking', 'Benchmarking'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    short_description = models.TextField(
        blank=True,
        help_text='Shown in the project card.'
    )
    long_description = models.TextField(
        blank=True,
        help_text='Optional extended case study text.'
    )
    thumbnail = models.ImageField(
        upload_to='projects/',
        null=True,
        blank=True
    )
    live_demo_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    tech_tags = models.CharField(
        max_length=500,
        blank=True,
        help_text='Comma-separated. e.g. Python, MCP, PyQt6'
    )
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        blank=True,
        help_text='Shown in the homepage agent roster. Leave empty to hide.'
    )
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
    case_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Shown as CASE FILE NO. 00X. Leave empty to hide the number.'
    )
    brief = models.TextField(
        blank=True,
        help_text='Case file "Brief". While empty, the long description is shown instead.'
    )
    architecture_notes = models.TextField(
        blank=True,
        help_text='Case file "Investigation": how it is built and why.'
    )
    open_leads = models.TextField(
        blank=True,
        help_text='Case file "Open leads": one per line.'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    STATUS_STAMPS = {
        'flagship': 'Flagship · Active',
        'live': 'Case closed · Shipped',
        'benchmarking': 'Active · Benchmarking',
        'archived': 'Case closed · Archived',
    }

    @property
    def case_label(self):
        return f'{self.case_number:03d}' if self.case_number is not None else ''

    @property
    def status_stamp(self):
        return self.STATUS_STAMPS.get(self.status, '')

    @property
    def brief_text(self):
        return self.brief.strip() or self.long_description.strip()

    @property
    def open_leads_list(self):
        return [line.strip() for line in self.open_leads.splitlines() if line.strip()]

    @property
    def metrics(self):
        pairs = [
            (self.metric_1_value, self.metric_1_label),
            (self.metric_2_value, self.metric_2_label),
            (self.metric_3_value, self.metric_3_label),
        ]
        return [{'value': value, 'label': label} for value, label in pairs if value]

    @property
    def tech_tags_list(self):
        return [tag.strip() for tag in self.tech_tags.split(',') if tag.strip()]

    @property
    def card_description(self):
        return self.short_description

    @property
    def card_image(self):
        return self.thumbnail

    @property
    def primary_live_url(self):
        return self.live_demo_url

    def __str__(self):
        return self.title

class CaseDecision(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='decisions')
    code = models.CharField(max_length=20, help_text='e.g. D-01')
    decision = models.TextField()
    tradeoff = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Case decision'
        verbose_name_plural = 'Case decisions'

    def __str__(self):
        return f'{self.project.title} {self.code}'

class CaseIncident(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='incidents')
    symptom = models.TextField()
    root_cause = models.TextField()
    fix = models.TextField()
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Case incident'
        verbose_name_plural = 'Case incidents'

    def __str__(self):
        return f'{self.project.title}: {self.symptom[:40]}'

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
    EMPLOYMENT_TYPE_CHOICES = [
        ('internship', 'Internship'),
        ('part_time', 'Part-time'),
        ('full_time', 'Full-time'),
        ('contract', 'Contract'),
        ('freelance', 'Freelance'),
    ]

    organization = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    employment_type = models.CharField(
        max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='internship')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(
        null=True, blank=True, help_text='Leave empty if this is your current role.')
    is_current = models.BooleanField(default=False)
    location = models.CharField(max_length=200, blank=True)
    is_remote = models.BooleanField(default=False)
    summary = models.TextField(blank=True, help_text='One or two lines.')
    highlights = models.TextField(blank=True, help_text='One bullet per line.')
    related_project = models.ForeignKey(
        'Project', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='experience_entries')
    tags = models.CharField(
        max_length=500, blank=True,
        help_text='Comma-separated tags e.g. Python,MCP,AI')
    order = models.IntegerField(
        default=0, help_text='Lower number appears first. Ties are sorted newest first.')

    class Meta:
        ordering = ['order', '-start_date']
        verbose_name = 'Professional Experience'
        verbose_name_plural = 'Professional Experience'

    @classmethod
    def newest_first(cls):
        """Current roles first, then by start date, newest first. Undated rows last."""
        return cls.objects.order_by(
            '-is_current', models.F('start_date').desc(nulls_last=True), 'order')

    def get_tags_list(self):
        if self.tags:
            return [t.strip() for t in self.tags.split(',') if t.strip()]
        return []

    @property
    def highlights_list(self):
        return [line.strip() for line in self.highlights.splitlines() if line.strip()]

    @property
    def date_range_label(self):
        if not self.start_date:
            return ''
        start = self.start_date.strftime('%b %Y')
        if self.is_current:
            return f'{start} – Present'
        if self.end_date:
            end = self.end_date.strftime('%b %Y')
            return start if end == start else f'{start} – {end}'
        return start

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

class Certification(models.Model):
    title = models.CharField(max_length=200)
    issuer = models.CharField(max_length=200, blank=True)
    category = models.CharField(
        max_length=100, blank=True,
        help_text='Optional group label e.g. Virtual Internship')
    issued_date = models.DateField(null=True, blank=True)
    certificate_file = models.FileField(
        upload_to='certificates/', blank=True, null=True)
    certificate_file_2 = models.FileField(
        upload_to='certificates/', blank=True, null=True,
        help_text='Second certificate file if needed')
    credential_url = models.URLField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'title']
        verbose_name = 'Certification'
        verbose_name_plural = 'Certifications'

    @property
    def has_file(self):
        return bool(self.certificate_file or self.certificate_file_2)

    def __str__(self):
        if self.issuer:
            return f"{self.issuer} - {self.title}"
        return self.title
