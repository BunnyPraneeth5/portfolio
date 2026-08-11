from django.test import TestCase, Client
from django.urls import reverse


class WidgetSmokeTestCase(TestCase):
    def test_contact_and_projects_render(self):
        c = Client()
        for name in ['contact', 'projects', 'index', 'about', 'skills', 'blog']:
            resp = c.get(reverse(name))
            self.assertEqual(resp.status_code, 200, name)
            self.assertContains(resp, 'pet-widget-root', msg_prefix=name)
            self.assertContains(resp, 'pet-chat-panel', msg_prefix=name)
