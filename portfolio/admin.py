from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import (
    About, Skill, Project, BlogPost, ContactMessage, SiteAppearance,
    WhatIDo, EducationEntry, ExperienceEntry, EventEntry,
    AdditionalCertification, SiteSettings,
)

admin.site.site_header = 'KP Portfolio Administration'
admin.site.site_title = 'KP Admin'
admin.site.index_title = 'Portfolio Control Center'

@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display = ['title']
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'subtitle', 'image', 'resume')
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
    list_display = ['name', 'category', 'percentage', 'icon', 'order']
    list_filter = ['category']
    list_editable = ['category', 'percentage', 'icon', 'order']
    search_fields = ['name', 'icon']
    ordering = ['category', 'order', 'name']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_featured', 'is_published', 'order', 'thumbnail_preview']
    list_filter = ['is_featured', 'is_published']
    list_editable = ['is_featured', 'is_published', 'order']
    search_fields = ['title', 'short_description', 'long_description', 'tech_tags']
    ordering = ['order']
    fieldsets = (
        ('Basic Info', {
            'fields': (
                'title',
                'short_description',
                'long_description',
                'thumbnail',
                'tech_tags',
                'order',
                'is_featured',
                'is_published',
            )
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
        ('Legacy fields', {
            'fields': (
                'description',
                'image',
                'technologies',
                'live_url',
                'featured',
            ),
            'classes': ('collapse',)
        }),
    )

    def thumbnail_preview(self, obj):
        image = obj.thumbnail or obj.image
        if image:
            return format_html(
                '<img src="{}" height="40" style="border-radius:2px;"/>',
                image.url
            )
        return "-"
    thumbnail_preview.short_description = 'Image'

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

@admin.register(ExperienceEntry)
class ExperienceEntryAdmin(admin.ModelAdmin):
    list_display = [
        'organization', 'role', 'year_label', 'side', 'order']
    list_editable = ['order', 'side']
    list_filter = ['side']

@admin.register(EventEntry)
class EventEntryAdmin(admin.ModelAdmin):
    list_display = ['title', 'role', 'year', 'order']
    list_editable = ['order']

@admin.register(AdditionalCertification)
class AdditionalCertificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'order']
    list_editable = ['order']

@admin.register(SiteAppearance)
class SiteAppearanceAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Brand & Hero', {
            'fields': ('site_name', 'hero_title', 'typewriter_phrases', 'hero_description')
        }),
        ('Colors', {
            'fields': ('primary_color', 'secondary_color', 'accent_color')
        }),
        ('Files', {
            'fields': ('profile_image', 'resume')
        }),
    )
    list_display = ['site_name', 'primary_color', 'secondary_color', 'accent_color', 'updated_at']
    readonly_fields = ['updated_at']

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in ['primary_color', 'secondary_color', 'accent_color']:
            kwargs['widget'] = forms.TextInput(attrs={'type': 'color'})
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def has_add_permission(self, request):
        if SiteAppearance.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False

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
