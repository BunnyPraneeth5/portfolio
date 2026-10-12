import json
import tempfile
from datetime import date, timedelta
from io import StringIO
from pathlib import Path

from django.core.cache import cache
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase, TransactionTestCase, Client
from django.urls import reverse
from django.utils import timezone

from . import chatbot
from .admin import ExperienceEntryAdminForm, ProjectReplayAdminForm
from .models import (
    About, Skill, Project, BlogPost, ContactMessage,
    Certification, EventEntry, ExperienceEntry, SiteSettings,
    CaseDecision, CaseIncident, ProjectReplay, SuggestedQuestion, ChatQuery, ChatAnswer,
)
from .replays import MAX_STEPS, ReplayValidationError, parse_replay_json, validate_replay

class PortfolioViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Set up mock database records for models that are referenced in templates
        self.about = About.objects.create(
            title="Dr. Cooper",
            subtitle="Pilot & Explorer",
            bio_paragraph_1="We are pioneers.",
            stat_accuracy="99.88",
            stat_accuracy_label="Accuracy",
            stat_agents="4",
            stat_agents_label="Agents",
            stat_teams="2",
            stat_teams_label="Teams",
            stat_projects="10",
            stat_projects_label="Projects"
        )
        
        self.skill = Skill.objects.create(
            name="Astrophysics",
            category="ml",
        )

        self.project = Project.objects.create(
            title="Project Lazarus",
            slug="project-lazarus",
            short_description="Locate a habitable planet.",
            tech_tags="Gravity, Time",
            is_featured=True
        )
        
        self.blog_post = BlogPost.objects.create(
            title="Entering the Wormhole",
            slug="entering-the-wormhole",
            content="It looks like a giant sphere...",
            published=True
        )

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        # Asserts for the main user name in the landing title
        self.assertContains(response, "Karu Praneeth Kumar")

    def test_about_view(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        # Asserts for the timeline headings or bio texts
        self.assertContains(response, "Karu Praneeth Kumar")
        self.assertContains(response, "We are pioneers.")

    def test_skills_view(self):
        response = self.client.get(reverse('skills'))
        self.assertEqual(response.status_code, 200)
        # Asserts on database skills rendering (since skills view renders all Skill items from the DB)
        self.assertContains(response, "Astrophysics")

    def test_projects_view(self):
        Project.objects.create(title="Endurance Docking", slug="endurance-docking", order=1)
        Project.objects.create(title="Hidden Draft", slug="hidden-draft", is_published=False)
        response = self.client.get(reverse('projects'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Project Lazarus")
        self.assertContains(response, "Endurance Docking")
        self.assertNotContains(response, "Hidden Draft")

    def test_blog_view(self):
        response = self.client.get(reverse('blog'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Entering the Wormhole")

    def test_blog_detail_view(self):
        response = self.client.get(reverse('blog_detail', kwargs={'slug': 'entering-the-wormhole'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "It looks like a giant sphere")

    def test_contact_view_get(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)

    def test_contact_view_post(self):
        post_data = {
            'name': 'Brand',
            'email': 'brand@lazarus.org',
            'subject': 'Gravity equations',
            'message': 'We need the data from the event horizon.'
        }
        response = self.client.post(reverse('contact'), data=post_data)
        # Should redirect back to contact
        self.assertEqual(response.status_code, 302)
        
        # Verify the database entry was created
        message = ContactMessage.objects.first()
        self.assertIsNotNone(message)
        self.assertEqual(message.name, 'Brand')
        self.assertEqual(message.email, 'brand@lazarus.org')
        self.assertEqual(message.subject, 'Gravity equations')
        self.assertEqual(message.message, 'We need the data from the event horizon.')


class BaseLayoutTests(TestCase):
    def test_pages_share_base_layout_and_fonts(self):
        Project.objects.create(title="Gargantua Probe", slug="gargantua-probe")
        for url in [reverse('index'), reverse('about'), reverse('skills'), reverse('projects'),
                    reverse('project_detail', args=['gargantua-probe']), reverse('blog'),
                    reverse('contact')]:
            response = self.client.get(url)
            self.assertContains(response, 'id="mobileMenu"', count=1, msg_prefix=url)
            self.assertContains(response, 'IBM+Plex+Sans', msg_prefix=url)
            self.assertNotContains(response, 'Orbitron', msg_prefix=url)
            self.assertNotContains(response, '--accent-blue', msg_prefix=url)

    def test_nav_marks_section_active_on_detail_page(self):
        Project.objects.create(title="Gargantua Probe", slug="gargantua-probe")
        response = self.client.get(reverse('project_detail', args=['gargantua-probe']))
        self.assertContains(response, 'class="nav-link active">Cases</a>')
        self.assertContains(response, 'class="nav-link">About</a>')

    def test_contact_section_and_footer(self):
        for url in [reverse('index'), reverse('about'), reverse('blog')]:
            response = self.client.get(url)
            self.assertContains(response, 'id="contact"', msg_prefix=url)
            self.assertContains(response, 'class="site-footer"', msg_prefix=url)
        response = self.client.get(reverse('contact'))
        self.assertNotContains(response, 'id="contact"')
        self.assertContains(response, 'class="site-footer"')


class HomepageTests(TestCase):
    def setUp(self):
        self.settings_obj = SiteSettings.load()
        Project.objects.create(title="Second Agent", slug="second-agent", order=2, status="live",
                               metric_1_value="84", metric_1_label="Features")
        Project.objects.create(title="First Agent", slug="first-agent", order=1, status="flagship",
                               tech_tags="Python, MCP, PyQt6, Django, Extra")
        Project.objects.create(title="Hidden Agent", slug="hidden-agent", is_published=False)

    def test_roster_lists_published_projects_in_order(self):
        response = self.client.get(reverse('index'))
        titles = [p.title for p in response.context['roster']]
        self.assertLess(titles.index("First Agent"), titles.index("Second Agent"))
        self.assertNotIn("Hidden Agent", titles)
        self.assertContains(response, reverse('project_detail', args=['first-agent']))
        self.assertContains(response, 'roster-status--flagship')
        self.assertContains(response, "Python · MCP · PyQt6 · Django")
        self.assertNotContains(response, "Extra")
        self.assertContains(response, "84")

    def test_best_work_is_flagship(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.context['flagship'].slug, "first-agent")

    def test_quick_view_rows_follow_settings(self):
        self.settings_obj.job_search_mode = 'open'
        self.settings_obj.looking_for = ""
        self.settings_obj.save()
        response = self.client.get(reverse('index'))
        self.assertNotContains(response, "Looking for")
        self.settings_obj.looking_for = "Agentic AI roles"
        self.settings_obj.save()
        response = self.client.get(reverse('index'))
        self.assertContains(response, "Looking for")
        self.assertContains(response, "Agentic AI roles")

    def test_availability_on_homepage_follows_job_search_mode(self):
        self.settings_obj.notice_period = "30 days"
        self.settings_obj.looking_for = "Agentic AI roles"
        self.settings_obj.job_search_mode = 'open'
        self.settings_obj.save()
        response = self.client.get(reverse('index'))
        for text in ["Open to roles", "30 days", "Agentic AI roles", "Open to remote"]:
            self.assertContains(response, text)
        for mode in ('quiet', 'not_looking'):
            self.settings_obj.job_search_mode = mode
            self.settings_obj.save()
            response = self.client.get(reverse('index'))
            for text in ["Open to roles", "30 days", "Agentic AI roles", "Open to remote"]:
                self.assertNotContains(response, text, msg_prefix=mode)

    def test_latest_three_published_logs(self):
        for i in range(4):
            BlogPost.objects.create(title=f"Log {i}", slug=f"log-{i}", content="x", excerpt="x", published=True)
        BlogPost.objects.create(title="Draft log", slug="draft-log", content="x", excerpt="x")
        response = self.client.get(reverse('index'))
        self.assertEqual(len(response.context['latest_posts']), 3)
        self.assertNotContains(response, "Draft log")

    def test_no_splash_and_replay_hidden(self):
        response = self.client.get(reverse('index'))
        self.assertNotContains(response, 'loadingScreen')
        self.assertNotContains(response, 'id="replay"')


class ExperienceEntryModelTests(TestCase):
    def test_date_range_label(self):
        current = ExperienceEntry(
            organization="NASA", role="Pilot",
            start_date=date(2026, 3, 1), is_current=True)
        finished = ExperienceEntry(
            organization="NASA", role="Pilot",
            start_date=date(2025, 6, 1), end_date=date(2025, 8, 31))
        undated = ExperienceEntry(organization="NASA", role="Pilot")
        self.assertEqual(current.date_range_label, "Mar 2026 – Present")
        self.assertEqual(finished.date_range_label, "Jun 2025 – Aug 2025")
        self.assertEqual(undated.date_range_label, "")

    def test_highlights_list_skips_blank_lines(self):
        entry = ExperienceEntry(highlights="First\n\n  Second  \n")
        self.assertEqual(entry.highlights_list, ["First", "Second"])

    def test_newest_first(self):
        old = ExperienceEntry.objects.create(
            organization="Old Co", role="Intern", start_date=date(2024, 1, 1))
        undated = ExperienceEntry.objects.create(organization="No Date", role="Intern")
        new = ExperienceEntry.objects.create(
            organization="New Co", role="Intern", start_date=date(2026, 1, 1))
        current = ExperienceEntry.objects.create(
            organization="Current Co", role="Intern",
            start_date=date(2025, 1, 1), is_current=True)
        self.assertEqual(list(ExperienceEntry.newest_first()), [current, new, old, undated])

    def test_admin_form_requires_start_date(self):
        form = ExperienceEntryAdminForm(data={
            'organization': 'NASA', 'role': 'Pilot',
            'employment_type': 'internship', 'order': 0,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('start_date', form.errors)

    def test_admin_form_rejects_end_date_on_current_role(self):
        form = ExperienceEntryAdminForm(data={
            'organization': 'NASA', 'role': 'Pilot', 'employment_type': 'internship',
            'order': 0, 'start_date': '2026-01-01', 'end_date': '2026-02-01',
            'is_current': True,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('end_date', form.errors)


class CertificationModelTests(TestCase):
    def test_str_and_has_file(self):
        with_issuer = Certification(title="SQL Advanced", issuer="HackerRank")
        without_issuer = Certification(title="CSS")
        self.assertEqual(str(with_issuer), "HackerRank - SQL Advanced")
        self.assertEqual(str(without_issuer), "CSS")
        self.assertFalse(without_issuer.has_file)
        without_issuer.certificate_file_2 = "certificates/css.pdf"
        self.assertTrue(without_issuer.has_file)


class AboutAndHomeExperienceTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(title="Gargantua Probe", slug="gargantua-probe")
        ExperienceEntry.objects.create(
            organization="Lazarus Labs", role="AI Intern", employment_type="internship",
            start_date=date(2026, 3, 1), is_current=True, location="Bengaluru", is_remote=True,
            summary="Built docking tools.", highlights="Shipped thing one\nShipped thing two",
            related_project=self.project)
        Certification.objects.create(
            title="SQL Advanced", issuer="HackerRank", issued_date=date(2025, 5, 1),
            certificate_file="certificates/sql.pdf")

    def test_about_shows_experience_and_certifications(self):
        response = self.client.get(reverse('about'))
        self.assertContains(response, "Professional Experience")
        self.assertContains(response, "Lazarus Labs")
        self.assertContains(response, "Internship")
        self.assertContains(response, "Mar 2026 – Present")
        self.assertContains(response, "Remote")
        self.assertContains(response, "Built docking tools.")
        self.assertContains(response, '<details class="experience-highlights">')
        self.assertContains(response, "Shipped thing two")
        self.assertContains(response, reverse('project_detail', args=['gargantua-probe']))
        self.assertContains(response, "Certifications</h2>")
        self.assertContains(response, "HackerRank · May 2025")
        self.assertContains(response, "View certificate")
        self.assertNotContains(response, "Credential")

    def test_about_hides_link_to_unpublished_project(self):
        self.project.is_published = False
        self.project.save()
        response = self.client.get(reverse('about'))
        self.assertNotContains(response, "See the project")

    def test_about_hides_empty_sections(self):
        ExperienceEntry.objects.all().delete()
        Certification.objects.all().delete()
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Professional Experience")
        self.assertNotContains(response, "Certifications</h2>")

    def test_home_shows_recent_role(self):
        ExperienceEntry.objects.create(
            organization="Older Co", role="Trainee", start_date=date(2024, 1, 1))
        response = self.client.get(reverse('index'))
        self.assertContains(response, "Recent: AI Intern at Lazarus Labs")

    def test_home_hides_recent_line_without_experience(self):
        ExperienceEntry.objects.all().delete()
        response = self.client.get(reverse('index'))
        self.assertNotContains(response, "Recent:")


class ChatbotExperienceTests(TestCase):
    def test_experience_lists_roles_then_events(self):
        ExperienceEntry.objects.create(
            organization="Old Co", role="Trainee", start_date=date(2024, 1, 1))
        ExperienceEntry.objects.create(
            organization="Lazarus Labs", role="AI Intern",
            start_date=date(2026, 3, 1), is_current=True, summary="Built docking tools.")
        EventEntry.objects.create(
            title="Hackathon X", role="Lead", year="2025", location="Bengaluru",
            description="Ran it.")
        reply = chatbot.get_reply("tell me about your experience")['reply']
        self.assertIn("AI Intern @ Lazarus Labs (Internship, Mar 2026 – Present)", reply)
        self.assertIn("Built docking tools.", reply)
        self.assertLess(reply.index("Lazarus Labs"), reply.index("Old Co"))
        self.assertIn("Hackathons and leadership", reply)
        self.assertLess(reply.index("Old Co"), reply.index("Hackathon X"))

    def test_experience_empty(self):
        result = chatbot.get_reply("work experience")
        self.assertIn("hasn't added", result['reply'])
        self.assertIn(reverse('about'), [link['url'] for link in result['links']])
        self.assertNotIn("TechTrotter", result['reply'])

    def test_certifications(self):
        Certification.objects.create(title="SQL Advanced", issuer="HackerRank")
        Certification.objects.create(title="CSS")
        reply = chatbot.get_reply("do you have any certifications?")['reply']
        self.assertIn("• SQL Advanced (HackerRank)", reply)
        self.assertIn("• CSS", reply)

    def test_certifications_empty(self):
        result = chatbot.get_reply("certifications")
        self.assertIn("hasn't listed", result['reply'])
        self.assertIn(reverse('about'), [link['url'] for link in result['links']])
        self.assertNotIn("MCP Certified", result['reply'])

    def test_routing_availability_vs_past_work(self):
        self.assertEqual(chatbot.get_reply("are you open to internships")['intent'], 'internship')
        for question in ["tell me about your internship", "where did you work",
                         "work experience", "where have you worked before"]:
            self.assertEqual(chatbot.get_reply(question)['intent'], 'experience', question)


class CertificationDataMigrationTests(TransactionTestCase):
    migrate_from = [('portfolio', '0015_experience_fields_and_certification')]
    migrate_to = [('portfolio', '0016_move_certificates_to_certification')]

    def setUp(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_from)
        old_apps = executor.loader.project_state(self.migrate_from).apps
        old_apps.get_model('portfolio', 'ExperienceEntry').objects.create(
            year_label="Virtual Internship", organization="Deloitte", role="Data Analytics",
            certificate_file="certificates/data.pdf",
            certificate_file_2="certificates/Deloitte.pdf", order=2)
        old_apps.get_model('portfolio', 'AdditionalCertification').objects.create(
            title="CSS", certificate_file="certificates/css.pdf", order=0)
        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_to)
        self.apps = executor.loader.project_state(self.migrate_to).apps

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())

    def test_everything_moves_to_certification(self):
        CertificationAtStep = self.apps.get_model('portfolio', 'Certification')
        self.assertEqual(self.apps.get_model('portfolio', 'ExperienceEntry').objects.count(), 0)
        self.assertEqual(
            self.apps.get_model('portfolio', 'AdditionalCertification').objects.count(), 0)
        deloitte = CertificationAtStep.objects.get(issuer="Deloitte")
        self.assertEqual(deloitte.title, "Data Analytics")
        self.assertEqual(deloitte.category, "Virtual Internship")
        self.assertEqual(deloitte.certificate_file.name, "certificates/data.pdf")
        self.assertEqual(deloitte.certificate_file_2.name, "certificates/Deloitte.pdf")
        css = CertificationAtStep.objects.get(title="CSS")
        self.assertEqual(css.certificate_file.name, "certificates/css.pdf")
        self.assertGreater(css.order, deloitte.order)


class CaseFileTests(TestCase):
    def setUp(self):
        Project.objects.all().delete()  # drop rows seeded by migration 0008
        self.first =Project.objects.create(title="First Case", slug="first-case", order=1)
        self.case = Project.objects.create(
            title="Middle Case", slug="middle-case", order=2, short_description="One line summary.",
            status="live", case_number=3, metric_1_value="99.88%", metric_1_label="Accuracy",
            metric_3_value="4", metric_3_label="Agents", tech_tags="Python, MCP",
            github_url="https://github.com/example/repo")
        self.last = Project.objects.create(title="Last Case", slug="last-case", order=3)
        Project.objects.create(title="Hidden Case", slug="hidden-case", order=4, is_published=False)

    def get(self, slug='middle-case'):
        return self.client.get(reverse('project_detail', args=[slug]))

    def test_model_helpers(self):
        self.assertEqual(self.case.case_label, "003")
        self.assertEqual(self.first.case_label, "")
        self.assertEqual(self.case.status_stamp, "Case closed · Shipped")
        self.assertEqual(self.first.status_stamp, "")
        self.assertEqual([m['value'] for m in self.case.metrics], ["99.88%", "4"])
        self.case.open_leads = "Lead one\n\n Lead two "
        self.assertEqual(self.case.open_leads_list, ["Lead one", "Lead two"])

    def test_title_block_and_evidence(self):
        response = self.get()
        self.assertContains(response, "Case file no. 003")
        self.assertContains(response, "Cases</a> / 003")
        self.assertContains(response, "Case closed · Shipped")
        self.assertContains(response, "One line summary.")
        self.assertContains(response, "99.88%")
        self.assertContains(response, "View code")
        self.assertContains(response, 'class="case-thumb-fallback"')

    def test_empty_sections_are_hidden(self):
        response = self.get()
        for heading in ['Brief', 'Investigation', 'Decisions', 'Incidents', 'Replay', 'Open leads']:
            self.assertNotContains(response, f'-heading" class="case-section__title">{heading}</h2>')
        self.assertNotContains(response, 'class="case-nav"')

    def test_sections_render_with_content(self):
        self.case.brief = "The brief."
        self.case.architecture_notes = "How it works."
        self.case.open_leads = "Try a bigger model"
        self.case.save()
        CaseDecision.objects.create(project=self.case, code="D-02", decision="Second", order=2)
        CaseDecision.objects.create(project=self.case, code="D-01", decision="Use MCP", tradeoff="More setup", order=1)
        CaseIncident.objects.create(project=self.case, symptom="Hung GUI", root_cause="Race", fix="Queue")
        response = self.get()
        for anchor in ['#brief', '#investigation', '#decisions', '#incidents', '#open-leads']:
            self.assertContains(response, f'href="{anchor}"')
        self.assertNotContains(response, 'href="#replay"')
        self.assertContains(response, "The brief.")
        self.assertContains(response, "More setup")
        self.assertContains(response, "Hung GUI")
        self.assertContains(response, "Try a bigger model")
        content = response.content.decode()
        self.assertLess(content.index("D-01"), content.index("D-02"))

    def test_brief_falls_back_to_long_description(self):
        self.case.long_description = "Older long text."
        self.case.save()
        self.assertContains(self.get(), "Older long text.")
        self.case.brief = "New brief."
        self.case.save()
        response = self.get()
        self.assertContains(response, "New brief.")
        self.assertNotContains(response, "Older long text.")

    def test_previous_and_next_case(self):
        response = self.get()
        self.assertEqual(response.context['previous_case'].slug, "first-case")
        self.assertEqual(response.context['next_case'].slug, "last-case")
        self.assertIsNone(self.get('first-case').context['previous_case'])
        # Unpublished projects are skipped.
        self.assertIsNone(self.get('last-case').context['next_case'])

    def test_unpublished_case_is_404(self):
        self.assertEqual(self.get('hidden-case').status_code, 404)

    def test_projects_list_uses_thumbnail_fallback(self):
        response = self.client.get(reverse('projects'))
        self.assertContains(response, 'class="case-thumb-fallback"')
        self.assertNotContains(response, 'project-thumbnail--')

    def test_admin_has_case_inlines(self):
        from django.contrib import admin as django_admin
        inline_models = [inline.model for inline in django_admin.site._registry[Project].inlines]
        self.assertEqual(inline_models, [CaseDecision, CaseIncident])


def replay_doc(**overrides):
    doc = {
        'title': 'Example run',
        'duration_s': 10,
        'steps': [
            {'t': 0, 'actor': 'orchestrator', 'kind': 'info', 'text': 'received alert'},
            {'t': 3, 'actor': 'recon', 'kind': 'tool_call', 'text': 'lookup_ip 203.0.113.7'},
            {'t': 7, 'actor': 'recon', 'kind': 'result', 'text': 'finding summary'},
        ],
    }
    doc.update(overrides)
    return doc


class ReplayValidatorTests(TestCase):
    def assertRejected(self, doc, fragment):
        with self.assertRaises(ReplayValidationError) as ctx:
            validate_replay(doc)
        self.assertTrue(any(fragment in m for m in ctx.exception.messages), ctx.exception.messages)

    def test_valid_document_is_normalized(self):
        doc = replay_doc(duration_s=9.2)
        doc['steps'][0]['extra'] = 'dropped'
        result = validate_replay(doc)
        self.assertEqual(result['duration_s'], 10)
        self.assertEqual(len(result['steps']), 3)
        self.assertNotIn('extra', result['steps'][0])

    def test_rejects_unknown_kind(self):
        doc = replay_doc()
        doc['steps'][1]['kind'] = 'warning'
        self.assertRejected(doc, "Step 2: unknown kind 'warning'")

    def test_rejects_too_many_steps(self):
        steps = [{'t': 0, 'actor': 'a', 'kind': 'info', 'text': 'x'}] * (MAX_STEPS + 1)
        self.assertRejected(replay_doc(steps=steps), 'Too many steps')

    def test_rejects_out_of_order_and_late_steps(self):
        doc = replay_doc()
        doc['steps'][2]['t'] = 1
        self.assertRejected(doc, 'time order')
        doc = replay_doc()
        doc['steps'][2]['t'] = 99
        self.assertRejected(doc, 'after "duration_s"')

    def test_rejects_long_text_and_missing_fields(self):
        doc = replay_doc()
        doc['steps'][0]['text'] = 'x' * 501
        self.assertRejected(doc, 'shorten it')
        self.assertRejected(replay_doc(title=''), '"title"')
        self.assertRejected(replay_doc(steps=[]), '"steps"')
        self.assertRejected([], 'Top level')

    def test_rejects_invalid_json(self):
        with self.assertRaises(ReplayValidationError) as ctx:
            parse_replay_json(b'{"title": ')
        self.assertIn('Not valid JSON', ctx.exception.messages[0])

    def test_blocks_obvious_leaks(self):
        for text, fragment in [
            ('mailed alice@example.com', 'email'),
            ('key sk-abcdefghijklmnopqrstu', 'API key'),
            ('api_key=12345', 'secret'),
            ('lookup 8.8.8.8', 'public IP'),
            ('hash ' + 'a' * 40, 'hex'),
        ]:
            doc = replay_doc()
            doc['steps'][0]['text'] = text
            self.assertRejected(doc, fragment)

    def test_allows_private_and_documentation_ips(self):
        doc = replay_doc()
        doc['steps'][0]['text'] = 'from 10.0.0.4 to 192.168.1.20 via 198.51.100.23'
        validate_replay(doc)


class ProjectReplayModelTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(title="Gargantua Probe", slug="gargantua-probe")

    def make(self, **kwargs):
        data = replay_doc()
        defaults = {'project': self.project, 'title': data['title'], 'duration_s': 10, 'steps': data['steps']}
        defaults.update(kwargs)
        return ProjectReplay.objects.create(**defaults)

    def test_only_one_featured_on_home(self):
        first = self.make(is_featured_on_home=True)
        second = self.make(is_featured_on_home=True)
        first.refresh_from_db()
        self.assertFalse(first.is_featured_on_home)
        self.assertTrue(second.is_featured_on_home)

    def test_clean_rejects_bad_steps(self):
        from django.core.exceptions import ValidationError
        replay = ProjectReplay(project=self.project, title='x', duration_s=5,
                               steps=[{'t': 0, 'actor': 'a', 'kind': 'nope', 'text': 'x'}])
        with self.assertRaises(ValidationError) as ctx:
            replay.full_clean()
        self.assertIn('steps', ctx.exception.message_dict)

    def test_admin_upload_fills_fields(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        upload = SimpleUploadedFile('run.json', json.dumps(replay_doc()).encode(), content_type='application/json')
        form = ProjectReplayAdminForm(
            data={'project': self.project.pk, 'title': '', 'duration_s': '', 'steps': '[]', 'order': 0},
            files={'replay_file': upload})
        self.assertTrue(form.is_valid(), form.errors)
        replay = form.save()
        self.assertEqual(replay.title, 'Example run')
        self.assertEqual(replay.duration_s, 10)
        self.assertEqual(replay.step_count, 3)
        self.assertFalse(replay.is_published)

    def test_admin_upload_rejects_bad_file(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        doc = replay_doc()
        doc['steps'][0]['kind'] = 'bogus'
        upload = SimpleUploadedFile('run.json', json.dumps(doc).encode(), content_type='application/json')
        form = ProjectReplayAdminForm(
            data={'project': self.project.pk, 'title': '', 'duration_s': '', 'steps': '[]', 'order': 0},
            files={'replay_file': upload})
        self.assertFalse(form.is_valid())
        self.assertIn('unknown kind', str(form.errors['replay_file']))


class ImportReplayCommandTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(title="Gargantua Probe", slug="gargantua-probe")
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write(self, content):
        path = Path(self.tmp.name) / 'run.json'
        path.write_text(content if isinstance(content, str) else json.dumps(content), encoding='utf-8')
        return str(path)

    def test_imports_valid_file_unpublished(self):
        out = StringIO()
        call_command('import_replay', 'gargantua-probe', self.write(replay_doc()), stdout=out)
        replay = ProjectReplay.objects.get()
        self.assertEqual(replay.project, self.project)
        self.assertFalse(replay.is_published)
        self.assertIn('3 steps', out.getvalue())

    def test_publish_and_feature_flags(self):
        call_command('import_replay', 'gargantua-probe', self.write(replay_doc()),
                     '--publish', '--feature-on-home', '--title', 'Custom', stdout=StringIO())
        replay = ProjectReplay.objects.get()
        self.assertTrue(replay.is_published)
        self.assertTrue(replay.is_featured_on_home)
        self.assertEqual(replay.title, 'Custom')

    def test_rejects_malformed_files_with_clear_errors(self):
        doc = replay_doc()
        doc['steps'][1]['kind'] = 'warning'
        with self.assertRaises(CommandError) as ctx:
            call_command('import_replay', 'gargantua-probe', self.write(doc), stdout=StringIO())
        self.assertIn("Step 2: unknown kind 'warning'", str(ctx.exception))
        with self.assertRaises(CommandError) as ctx:
            call_command('import_replay', 'gargantua-probe', self.write('{not json'), stdout=StringIO())
        self.assertIn('Not valid JSON', str(ctx.exception))
        self.assertEqual(ProjectReplay.objects.count(), 0)

    def test_unknown_project_and_missing_file(self):
        with self.assertRaises(CommandError):
            call_command('import_replay', 'nope', self.write(replay_doc()), stdout=StringIO())
        with self.assertRaises(CommandError):
            call_command('import_replay', 'gargantua-probe', str(Path(self.tmp.name) / 'missing.json'), stdout=StringIO())


class ReplayPageTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(title="Gargantua Probe", slug="gargantua-probe")
        self.other = Project.objects.create(title="Endurance Docking", slug="endurance-docking")

    def make(self, project, **kwargs):
        data = replay_doc()
        defaults = {'title': data['title'], 'duration_s': 10, 'steps': data['steps'], 'is_published': True}
        defaults.update(kwargs)
        return ProjectReplay.objects.create(project=project, **defaults)

    def test_hidden_without_published_replays(self):
        self.make(self.project, is_published=False)
        response = self.client.get(reverse('index'))
        self.assertNotContains(response, 'id="replay"')
        self.assertNotContains(response, 'replay.js')
        self.assertNotContains(response, '#replay" class="nav-link"')

    def test_homepage_player_featured_first_with_switcher(self):
        plain = self.make(self.project, title='Plain run', order=0)
        featured = self.make(self.other, title='Featured run', order=5, is_featured_on_home=True)
        response = self.client.get(reverse('index'))
        self.assertEqual([r.pk for r in response.context['replays']], [featured.pk, plain.pk])
        self.assertContains(response, 'id="replay"')
        self.assertContains(response, 'data-replay-title>Featured run<')
        self.assertContains(response, f'id="replay-data-{plain.pk}"')
        self.assertContains(response, 'role="tablist"')
        self.assertContains(response, 'replay.js')
        self.assertContains(response, '#replay" class="nav-link"')

    def test_project_page_replay_section(self):
        self.make(self.project)
        response = self.client.get(reverse('project_detail', args=['gargantua-probe']))
        self.assertContains(response, 'href="#replay"')
        self.assertContains(response, 'data-replay-player')
        self.assertContains(response, 'finding summary')
        other = self.client.get(reverse('project_detail', args=['endurance-docking']))
        self.assertNotContains(other, 'data-replay-player')

    def test_step_text_is_escaped(self):
        replay = self.make(self.project)
        replay.steps = [{'t': 0, 'actor': 'a', 'kind': 'info', 'text': '<img src=x onerror=alert(1)>'}]
        replay.save()
        response = self.client.get(reverse('project_detail', args=['gargantua-probe']))
        self.assertNotContains(response, '<img src=x')
        self.assertContains(response, '&lt;img src=x')
        self.assertContains(response, '\\u003Cimg src=x')


class ChatHelperReplyTests(TestCase):
    def test_story_replies_wait_for_review(self):
        for question, story_text in [
            ("what's the hardest bug you fixed", "async state synchronization"),
            ("tell me about a conflict in your team", "15-minute benchmarks"),
            ("what is your favorite library", "PyTorch and Django"),
        ]:
            result = chatbot.get_reply(question)
            self.assertTrue(ChatAnswer.objects.get(intent=result['intent']).needs_review, question)
            self.assertTrue(result['fallback'])
            self.assertIn("no approved answer", result['reply'])
            self.assertNotIn(story_text, result['reply'])
            self.assertTrue(result['chips'])

    def test_is_ai_is_honest(self):
        for question in ["are you an ai?", "is this a bot", "are you human", "who is answering"]:
            result = chatbot.get_reply(question)
            self.assertEqual(result['intent'], 'is_ai', question)
            self.assertIn("scripted helper", result['reply'])
            self.assertNotIn("AI portfolio assistant", result['reply'])

    def test_replies_are_third_person(self):
        questions = ["hi", "tell me about yourself", "why should we hire you", "notice period",
                     "are you remote", "are you available", "internship", "education", "resume",
                     "contact", "skills", "python", "projects", "tell me about soc copilot"]
        for question in questions:
            reply = chatbot.get_reply(question)['reply']
            self.assertNotIn("I'm Karu", reply, question)
            self.assertNotRegex(reply, r"\b(my|My) (projects|skills|resume|notice|education)\b", question)

    def test_no_hardcoded_fallback_content(self):
        Project.objects.all().delete()
        Skill.objects.all().delete()
        self.assertIn("No projects are published", chatbot.get_reply("projects")['reply'])
        self.assertIn("aren't listed", chatbot.get_reply("skills")['reply'])
        self.assertIn("hasn't listed Python", chatbot.get_reply("python")['reply'])
        self.assertIn("isn't published", chatbot.get_reply("tell me about soc copilot")['reply'])

    def test_project_reply_links_case_file_and_replay(self):
        project = Project.objects.get(slug='soc-copilot')
        url = reverse('project_detail', args=['soc-copilot'])
        labels = {link['label']: link['url'] for link in chatbot.get_reply("tell me about soc copilot")['links']}
        self.assertEqual(labels.get('SOC Copilot case file'), url)
        self.assertNotIn('Play the replay', labels)
        ProjectReplay.objects.create(project=project, title='Run', duration_s=5, is_published=True,
                                     steps=[{'t': 0, 'actor': 'a', 'kind': 'info', 'text': 'x'}])
        labels = {link['label']: link['url'] for link in chatbot.get_reply("tell me about soc copilot")['links']}
        self.assertEqual(labels.get('Play the replay'), url + '#replay')

    def test_chips_come_from_active_suggested_questions(self):
        settings_obj = SiteSettings.load()
        settings_obj.job_search_mode = 'open'
        settings_obj.save()
        SuggestedQuestion.objects.update(is_active=True)
        first = SuggestedQuestion.objects.first()
        first.is_active = False
        first.save()
        chips = chatbot.get_reply("hi")['chips']
        self.assertNotIn(first.text, chips)
        self.assertEqual(len(chips), SuggestedQuestion.objects.filter(is_active=True).count())

    def test_seeded_chips_all_get_real_answers(self):
        texts = list(SuggestedQuestion.objects.values_list('text', flat=True))
        self.assertIn('How does SOC Copilot work?', texts)
        for text in texts:
            result = chatbot.get_reply(text)
            self.assertFalse(result['fallback'], text)
            self.assertFalse(ChatAnswer.objects.get(intent=result['intent']).needs_review, text)


class ChatApiTests(TestCase):
    def setUp(self):
        cache.clear()

    def post(self, message, ip='203.0.113.5'):
        return self.client.post(reverse('chat_reply'), data=json.dumps({'message': message}),
                                content_type='application/json', HTTP_X_REAL_IP=ip)

    def test_response_shape(self):
        data = self.post("hi").json()
        self.assertEqual(set(data), {'reply', 'links', 'chips'})
        self.assertTrue(data['chips'])

    def test_logs_scrubbed_question_without_ip(self):
        question = "email me at bob@example.com or +91 98765 43210 about python"
        self.post(question)
        query = ChatQuery.objects.get()
        self.assertNotIn("bob@example.com", query.question)
        self.assertNotIn("98765", query.question)
        self.assertIn("[email]", query.question)
        self.assertEqual(query.matched_intent, chatbot.get_reply(question)['intent'])
        self.assertFalse(query.was_fallback)
        self.assertNotIn('ip', [f.name for f in ChatQuery._meta.get_fields()])

    def test_logs_fallbacks_and_skips_empty(self):
        self.post("zzqx blorp")
        self.post("   ")
        self.assertEqual(ChatQuery.objects.count(), 1)
        self.assertTrue(ChatQuery.objects.get().was_fallback)

    def test_old_queries_are_purged(self):
        old = ChatQuery.objects.create(question="old")
        ChatQuery.objects.filter(pk=old.pk).update(created_at=timezone.now() - timedelta(days=91))
        self.post("python")
        self.assertFalse(ChatQuery.objects.filter(pk=old.pk).exists())

    def test_rate_limit_per_visitor(self):
        for _ in range(20):
            self.assertEqual(self.post("hi").status_code, 200)
        limited = self.post("hi")
        self.assertEqual(limited.status_code, 429)
        self.assertIn("wait a minute", limited.json()['reply'])
        self.assertEqual(self.post("hi", ip='198.51.100.9').status_code, 200)

    def test_requires_csrf(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(reverse('chat_reply'), data=json.dumps({'message': 'hi'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 403)


class ChatWidgetTemplateTests(TestCase):
    def test_widget_markup(self):
        response = self.client.get(reverse('about'))
        self.assertContains(response, 'role="dialog"')
        self.assertContains(response, 'aria-controls="pet-chat-panel"')
        self.assertContains(response, 'Scripted helper · not AI')
        self.assertContains(response, 'id="pet-chat-chips"')
        self.assertContains(response, 'chat_widget.js')
        self.assertNotContains(response, 'AI Portfolio Companion')
        self.assertNotContains(response, "I'm Karu Praneeth Kumar (Bunny). Ask me")


class LogsTests(TestCase):
    def setUp(self):
        BlogPost.objects.all().delete()
        self.old = BlogPost.objects.create(title="Old note", slug="old-note", content="x", excerpt="Old excerpt",
                                           published=True, event_date=date(2024, 1, 5))
        self.decision = BlogPost.objects.create(title="Why MCP", slug="why-mcp", content="Body text", excerpt="A choice",
                                                published=True, log_type='decision', event_date=date(2026, 2, 1))
        self.incident = BlogPost.objects.create(title="Queue stall", slug="queue-stall", content="x", excerpt="x",
                                                published=True, log_type='incident', event_date=date(2025, 6, 1))
        BlogPost.objects.create(title="Draft decision", slug="draft-decision", content="x", excerpt="x",
                                log_type='decision')

    def test_default_type_is_note(self):
        self.assertEqual(self.old.log_type, 'note')
        response = self.client.get(reverse('blog'))
        self.assertContains(response, 'log-type--note">Note</span> · 05 Jan 2024')

    def test_ordered_by_event_date(self):
        titles = [p.title for p in self.client.get(reverse('blog')).context['posts']]
        self.assertEqual(titles, ["Why MCP", "Queue stall", "Old note"])

    def test_filter_by_type(self):
        response = self.client.get(reverse('blog') + '?type=decision')
        self.assertEqual([p.title for p in response.context['posts']], ["Why MCP"])
        self.assertContains(response, 'aria-current="page">Decision')
        self.assertNotContains(response, "Draft decision")

    def test_filters_only_list_types_with_posts_and_ignore_bad_values(self):
        response = self.client.get(reverse('blog') + '?type=bogus')
        self.assertEqual(response.context['active_type'], '')
        self.assertEqual(len(response.context['posts']), 3)
        self.assertEqual([f['value'] for f in response.context['filters']], ['decision', 'incident', 'note'])
        self.assertEqual(response.context['total_count'], 3)

    def test_empty_states_and_no_placeholders(self):
        response = self.client.get(reverse('blog') + '?type=build_log')
        self.assertContains(response, "Nothing filed under Build log yet.")
        BlogPost.objects.all().delete()
        response = self.client.get(reverse('blog'))
        self.assertContains(response, "No logs published yet.")
        for invented in ["Coming Soon", "Designing Agentic SOC Workflows", "What Accuracy Hides",
                         "Building Calm Engineering Tools"]:
            self.assertNotContains(response, invented)

    def test_detail_uses_case_file_layout(self):
        response = self.client.get(reverse('blog_detail', args=['why-mcp']))
        self.assertContains(response, 'Logs</a> / <a href="/blog/?type=decision">Decision</a>')
        self.assertContains(response, '<h1 class="case-title">Why MCP</h1>')
        self.assertContains(response, "Body text")

    def test_homepage_shows_log_type(self):
        response = self.client.get(reverse('index'))
        self.assertEqual([p.title for p in response.context['latest_posts']], ["Why MCP", "Queue stall", "Old note"])
        self.assertContains(response, 'log-type--decision">Decision</span>')

    def test_blog_url_unchanged_and_nav_says_logs(self):
        self.assertEqual(reverse('blog'), '/blog/')
        response = self.client.get(reverse('blog'))
        self.assertContains(response, 'class="nav-link active">Logs</a>')


class ChatEvalTests(TestCase):
    """Every recruiter phrasing in portfolio/chat_eval.py must reach its expected topic."""

    def setUp(self):
        chatbot.clear_cache()

    def test_all_eval_phrasings(self):
        from .chat_eval import QUESTIONS
        misses = []
        for topic, expected, kind, phrasings in QUESTIONS:
            accepted = expected if isinstance(expected, tuple) else (expected,)
            for text in phrasings:
                result = chatbot.get_reply(text)
                ok = result['fallback'] if kind == 'guard' else result['intent'] in accepted
                if not ok:
                    misses.append(f"{text!r}: expected {accepted}, got {result['intent']}")
        self.assertEqual(misses, [], "\n".join(misses))

    def test_eval_covers_enough(self):
        from .chat_eval import QUESTIONS
        self.assertGreaterEqual(len(QUESTIONS), 74)
        self.assertGreaterEqual(sum(len(q[3]) for q in QUESTIONS), 250)


class JobSearchModeTests(TestCase):
    def setUp(self):
        chatbot.clear_cache()
        self.settings_obj = SiteSettings.load()

    def set_mode(self, mode):
        self.settings_obj.job_search_mode = mode
        self.settings_obj.save()

    def test_default_mode_is_quiet(self):
        self.assertEqual(SiteSettings._meta.get_field('job_search_mode').default, 'quiet')

    def test_quiet_mode_gives_neutral_reply(self):
        self.set_mode('quiet')
        for question in ["is he open to new roles", "notice period?", "wfh possible?", "open to internships?"]:
            result = chatbot.get_reply(question)
            self.assertIn("contact Bunny directly", result['reply'], question)
            self.assertNotIn("open to new roles", result['reply'].lower(), question)
            self.assertNotIn(self.settings_obj.notice_period or 'zz', result['reply'], question)

    def test_not_looking_mode(self):
        self.set_mode('not_looking')
        self.assertIn("isn't looking for new roles", chatbot.get_reply("is he available")['reply'])

    def test_open_mode_answers_from_data(self):
        self.settings_obj.notice_period = "30 days"
        self.set_mode('open')
        self.assertIn("Bunny is open to new roles", chatbot.get_reply("is he available")['reply'])
        self.assertIn("30 days", chatbot.get_reply("notice period?")['reply'])

    def test_mode_replies_are_editable(self):
        self.settings_obj.quiet_reply = "Reach out to {name} at {contact_email}."
        self.set_mode('quiet')
        reply = chatbot.get_reply("is he available")['reply']
        self.assertEqual(reply, f"Reach out to {self.settings_obj.hero_name_display} at {self.settings_obj.contact_email}.")

    def test_availability_chips_hidden_unless_open(self):
        self.set_mode('quiet')
        self.assertNotIn('Is Bunny open to roles?', chatbot.get_reply("hi")['chips'])
        self.set_mode('open')
        self.assertIn('Is Bunny open to roles?', chatbot.get_reply("hi")['chips'])

    def test_why_hire_mentions_open_to_roles_only_in_open_mode(self):
        self.set_mode('quiet')
        self.assertNotIn("Open to roles", chatbot.get_reply("why should we hire him")['reply'])
        self.set_mode('open')
        self.assertIn("Open to roles", chatbot.get_reply("why should we hire him")['reply'])

    def test_neutral_topics_never_give_specifics(self):
        self.set_mode('open')
        for question in ["expected ctc?", "does he need visa sponsorship", "any competing offers?",
                         "is he planning to leave his company?"]:
            result = chatbot.get_reply(question)
            self.assertIn(self.settings_obj.contact_email, result['reply'], question)
            self.assertIn('/contact/', [link['url'] for link in result['links']], question)

    def test_availability_timestamp(self):
        self.set_mode('open')
        first = SiteSettings.load().availability_updated_at
        self.assertIsNotNone(first)
        settings_obj = SiteSettings.load()
        settings_obj.contact_tagline = "Unrelated change"
        settings_obj.save()
        self.assertEqual(SiteSettings.load().availability_updated_at, first)
        settings_obj.notice_period = "60 days"
        settings_obj.save()
        self.assertGreater(SiteSettings.load().availability_updated_at, first)


class ChatAnswerAdminEditTests(TestCase):
    def setUp(self):
        chatbot.clear_cache()

    def test_text_edit_takes_effect_immediately(self):
        chatbot.get_reply("what is this website built with")  # warm the cache
        answer = ChatAnswer.objects.get(intent='site_tech')
        answer.answer = "Built by {name} with Django."
        answer.save()
        reply = chatbot.get_reply("what is this website built with")['reply']
        self.assertEqual(reply, f"Built by {SiteSettings.load().hero_name_display} with Django.")

    def test_text_overrides_live_data_and_link_is_added(self):
        answer = ChatAnswer.objects.get(intent='resume')
        answer.answer = "Ask for the latest resume."
        answer.link_label, answer.link_url = 'Contact', '/contact/'
        answer.save()
        result = chatbot.get_reply("send me the cv")
        self.assertEqual(result['reply'], "Ask for the latest resume.")
        self.assertEqual(result['links'], [{'label': 'Contact', 'url': '/contact/'}])

    def test_new_keyword_and_synonym(self):
        self.assertTrue(chatbot.get_reply("zorbleflux")['fallback'])
        answer = ChatAnswer.objects.get(intent='resume')
        answer.synonyms += "\nzorbleflux = resume"
        answer.save()
        self.assertEqual(chatbot.get_reply("zorbleflux")['intent'], 'resume')

    def test_inactive_topic_is_ignored(self):
        ChatAnswer.objects.filter(intent='site_tech').update(is_active=False)
        chatbot.clear_cache()
        self.assertNotEqual(chatbot.get_reply("how was this site made")['intent'], 'site_tech')

    def test_story_served_only_after_review(self):
        question = "what is the hardest bug he fixed"
        result = chatbot.get_reply(question)
        self.assertEqual(result['intent'], 'hardest_bug')
        self.assertIn("no approved answer", result['reply'])
        answer = ChatAnswer.objects.get(intent='hardest_bug')
        answer.answer = "Approved answer text."
        answer.needs_review = False
        answer.save()
        self.assertEqual(chatbot.get_reply(question)['reply'], "Approved answer text.")

    def test_new_story_topic_without_text_stays_pending(self):
        ChatAnswer.objects.filter(intent='weakness').update(needs_review=False)
        chatbot.clear_cache()
        self.assertIn("no approved answer", chatbot.get_reply("what is his biggest weakness")['reply'])

    def test_placeholders(self):
        self.assertEqual(chatbot.fill_placeholders("{unknown} {contact_email}"),
                         "{unknown} " + SiteSettings.load().contact_email)

    def test_validation(self):
        from django.core.exceptions import ValidationError
        answer = ChatAnswer(intent='x', topic='X', link_label='Bad', link_url='javascript:alert(1)')
        with self.assertRaises(ValidationError):
            answer.full_clean()
        answer = ChatAnswer(intent='x', topic='X', synonyms='no equals sign')
        with self.assertRaises(ValidationError):
            answer.full_clean()

    def test_his_is_not_a_greeting(self):
        for question in ["whats his cgpa", "is bunny his real name"]:
            self.assertNotEqual(chatbot.get_reply(question)['intent'], 'greeting', question)


class ChatAdminViewTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        self.admin = get_user_model().objects.create_superuser('boss', 'boss@example.com', 'unused-test-pass')
        self.client.force_login(self.admin)

    def test_try_question_page(self):
        response = self.client.get(reverse('admin:portfolio_chatanswer_try') + '?question=NP%3F')
        self.assertContains(response, 'notice period')
        self.assertContains(response, 'Notice period / start date')

    def test_changelist_has_try_button_and_source_column(self):
        response = self.client.get(reverse('admin:portfolio_chatanswer_changelist'))
        self.assertContains(response, 'Try a question')
        self.assertContains(response, 'Live site data')

    def test_create_answer_from_logged_questions(self):
        q = ChatQuery.objects.create(question="Do you do night shifts in winter?", was_fallback=True)
        response = self.client.post(reverse('admin:portfolio_chatquery_changelist'), {
            'action': 'create_answer_from_questions', '_selected_action': [q.pk]})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('admin:portfolio_chatanswer_add'), response['Location'])
        self.assertIn('night+shifts', response['Location'])
