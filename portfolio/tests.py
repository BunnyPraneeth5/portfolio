from datetime import date

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase, TransactionTestCase, Client
from django.urls import reverse

from . import chatbot
from .admin import ExperienceEntryAdminForm
from .models import (
    About, Skill, Project, BlogPost, ContactMessage,
    Certification, EventEntry, ExperienceEntry,
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
        self.assertContains(response, 'class="nav-link active">Projects</a>')
        self.assertContains(response, 'class="nav-link">About</a>')


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
