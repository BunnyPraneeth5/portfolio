from django.contrib import admin
from django import forms
from .models import (
    About, Skill, Project, BlogPost, ContactMessage, SiteAppearance,
    WhatIDo, EducationEntry, ExperienceEntry, EventEntry,
    AdditionalCertification,
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
    list_display = ['title', 'featured', 'created_at']
    list_filter = ['featured', 'created_at']
    list_editable = ['featured']

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'published', 'created_at']
    list_filter = ['published', 'created_at']
    list_editable = ['published']
    prepopulated_fields = {'slug': ('title',)}

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
