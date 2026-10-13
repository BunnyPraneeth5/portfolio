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
    Certification, EducationEntry, EventEntry, ExperienceEntry, SiteSettings,
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
        Project.objects.create(title="Gargantua Probe", slug="gargantua-probe")
        BlogPost.objects.create(title="A log", slug="a-log", content="x", excerpt="x", published=True)
        with_section = [reverse('index'), reverse('project_detail', args=['gargantua-probe']),
                        reverse('blog_detail', args=['a-log'])]
        without_section = [reverse('about'), reverse('skills'), reverse('projects'), reverse('blog'),
                           reverse('contact')]
        for url in with_section:
            self.assertContains(self.client.get(url), 'id="contact"', msg_prefix=url)
        for url in without_section:
            self.assertNotContains(self.client.get(url), 'id="contact"', msg_prefix=url)
        for url in with_section + without_section:
            self.assertContains(self.client.get(url), 'class="site-footer"', msg_prefix=url)


class HomepageTests(TestCase):
    def setUp(self):
        self.settings_obj = SiteSettings.load()
        Project.objects.create(title="Second Agent", slug="second-agent", order=2, status="live",
                               metric_1_value="84", metric_1_label="Features")
        Project.objects.create(title="First Agent", slug="first-agent", order=1, status="flagship",
                               tech_tags="Python, MCP, PyQt6, Django, Extra")
        Project.objects.create(title="Hidden Agent", slug="hidden-agent", is_published=False)

    def test_roster_lists_published_projects_in_order(self):
        Project.objects.filter(slug__in=['first-agent', 'second-agent', 'hidden-agent']).update(is_featured=True)
        response = self.client.get(reverse('index'))
        titles = [p.title for p in response.context['roster']]
        self.assertLess(titles.index("First Agent"), titles.index("Second Agent"))
        self.assertNotIn("Hidden Agent", titles)
        self.assertContains(response, reverse('project_detail', args=['first-agent']))
        self.assertContains(response, 'roster-status--flagship')
        self.assertContains(response, "Python · MCP · PyQt6 · Django")
        self.assertNotContains(response, "Extra")
        self.assertNotContains(response, "Key metric")
        self.assertNotContains(response, "roster__metric")

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
        self.assertContains(response, 'id="work-heading">Work</h2>')
        self.assertContains(response, "Lazarus Labs")
        self.assertContains(response, "Internship")
        self.assertContains(response, "Mar 2026 – Present")
        self.assertContains(response, "Remote")
        self.assertContains(response, "Built docking tools.")
        self.assertContains(response, "Highlights")
        self.assertContains(response, "Shipped thing two")
        self.assertContains(response, "since Mar 2026")
        self.assertContains(response, reverse('project_detail', args=['gargantua-probe']))
        self.assertContains(response, "Courses and certificates</h2>")
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
        self.assertNotContains(response, 'id="work-heading"')
        self.assertNotContains(response, "Courses and certificates</h2>")

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
        Project.objects.filter(is_published=True).update(is_featured=True, thumbnail='')
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
        self.assertNotContains(response, '#replay" class="nav-link"')

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
        self.assertContains(response, 'log-type--note">Note</span>')
        self.assertContains(response, 'datetime="2024-01-05">05 Jan</time>')
        self.assertContains(response, '<h2 id="log-year-2024" class="log-year__label">2024</h2>', html=True)

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


class Phase7Tests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(title="Gargantua Probe", slug="gargantua-probe",
                                              short_description="Probe summary for sharing.")
        self.post = BlogPost.objects.create(title="A log", slug="a-log", content="x", excerpt="Log excerpt.",
                                            published=True)
        self.urls = [reverse('index'), reverse('about'), reverse('skills'), reverse('projects'),
                     reverse('project_detail', args=['gargantua-probe']), reverse('blog'),
                     reverse('blog_detail', args=['a-log']), reverse('contact')]

    def test_no_third_party_css_or_js_libraries(self):
        for url in self.urls:
            html = self.client.get(url).content.decode()
            for library in ['tailwindcss', 'font-awesome', 'unpkg.com/aos', 'cdn.jsdelivr']:
                self.assertNotIn(library, html, f'{url}: {library}')

    def test_every_page_has_description_and_open_graph(self):
        for url in self.urls:
            response = self.client.get(url)
            self.assertContains(response, '<meta name="description" content="', msg_prefix=url)
            self.assertNotContains(response, '<meta name="description" content="">', msg_prefix=url)
            for prop in ['og:title', 'og:description', 'og:url', 'og:image']:
                self.assertContains(response, f'property="{prop}"', msg_prefix=url)

    def test_case_file_and_log_share_their_own_details(self):
        response = self.client.get(reverse('project_detail', args=['gargantua-probe']))
        self.assertContains(response, '<meta property="og:title" content="Gargantua Probe">')
        self.assertContains(response, 'content="Probe summary for sharing."')
        self.assertContains(response, '<meta property="og:type" content="article">')
        response = self.client.get(reverse('blog_detail', args=['a-log']))
        self.assertContains(response, '<meta property="og:title" content="A log">')

    def test_site_settings_loaded_once_per_request(self):
        SiteSettings.load()  # the row exists in real use; creating it is a one-time cost
        from django.db import connection
        from django.test.utils import CaptureQueriesContext
        for url in self.urls:
            with CaptureQueriesContext(connection) as ctx:
                self.client.get(url)
            count = sum('portfolio_sitesettings' in q['sql'] for q in ctx.captured_queries)
            self.assertEqual(count, 1, url)

    def test_restyled_pages_drop_hardcoded_badges(self):
        EventEntry.objects.create(title="Hackathon X", role="Lead", year="2025", location="Bengaluru",
                                  description="Ran it.")
        response = self.client.get(reverse('about'))
        self.assertContains(response, "Hackathon X")
        self.assertNotContains(response, "College Level")
        self.assertNotContains(response, ">Organizer<")
        self.assertNotContains(response, "data-count-to")

    def test_skills_marks_core_stack(self):
        Skill.objects.create(name="Zeta Lang", category="languages", is_featured=True)
        response = self.client.get(reverse('skills'))
        self.assertContains(response, 'Zeta Lang <span class="tag tag--core">Core</span>')


class Phase8FieldsTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        self.admin = get_user_model().objects.create_superuser('boss8', 'boss8@example.com', 'unused-test-pass')
        self.client.force_login(self.admin)
        self.project = Project.objects.create(title="Probe", slug="probe")

    def test_new_fields_start_empty(self):
        self.assertEqual((self.project.role, self.project.year, self.project.project_type,
                          self.project.one_liner, self.project.personal_note), ('', '', '', '', ''))
        self.assertEqual(SiteSettings.load().currently, '')
        about = About.objects.create(title="About", description="x")
        self.assertEqual((about.off_duty, about.pull_quote), ('', ''))
        self.assertFalse(Certification.objects.create(title="Cert").is_featured)
        self.assertIsNone(BlogPost.objects.create(title="L", slug="l", content="c", excerpt="e").related_project)

    def test_updated_at_is_set_on_save(self):
        self.assertIsNotNone(self.project.updated_at)
        settings = SiteSettings.load()
        settings.save()
        self.assertIsNotNone(settings.updated_at)

    def test_log_keeps_existing_when_project_deleted(self):
        post = BlogPost.objects.create(title="L", slug="l", content="c", excerpt="e", related_project=self.project)
        self.assertEqual(list(self.project.logs.all()), [post])
        self.project.delete()
        post.refresh_from_db()
        self.assertIsNone(post.related_project)

    def test_admin_forms_show_new_fields(self):
        about = About.objects.create(title="About", description="x")
        cert = Certification.objects.create(title="Cert")
        post = BlogPost.objects.create(title="L", slug="l", content="c", excerpt="e")
        SiteSettings.load()
        checks = [
            (reverse('admin:portfolio_project_change', args=[self.project.pk]),
             ['name="role"', 'name="year"', 'name="project_type"', 'name="one_liner"', 'name="personal_note"']),
            (reverse('admin:portfolio_sitesettings_change', args=[1]), ['name="currently"']),
            (reverse('admin:portfolio_about_change', args=[about.pk]), ['name="off_duty"', 'name="pull_quote"']),
            (reverse('admin:portfolio_certification_change', args=[cert.pk]), ['name="is_featured"']),
            (reverse('admin:portfolio_blogpost_change', args=[post.pk]), ['name="related_project"']),
        ]
        for url, names in checks:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, url)
            for name in names:
                self.assertContains(response, name, msg_prefix=url)

    def test_public_pages_unchanged_by_new_empty_fields(self):
        for url in [reverse('index'), reverse('about'), reverse('projects'), reverse('blog')]:
            self.assertEqual(self.client.get(url).status_code, 200, url)


class CaseBoardTests(TestCase):
    def setUp(self):
        self.lead = Project.objects.create(
            title="Lazarus Lead", slug="lazarus-lead", is_featured=True, order=1, case_number=1,
            status='live', role="Solo builder", year="2025", project_type="Agent system",
            short_description="Lead summary.", tech_tags="Python, MCP", github_url="https://example.com/code")
        self.side = Project.objects.create(title="Side Quest", slug="side-quest", order=2, year="2024",
                                           tech_tags="Django", live_demo_url="https://example.com/demo")
        Project.objects.create(title="Hidden Draft", slug="hidden-draft", is_featured=True, is_published=False)

    def get(self):
        return self.client.get(reverse('projects'))

    def test_featured_on_board_and_others_in_archive(self):
        response = self.get()
        featured = [p.title for p in response.context['featured_cases']]
        archive = [p.title for p in response.context['archive_projects']]
        self.assertIn("Lazarus Lead", featured)
        self.assertNotIn("Side Quest", featured)
        self.assertIn("Side Quest", archive)
        self.assertNotIn("Lazarus Lead", archive)
        total = Project.objects.filter(is_published=True).count()
        self.assertEqual(len(featured) + len(archive), total)
        self.assertContains(response, "Cases · %d on file" % total)
        self.assertNotContains(response, "Hidden Draft")

    def test_board_row_shows_filled_fields(self):
        response = self.get()
        self.assertContains(response, "Case 001")
        self.assertContains(response, "Case closed · Shipped")
        self.assertContains(response, "Solo builder · 2025 · Agent system")
        self.assertContains(response, '<li class="tag">MCP</li>', html=True)

    def test_empty_fields_render_nothing(self):
        Project.objects.filter(pk=self.lead.pk).update(role='', year='', project_type='', status='', case_number=None)
        response = self.get()
        self.assertNotContains(response, 'case-row__meta')
        self.assertNotContains(response, 'case-stamp')
        self.assertContains(response, 'Case file')

    def test_evidence_counts_and_hidden_when_zero(self):
        self.assertNotContains(self.get(), 'case-row__evidence')
        CaseDecision.objects.create(project=self.lead, code="D-01", decision="d", tradeoff="t")
        CaseDecision.objects.create(project=self.lead, code="D-02", decision="d", tradeoff="t")
        CaseIncident.objects.create(project=self.lead, symptom="s", root_cause="r", fix="f")
        response = self.get()
        self.assertContains(response, "2 decisions")
        self.assertContains(response, "1 incident<")
        self.assertNotContains(response, "Replay on file")

    def test_replay_only_when_published_replay_exists(self):
        response = self.get()
        self.assertNotContains(response, "Watch the run")
        self.assertNotContains(response, "replay.js")
        replay = ProjectReplay.objects.create(
            project=self.lead, title="Run one", duration_s=3,
            steps=[{"t": 0, "actor": "agent", "kind": "info", "text": "hello"}])
        self.assertNotContains(self.get(), "Watch the run")
        replay.is_published = True
        replay.save()
        response = self.get()
        self.assertContains(response, "Watch the run")
        self.assertContains(response, "Replay on file")
        self.assertContains(response, "replay.js")
        self.assertContains(response, 'id="replay-data-%d"' % replay.pk)

    def test_thumbnail_fallback_has_no_duplicate_title(self):
        response = self.get()
        self.assertContains(response, 'case-thumb-fallback')
        self.assertNotContains(response, 'case-thumb-fallback__title')

    def test_archive_year_column_only_when_any_year(self):
        self.assertContains(self.get(), 'archive-table__year')
        Project.objects.filter(pk=self.side.pk).update(year='')
        self.assertNotContains(self.get(), 'archive-table__year')

    def test_no_featured_means_everything_in_archive(self):
        Project.objects.update(is_featured=False)
        response = self.get()
        self.assertEqual(response.context['featured_cases'], [])
        self.assertContains(response, "All projects")
        self.assertNotContains(response, 'class="case-board"')


class HomePhase8Tests(TestCase):
    def setUp(self):
        Project.objects.update(is_featured=False)
        self.a = Project.objects.create(title="Alpha Agent", slug="alpha-agent", order=1, is_featured=True,
                                        short_description="First sentence here. Second sentence here.")
        self.b = Project.objects.create(title="Beta Agent", slug="beta-agent", order=2,
                                        short_description="Beta summary.")

    def test_currently_line_only_when_filled(self):
        self.assertNotContains(self.client.get(reverse('index')), 'home-hero__currently')
        settings = SiteSettings.load()
        settings.currently = "Building a replay recorder"
        settings.save()
        self.assertContains(self.client.get(reverse('index')), "Currently: Building a replay recorder")

    def test_roster_shows_featured_only(self):
        response = self.client.get(reverse('index'))
        self.assertEqual([p.title for p in response.context['roster']], ["Alpha Agent"])
        self.assertContains(response, "Roster · 1 featured")
        total = Project.objects.filter(is_published=True).count()
        self.assertContains(response, "Case board and archive (%d on file)" % total)

    def test_roster_falls_back_to_first_four(self):
        Project.objects.update(is_featured=False)
        for i in range(5):
            Project.objects.create(title="Extra %d" % i, slug="extra-%d" % i, order=10 + i)
        response = self.client.get(reverse('index'))
        self.assertEqual(len(response.context['roster']), 4)
        self.assertContains(response, "Roster · 4 of")

    def test_roster_line_prefers_one_liner_then_first_sentence(self):
        self.assertContains(self.client.get(reverse('index')), "First sentence here.")
        self.assertNotContains(self.client.get(reverse('index')), "Second sentence here.")
        Project.objects.filter(pk=self.a.pk).update(one_liner="Short roster line")
        self.assertContains(self.client.get(reverse('index')), "Short roster line")

    def test_logs_list_latest_three_newest_first(self):
        for i in range(4):
            BlogPost.objects.create(title="Log %d" % i, slug="log-%d" % i, content="c", excerpt="e",
                                    published=True, event_date=date(2026, 1, i + 1))
        BlogPost.objects.create(title="Draft log", slug="draft-log", content="c", excerpt="e", event_date=date(2026, 2, 1))
        response = self.client.get(reverse('index'))
        titles = [p.title for p in response.context['latest_posts']]
        self.assertEqual(titles, ["Log 3", "Log 2", "Log 1"])
        self.assertContains(response, 'class="log-ledger"')
        self.assertContains(response, '<time class="label-mono" datetime="2026-01-04">04 Jan 2026</time>', html=True)

    def test_footer_last_updated_is_newest_change(self):
        from .context_processors import last_updated
        SiteSettings.load()
        About.objects.create(title="About", description="x")
        old = timezone.now() - timedelta(days=30)
        Project.objects.update(updated_at=old)
        BlogPost.objects.update(updated_at=old)
        About.objects.update(updated_at=old)
        SiteSettings.objects.update(updated_at=old)
        newest = timezone.now() - timedelta(days=2)
        BlogPost.objects.create(title="Fresh", slug="fresh", content="c", excerpt="e", published=True)
        BlogPost.objects.filter(slug="fresh").update(updated_at=newest)
        draft = BlogPost.objects.create(title="Draft", slug="draft", content="c", excerpt="e")
        settings = SiteSettings.objects.get(pk=1)
        self.assertEqual(last_updated(settings), newest)
        response = self.client.get(reverse('about'))
        self.assertContains(response, "Last updated")
        self.assertContains(response, newest.strftime("%d %b %Y"))

    def test_nav_has_skills_not_replay(self):
        ProjectReplay.objects.create(project=self.b, title="Run", duration_s=1, is_published=True,
                                     steps=[{"t": 0, "actor": "a", "kind": "info", "text": "x"}])
        response = self.client.get(reverse('projects'))
        self.assertNotContains(response, 'href="/#replay"')
        self.assertContains(response, 'href="/skills/" class="nav-link"')
        self.assertNotContains(response, "Watch the run")
        self.assertContains(self.client.get(reverse('skills')), 'href="/skills/" class="nav-link active"')



class LogsPhase8Tests(TestCase):
    def setUp(self):
        BlogPost.objects.all().delete()
        self.case = Project.objects.create(title="Linked Case", slug="linked-case", case_number=7)
        self.first = BlogPost.objects.create(title="First log", slug="first-log", content="word " * 450,
                                             excerpt="e", published=True, event_date=date(2025, 3, 1))
        self.second = BlogPost.objects.create(title="Second log", slug="second-log", content="short",
                                              excerpt="e", published=True, event_date=date(2026, 1, 2),
                                              related_project=self.case)
        self.third = BlogPost.objects.create(title="Third log", slug="third-log", content="short",
                                             excerpt="e", published=True, event_date=date(2026, 5, 9))
        BlogPost.objects.create(title="Draft log", slug="draft-log", content="x", excerpt="e",
                                event_date=date(2026, 2, 1), related_project=self.case)

    def test_reading_time(self):
        self.assertEqual(self.first.reading_minutes, 3)
        self.assertEqual(self.second.reading_minutes, 1)
        html_post = BlogPost(content="<p>" + "word " * 200 + "</p>")
        self.assertEqual(html_post.reading_minutes, 1)

    def test_index_grouped_by_year_newest_first(self):
        html = self.client.get(reverse('blog')).content.decode()
        self.assertLess(html.index('log-year-2026'), html.index('log-year-2025'))
        self.assertLess(html.index('Third log'), html.index('Second log'))
        self.assertIn('3 min read', html)

    def test_filed_under_only_for_linked_published_case(self):
        response = self.client.get(reverse('blog'))
        self.assertContains(response, 'Filed under', count=1)
        self.assertContains(response, 'Case 007 · Linked Case')
        Project.objects.filter(pk=self.case.pk).update(is_published=False)
        self.assertNotContains(self.client.get(reverse('blog')), 'Filed under')

    def test_detail_rail_and_case_link(self):
        response = self.client.get(reverse('blog_detail', args=['second-log']))
        self.assertContains(response, 'class="log-rail"')
        self.assertContains(response, '1 min')
        self.assertContains(response, reverse('project_detail', args=['linked-case']))
        response = self.client.get(reverse('blog_detail', args=['third-log']))
        self.assertNotContains(response, '>Case<')

    def test_older_and_newer_links(self):
        middle = self.client.get(reverse('blog_detail', args=['second-log'])).context
        self.assertEqual(middle['older_post'].slug, 'first-log')
        self.assertEqual(middle['newer_post'].slug, 'third-log')
        oldest = self.client.get(reverse('blog_detail', args=['first-log'])).context
        self.assertIsNone(oldest['older_post'])
        newest = self.client.get(reverse('blog_detail', args=['third-log'])).context
        self.assertIsNone(newest['newer_post'])
        self.assertEqual(newest['older_post'].slug, 'second-log')

    def test_same_day_posts_follow_creation_order(self):
        same = BlogPost.objects.create(title="Same day later", slug="same-day-later", content="x", excerpt="e",
                                       published=True, event_date=date(2026, 1, 2))
        context = self.client.get(reverse('blog_detail', args=['second-log'])).context
        self.assertEqual(context['newer_post'].slug, same.slug)

    def test_case_file_lists_its_published_logs(self):
        response = self.client.get(reverse('project_detail', args=['linked-case']))
        self.assertContains(response, 'Logs on this case')
        self.assertContains(response, 'href="#case-logs"')
        self.assertEqual([p.title for p in response.context['case_logs']], ["Second log"])
        other = Project.objects.create(title="Other Case", slug="other-case")
        self.assertNotContains(self.client.get(reverse('project_detail', args=['other-case'])), 'Logs on this case')



class AboutPhase8Tests(TestCase):
    def setUp(self):
        self.about = About.objects.create(title="About", description="Lead paragraph.",
                                          bio_paragraph_1="Second paragraph.", stat_accuracy="99%")
        EducationEntry.objects.create(year_range="2022-2026", degree="B.Tech", field_of_study="CS",
                                      institution="Some College", bullet_1="Focus one")
        EventEntry.objects.create(title="Hack Night", role="Lead", year="2025", location="Kurnool",
                                  description="", stat_1_value="25+", stat_1_label="Teams")
        self.cert_a = Certification.objects.create(title="Featured Cert", issuer="Acme", is_featured=True,
                                                   credential_url="https://example.com/verify")
        self.cert_b = Certification.objects.create(title="Plain Cert", issuer="Other")

    def get(self):
        return self.client.get(reverse('about'))

    def test_story_splits_lead_and_rest(self):
        response = self.get()
        self.assertEqual(response.context['story_lead'], ["Lead paragraph."])
        self.assertEqual(response.context['story_more'], ["Second paragraph."])
        self.assertContains(response, "Read the full story")

    def test_optional_cards_hidden_when_empty(self):
        response = self.get()
        self.assertNotContains(response, "Off duty")
        self.assertNotContains(response, "about-card--quote")
        self.assertContains(response, "about-card--story span-6")
        About.objects.filter(pk=self.about.pk).update(off_duty="Plays chess", pull_quote="Ship small")
        response = self.get()
        self.assertContains(response, "Plays chess")
        self.assertContains(response, '"Ship small"')
        self.assertContains(response, "about-card--story span-4")

    def test_now_card_from_current_role(self):
        self.assertNotContains(self.get(), '>Now<')
        ExperienceEntry.objects.create(organization="Lab", role="Intern", employment_type="internship",
                                       start_date=date(2026, 8, 1), is_current=True)
        response = self.get()
        self.assertContains(response, '>Now<')
        self.assertContains(response, "Lab · since Aug 2026")
        self.assertContains(response, 'entry__badge--current">Current<')

    def test_work_education_events_are_separate_sections(self):
        ExperienceEntry.objects.create(organization="Lab", role="Intern", employment_type="internship")
        response = self.get()
        for heading in ['id="work-heading"', 'id="education-heading"', 'id="events-heading"']:
            self.assertContains(response, heading)
        self.assertContains(response, "Hack Night")
        self.assertContains(response, '<span class="event-card__stat">25+</span>', html=True)

    def test_featured_certs_as_cards_rest_as_chips(self):
        response = self.get()
        self.assertEqual(response.context['featured_certs'], [self.cert_a])
        self.assertEqual(response.context['other_certs'], [self.cert_b])
        self.assertContains(response, "2 on file")
        self.assertContains(response, 'href="https://example.com/verify"')
        self.assertContains(response, ">Also<")

    def test_no_featured_certs_all_chips_without_also_label(self):
        Certification.objects.update(is_featured=False)
        response = self.get()
        self.assertNotContains(response, "cert-card")
        self.assertNotContains(response, ">Also<")
        self.assertContains(response, "Featured Cert")

    def test_stat_tiles_no_longer_shown(self):
        response = self.get()
        self.assertNotContains(response, "stat-tile")
        self.assertNotContains(response, "99%")

    def test_what_i_do_numbered(self):
        from .models import WhatIDo
        WhatIDo.objects.create(item="Build agents", order=0)
        WhatIDo.objects.create(item="Ship apps", order=1)
        response = self.get()
        self.assertContains(response, '<span class="about-do__num">01</span>', html=True)
        self.assertContains(response, "2 capabilities")



class CaseNoteTests(TestCase):
    def test_personal_note_only_when_filled(self):
        Project.objects.create(title="Noted", slug="noted")
        url = reverse('project_detail', args=['noted'])
        self.assertNotContains(self.client.get(url), 'case-note')
        Project.objects.filter(slug='noted').update(personal_note="I would log earlier next time.")
        response = self.client.get(url)
        self.assertContains(response, 'class="case-note"')
        self.assertContains(response, "I would log earlier next time.")



class MockupGapTests(TestCase):
    def setUp(self):
        Project.objects.update(is_featured=False)
        Project.objects.create(title="Bare Archive", slug="bare-archive")
        BlogPost.objects.all().delete()
        self.only = BlogPost.objects.create(title="Only log", slug="only-log", content="c", excerpt="e",
                                            published=True, event_date=date(2026, 1, 1))

    def test_archive_shows_none_listed_for_empty_stack(self):
        self.assertContains(self.client.get(reverse('projects')), "none listed")

    def test_logs_lead_and_read_link(self):
        response = self.client.get(reverse('blog'))
        self.assertContains(response, "Decisions, incidents and build notes from the work.")
        self.assertContains(response, "Logs · 1 filed")
        self.assertContains(response, 'log-entry__read')

    def test_log_pager_shows_none_yet_both_sides(self):
        response = self.client.get(reverse('blog_detail', args=['only-log']))
        self.assertContains(response, "None yet", count=2)
        self.assertContains(response, 'log-rail__back')

    def test_about_personnel_file_and_split_headings(self):
        from .models import WhatIDo
        WhatIDo.objects.create(item="Build agents")
        response = self.client.get(reverse('about'))
        self.assertContains(response, "About · personnel file")
        self.assertContains(response, "KP · ops://bunny")
        self.assertContains(response, 'section-head section-head--split')

    def test_footer_last_updated_sits_with_links(self):
        html = self.client.get(reverse('contact')).content.decode()
        self.assertLess(html.index('site-footer__end'), html.index('Last updated'))



class SkillsToolkitTests(TestCase):
    def setUp(self):
        Skill.objects.all().delete()
        Project.objects.update(is_published=False)
        self.soc = Project.objects.create(title="SOC Bot", slug="soc-bot", tech_tags="Python, MCP, Scikit-learn")
        Project.objects.create(title="Gate", slug="gate", tech_tags="Django, Python")
        Project.objects.create(title="Dup", slug="dup-1", tech_tags="Django")
        Project.objects.create(title="Dup", slug="dup-2", tech_tags="Django")
        Project.objects.create(title="Hidden", slug="hidden", tech_tags="Python", is_published=False)
        Skill.objects.create(name="Python", category="languages", is_featured=True)
        Skill.objects.create(name="MCP / Agentic AI", category="agentic", is_featured=True)
        Skill.objects.create(name="Django / DRF", category="web", is_featured=True)
        Skill.objects.create(name="HTML/CSS", category="web")
        Skill.objects.create(name="Scikit-Learn", category="ml")
        Skill.objects.create(name="ML", category="ml")

    def skills(self):
        return {s.name: s for s in self.client.get(reverse('skills')).context['skills']}

    def test_exact_part_matching_only_published(self):
        skills = self.skills()
        self.assertEqual([c['project'].title for c in skills["Python"].used_in], ["SOC Bot", "Gate"])
        self.assertEqual([c['project'].title for c in skills["MCP / Agentic AI"].used_in], ["SOC Bot"])
        self.assertEqual(skills["Scikit-Learn"].used_in_total, 1)
        self.assertEqual(skills["HTML/CSS"].used_in, [])
        self.assertEqual(skills["ML"].used_in, [])

    def test_same_title_projects_fold_together(self):
        django = self.skills()["Django / DRF"]
        self.assertEqual([(c['project'].title, c['count']) for c in django.used_in], [("Gate", 1), ("Dup", 2)])
        self.assertEqual(django.used_in_total, 3)

    def test_page_shows_core_cards_and_honest_empty_state(self):
        response = self.client.get(reverse('skills'))
        self.assertContains(response, "Toolkit</h1>")
        self.assertContains(response, "6 listed · 3 core")
        self.assertContains(response, 'href="/projects/soc-bot/"')
        self.assertContains(response, "Dup ×2")
        self.assertContains(response, "no case yet")
        self.assertContains(response, "3 cases")

    def test_bigger_areas_first(self):
        labels = [g['label'] for g in self.client.get(reverse('skills')).context['grouped_skills']]
        self.assertEqual(labels[:2], ["ML & Data", "Web & APIs"])



class LogTieBreakTests(TestCase):
    def test_identical_timestamps_still_chain(self):
        BlogPost.objects.all().delete()
        stamp = timezone.now()
        posts = [BlogPost.objects.create(title="T%d" % i, slug="t-%d" % i, content="c", excerpt="e",
                                         published=True, event_date=date(2026, 1, 1)) for i in range(3)]
        BlogPost.objects.update(created_at=stamp)
        middle = self.client.get(reverse('blog_detail', args=['t-1'])).context
        self.assertEqual(middle['older_post'].slug, 't-0')
        self.assertEqual(middle['newer_post'].slug, 't-2')
        index = [p.slug for p in self.client.get(reverse('blog')).context['posts']]
        self.assertEqual(index, ['t-2', 't-1', 't-0'])
