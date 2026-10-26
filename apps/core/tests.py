from django.test import TestCase, Client, override_settings
from django.urls import reverse
from apps.content.models import Solution, Project, FAQ

class PagesViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.solution = Solution.objects.create(
            title="Answer faster",
            slug="answer-faster",
            headline="Stop answering repeat questions",
            problem="Staff repeats questions all day long.",
            cost_today="Manual lookup.",
            step1_desc="Upload docs",
            step2_desc="Assistant retrieves",
            step3_desc="Human reviews",
            expected_outcome="Faster reply",
            metrics="reply time",
            order=1
        )
        self.project = Project.objects.create(
            title="DocuMind",
            slug="documind",
            headline="Answers from docs",
            status="Concept",
            problem="Staff repeats questions",
            cost_today="Manual lookup",
            step1_desc="Upload",
            step2_desc="Query",
            step3_desc="Verify",
            order=1
        )
        self.project.solutions.add(self.solution)
        self.faq = FAQ.objects.create(
            question="How do you scope a project?",
            answer="Projects are scoped one problem at a time.",
            page="home",
            order=1
        )

    def test_all_marketing_pages_return_200(self):
        urls = [
            reverse('home'),
            reverse('solutions_hub'),
            reverse('solution_detail', kwargs={'slug': self.solution.slug}),
            reverse('projects_hub'),
            reverse('project_detail', kwargs={'slug': self.project.slug}),
            reverse('process'),
            reverse('security_data'),
            reverse('about'),
            reverse('faq'),
            reverse('privacy_policy'),
            reverse('terms_of_service'),
            reverse('robots'),
            reverse('sitemap'),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"URL {url} failed with {response.status_code}")

    def test_fiverr_page_follows_the_switch(self):
        from apps.content.models import SiteSetting
        self.assertEqual(self.client.get(reverse('hire_fiverr')).status_code, 302)  # off by default
        SiteSetting.objects.create(key='fiverr_enabled', label='Fiverr switch', value='on')
        self.assertEqual(self.client.get(reverse('hire_fiverr')).status_code, 200)

    def test_robots_content(self):
        response = self.client.get(reverse('robots'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"User-agent: *", response.content)
        self.assertIn(b"Disallow: /admin/", response.content)

    def test_sitemap_content(self):
        response = self.client.get(reverse('sitemap'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"<loc>", response.content)
        self.assertIn(b"documind", response.content)


class NotFoundPageTest(TestCase):
    @override_settings(DEBUG=False)
    def test_unknown_address_shows_the_hagglab_404_page(self):
        res = self.client.get('/this-page-does-not-exist/')
        self.assertEqual(res.status_code, 404)
        self.assertContains(res, 'We can’t find that page.', status_code=404)
        self.assertContains(res, '/this-page-does-not-exist/', status_code=404)

    @override_settings(DEBUG=True)
    def test_unknown_address_shows_the_hagglab_404_page_locally_too(self):
        res = self.client.get('/no-such-page/')
        self.assertContains(res, 'We can’t find that page.', status_code=404)
        self.assertNotContains(res, 'Using the URLconf', status_code=404)

    @override_settings(DEBUG=False)
    def test_styleguide_is_hidden_in_production(self):
        self.assertEqual(self.client.get('/styleguide/').status_code, 404)

    @override_settings(DEBUG=True)
    def test_missing_project_shows_the_hagglab_404_page_locally(self):
        self.assertContains(self.client.get('/projects/no-such-project/'), 'Error 404', status_code=404)
