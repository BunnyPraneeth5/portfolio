from datetime import date

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase, TransactionTestCase, Client
from django.urls import reverse

from . import chatbot
from .admin import ExperienceEntryAdminForm
from .models import (
    About, Skill, Project, BlogPost, ContactMessage,
    Certification, EventEntry, ExperienceEntry, SiteSettings,
    CaseDecision, CaseIncident,
)

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
        self.settings_obj.looking_for = ""
        self.settings_obj.save()
        response = self.client.get(reverse('index'))
        self.assertNotContains(response, "Looking for")
        self.settings_obj.looking_for = "Agentic AI roles"
        self.settings_obj.save()
        response = self.client.get(reverse('index'))
        self.assertContains(response, "Looking for")
        self.assertContains(response, "Agentic AI roles")

    def test_status_line_follows_open_to_work(self):
        self.settings_obj.open_to_work = True
        self.settings_obj.save()
        self.assertContains(self.client.get(reverse('index')), "Open to roles")
        self.settings_obj.open_to_work = False
        self.settings_obj.save()
        self.assertNotContains(self.client.get(reverse('index')), "Open to roles")

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
        reply = chatbot.get_reply("tell me about your experience")
        self.assertIn("AI Intern @ Lazarus Labs (Internship, Mar 2026 – Present)", reply)
        self.assertIn("Built docking tools.", reply)
        self.assertLess(reply.index("Lazarus Labs"), reply.index("Old Co"))
        self.assertIn("Hackathons and leadership", reply)
        self.assertLess(reply.index("Old Co"), reply.index("Hackathon X"))

    def test_experience_empty(self):
        reply = chatbot.get_reply("work experience")
        self.assertIn("haven't added", reply)
        self.assertIn("/about/", reply)
        self.assertNotIn("TechTrotter", reply)

    def test_certifications(self):
        Certification.objects.create(title="SQL Advanced", issuer="HackerRank")
        Certification.objects.create(title="CSS")
        reply = chatbot.get_reply("do you have any certifications?")
        self.assertIn("• SQL Advanced (HackerRank)", reply)
        self.assertIn("• CSS", reply)

    def test_certifications_empty(self):
        reply = chatbot.get_reply("certifications")
        self.assertIn("haven't listed", reply)
        self.assertIn("/about/", reply)
        self.assertNotIn("MCP Certified", reply)

    def test_routing_availability_vs_past_work(self):
        self.assertEqual(chatbot._match_intent("are you open to internships"), 'internship')
        for question in ["tell me about your internship", "where did you work",
                         "work experience", "where have you worked before"]:
            self.assertIn(chatbot._match_intent(question), ('past_work', 'experience'), question)


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
