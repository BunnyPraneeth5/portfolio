from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import (
    About, Skill, Project, BlogPost, ContactMessage,
    WhatIDo, EducationEntry, ExperienceEntry, EventEntry,
    Certification, SiteSettings, CaseDecision, CaseIncident, ProjectReplay,
)
from .replays import MAX_FILE_BYTES, ReplayValidationError, load_replay_file

admin.site.site_header = 'KP Portfolio Administration'
admin.site.site_title = 'KP Admin'
admin.site.index_title = 'Portfolio Control Center'

@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display = ['title']
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'subtitle')
        }),
        ('Bio Paragraphs', {
            'fields': (
                'bio_paragraph_1',
                'bio_paragraph_2',
                'bio_paragraph_3',
                'description'
            )
        }),
        ('Stats', {
            'fields': (
                ('stat_accuracy', 'stat_accuracy_label'),
                ('stat_agents', 'stat_agents_label'),
                ('stat_teams', 'stat_teams_label'),
                ('stat_projects', 'stat_projects_label'),
            )
        }),
    )

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_featured', 'order']
    list_filter = ['category']
    list_editable = ['category', 'is_featured', 'order']
    search_fields = ['name']
    ordering = ['category', 'order', 'name']

class CaseDecisionInline(admin.StackedInline):
    model = CaseDecision
    extra = 0
    fields = ('code', 'decision', 'tradeoff', 'order')


class CaseIncidentInline(admin.StackedInline):
    model = CaseIncident
    extra = 0
    fields = ('symptom', 'root_cause', 'fix', 'order')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    inlines = [CaseDecisionInline, CaseIncidentInline]
    list_display = ['title', 'slug', 'status', 'is_featured', 'is_published', 'order', 'thumbnail_preview']
    list_filter = ['status', 'is_featured', 'is_published']
    list_editable = ['status', 'is_featured', 'is_published', 'order']
    search_fields = ['title', 'short_description', 'long_description', 'brief', 'tech_tags']
    ordering = ['order']
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Basic Info', {
            'fields': (
                'title',
                'slug',
                'short_description',
                'long_description',
                'thumbnail',
                'tech_tags',
                'order',
                'status',
                'is_featured',
                'is_published',
            )
        }),
        ('Case file', {
            'description': 'Each section shows on the project page only when it has content. Decisions and incidents are below.',
            'fields': ('case_number', 'brief', 'architecture_notes', 'open_leads')
        }),
        ('Links', {
            'fields': ('github_url', 'live_demo_url')
        }),
        ('Metrics (optional)', {
            'fields': (
                'metric_kicker',
                'secondary_kicker',
                'metric_1_value', 'metric_1_label',
                'metric_2_value', 'metric_2_label',
                'metric_3_value', 'metric_3_label',
            ),
            'classes': ('collapse',)
        }),
    )

    def thumbnail_preview(self, obj):
        image = obj.thumbnail
        if image:
            return format_html(
                '<img src="{}" height="40" style="border-radius:2px;"/>',
                image.url
            )
        return "-"
    thumbnail_preview.short_description = 'Image'

class ProjectReplayAdminForm(forms.ModelForm):
    replay_file = forms.FileField(
        required=False,
        help_text=(
            'Upload a sanitized .json replay ({"title", "duration_s", "steps"}). '
            'It replaces the steps and fills title / duration if they are empty. '
            'Checked for format, step limits and obvious leaks (emails, keys, public IPs).'
        ),
    )

    class Meta:
        model = ProjectReplay
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Title and duration can come from the uploaded file.
        self.fields['title'].required = False
        self.fields['duration_s'].required = False

    def clean(self):
        cleaned = super().clean()
        upload = cleaned.get('replay_file')
        if upload:
            if upload.size > MAX_FILE_BYTES:
                self.add_error('replay_file', f'File is larger than {MAX_FILE_BYTES // 1024} KB.')
                return cleaned
            try:
                doc = load_replay_file(upload.read())
            except ReplayValidationError as err:
                self.add_error('replay_file', err.messages)
                return cleaned
            cleaned['steps'] = doc['steps']
            if not cleaned.get('title'):
                cleaned['title'] = doc['title']
            if cleaned.get('duration_s') in (None, ''):
                cleaned['duration_s'] = doc['duration_s']
        if not cleaned.get('title'):
            self.add_error('title', 'Enter a title or upload a replay file.')
        if cleaned.get('duration_s') in (None, ''):
            self.add_error('duration_s', 'Enter a duration or upload a replay file.')
        if not upload and not cleaned.get('steps'):
            self.add_error('replay_file', 'Upload a replay file.')
        return cleaned


@admin.register(ProjectReplay)
class ProjectReplayAdmin(admin.ModelAdmin):
    form = ProjectReplayAdminForm
    list_display = ['title', 'project', 'step_count', 'duration_label', 'is_published', 'is_featured_on_home', 'order']
    list_filter = ['project', 'is_published']
    list_editable = ['is_published', 'is_featured_on_home', 'order']
    search_fields = ['title', 'project__title']
    fieldsets = (
        ('Replay', {
            'fields': ('project', 'replay_file', 'title', 'duration_s', 'order')
        }),
        ('Visibility', {
            'description': 'Run the sanitization checklist before publishing: no API keys, tokens, file paths, usernames, real IPs, emails or private data; long tool outputs shortened to one line.',
            'fields': ('is_published', 'is_featured_on_home')
        }),
        ('Steps (from the file)', {
            'fields': ('steps',),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Steps')
    def step_count(self, obj):
        return obj.step_count

    @admin.display(description='Duration')
    def duration_label(self, obj):
        return obj.duration_label


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_date', 'published', 'created_at', 'thumbnail_preview']
    list_filter = ['published', 'created_at']
    list_editable = ['published']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    fields = [
        'title',
        'slug',
        'event_date',
        'content',
        'excerpt',
        'image',
        'published',
    ]

    def thumbnail_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" height="40" style="border-radius:2px;"/>',
                obj.image.url
            )
        return "-"
    thumbnail_preview.short_description = 'Image'

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at']
    readonly_fields = ['created_at']

@admin.register(WhatIDo)
class WhatIDoAdmin(admin.ModelAdmin):
    list_display = ['item', 'order']
    list_editable = ['order']

@admin.register(EducationEntry)
class EducationEntryAdmin(admin.ModelAdmin):
    list_display = [
        'degree', 'institution', 'year_range', 'order']
    list_editable = ['order']

class ExperienceEntryAdminForm(forms.ModelForm):
    class Meta:
        model = ExperienceEntry
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_date'].required = True

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end = cleaned.get('end_date')
        if cleaned.get('is_current') and end:
            self.add_error('end_date', 'Leave the end date empty for a current role.')
        if start and end and end < start:
            self.add_error('end_date', 'End date cannot be before the start date.')
        return cleaned

@admin.register(ExperienceEntry)
class ExperienceEntryAdmin(admin.ModelAdmin):
    form = ExperienceEntryAdminForm
    list_display = [
        'organization', 'role', 'employment_type',
        'start_date', 'end_date', 'is_current', 'order']
    list_editable = ['order']
    list_filter = ['employment_type', 'is_current']
    search_fields = ['organization', 'role', 'summary']
    fieldsets = (
        ('Role', {
            'fields': ('organization', 'role', 'employment_type')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'is_current')
        }),
        ('Details', {
            'fields': ('location', 'is_remote', 'summary', 'highlights', 'tags', 'order')
        }),
        ('Links', {
            'fields': ('related_project',)
        }),
    )

@admin.register(EventEntry)
class EventEntryAdmin(admin.ModelAdmin):
    list_display = ['title', 'role', 'year', 'order']
    list_editable = ['order']

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'issuer', 'category', 'issued_date', 'has_file', 'order']
    list_editable = ['order']
    list_filter = ['category']
    search_fields = ['title', 'issuer']

    @admin.display(boolean=True, description='Has file')
    def has_file(self, obj):
        return obj.has_file

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Profile & Resume', {
            'fields': (
                'profile_image',
                'resume',
            )
        }),
        ('Hero Section', {
            'fields': (
                'hero_name_display',
                'hero_roles',
                'hero_description',
                'hero_cta_primary_label',
                'hero_cta_primary_url',
                'hero_cta_secondary_label',
                'hero_cta_secondary_url',
            )
        }),
        ('Availability', {
            'fields': (
                'open_to_work',
                'open_to_remote',
                'open_to_internship',
                'notice_period',
                'looking_for',
            )
        }),
        ('Social Links', {
            'fields': (
                'github_url',
                'linkedin_url',
                'kaggle_url',
                'hackerrank_url',
                'leetcode_url',
            )
        }),
        ('Contact Section', {
            'fields': (
                'contact_email',
                'contact_location',
                'contact_tagline',
                'contact_form_active',
            )
        }),
        ('SEO', {
            'fields': (
                'meta_title',
                'meta_description',
            ),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
