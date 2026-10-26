from unittest import mock
from django.core.cache import cache
from django.test import override_settings
from django.test import TestCase, Client
from django.urls import reverse
from apps.leads.models import Inquiry

@override_settings(TURNSTILE_SECRET_KEY='', TURNSTILE_SITE_KEY='')
class LeadsRoutingTest(TestCase):
    def setUp(self):
        self.client = Client()
        cache.clear()  # each test starts with a fresh rate-limit counter
        # These tests cover the Fiverr routing, so the Fiverr switch is on
        from apps.content.models import SiteSetting
        SiteSetting.objects.create(key='fiverr_enabled', label='Fiverr switch', value='on')

    def test_direct_visitor_sees_form(self):
        # Path B: direct visitor
        response = self.client.get(reverse('start_project'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tell us the problem')
        self.assertContains(response, 'Send project details')
        self.assertTemplateUsed(response, 'pages/start.html')

    def test_fiverr_visitor_by_param_sees_path_a_only(self):
        # Path A: ref=fiverr
        response = self.client.get(reverse('start_project') + '?ref=fiverr')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Message us on Fiverr')
        self.assertNotContains(response, '<form method="post"')
        self.assertNotContains(response, 'Send project details')

    def test_fiverr_session_persists(self):
        # Once flagged as Fiverr, session stays Fiverr
        self.client.get(reverse('home') + '?ref=fiverr')
        response = self.client.get(reverse('start_project'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Message us on Fiverr')
        self.assertNotContains(response, '<form method="post"')

    def test_valid_form_submission(self):
        # Valid Path B submission
        data = {
            'name': 'Alice Smith',
            'email': 'alice@example.com',
            'service': 'answer_faster',
            'problem': 'We spend 8 hours every week answering repeat questions from staff in Slack.',
            'data_available': 'documents',
            'timeline': 'month',
            'consent': 'on',
        }
        response = self.client.post(reverse('start_project'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Inquiry.objects.count(), 1)
        inquiry = Inquiry.objects.first()
        self.assertEqual(inquiry.email, 'alice@example.com')

    def test_honeypot_rejects_bots(self):
        # Spam trap: website_url filled by bot
        data = {
            'name': 'Bot',
            'email': 'bot@example.com',
            'service': 'answer_faster',
            'problem': 'Spam content',
            'data_available': 'none',
            'timeline': 'asap',
            'consent': 'on',
            'website_url': 'http://spam.ru',
        }
        response = self.client.post(reverse('start_project'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Spam detected')
        self.assertEqual(Inquiry.objects.count(), 0)

    def _valid_data(self, **extra):
        data = {
            'name': 'Alice Smith', 'email': 'alice@example.com', 'service': 'answer_faster',
            'problem': 'We spend 8 hours every week answering repeat questions from staff.',
            'data_available': 'documents', 'timeline': 'month', 'consent': 'on',
        }
        data.update(extra)
        return data

    @override_settings(TURNSTILE_SECRET_KEY='secret', TURNSTILE_SITE_KEY='site')
    def test_turnstile_missing_token_is_rejected(self):
        response = self.client.post(reverse('start_project'), self._valid_data())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please complete the security check')
        self.assertEqual(Inquiry.objects.count(), 0)

    @override_settings(TURNSTILE_SECRET_KEY='secret', TURNSTILE_SITE_KEY='site')
    def test_turnstile_failed_check_is_rejected(self):
        with mock.patch('apps.leads.forms.verify_turnstile', return_value={'success': False}):
            response = self.client.post(reverse('start_project'), self._valid_data(**{'cf-turnstile-response': 'bad'}))
        self.assertContains(response, 'Security verification failed')
        self.assertEqual(Inquiry.objects.count(), 0)

    @override_settings(TURNSTILE_SECRET_KEY='secret', TURNSTILE_SITE_KEY='site')
    def test_turnstile_passed_check_is_accepted(self):
        with mock.patch('apps.leads.forms.verify_turnstile', return_value={'success': True}):
            response = self.client.post(reverse('start_project'), self._valid_data(**{'cf-turnstile-response': 'ok'}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Inquiry.objects.count(), 1)



class FiverrSwitchOffTest(TestCase):
    """With no fiverr_enabled setting (the default), Fiverr is off everywhere."""

    def test_fiverr_link_and_page_are_gone(self):
        page = self.client.get(reverse('home')).content.decode()
        self.assertNotIn('Hire on Fiverr', page)
        self.assertNotIn('/hire/', page)
        self.assertRedirects(self.client.get(reverse('hire_fiverr')), reverse('start_project'))

    def test_fiverr_referral_still_gets_the_form(self):
        self.client.get(reverse('home') + '?ref=fiverr')
        response = self.client.get(reverse('start_project'))
        self.assertContains(response, 'Send project details')
        self.assertNotContains(response, 'Found us on Fiverr')

    def test_sitemap_leaves_out_the_fiverr_page(self):
        self.assertNotContains(self.client.get(reverse('sitemap')), '/hire/')


class FiverrPerGigTest(TestCase):
    """Fiverr appears only for projects and services that have a gig link."""

    def setUp(self):
        from apps.content.models import Project, SiteSetting, Solution
        self.ai = Solution.objects.create(title='AI', slug='ai', headline='h', problem='p', cost_today='c',
                                          step1_desc='a', step2_desc='b', step3_desc='c', order=1)
        self.book = Solution.objects.create(title='Book', slug='book', headline='h', problem='p', cost_today='c',
                                            step1_desc='a', step2_desc='b', step3_desc='c', order=2)
        common = dict(headline='h', problem='p', cost_today='c', step1_desc='a', step2_desc='b', step3_desc='c',
                      try_ready=True)
        Project.objects.create(title='DocuMind', slug='documind', order=1, **common).solutions.add(self.ai)
        Project.objects.create(title='BookIt', slug='bookit', order=2, **common).solutions.add(self.book)
        from apps.content.models import FiverrGig
        gig = FiverrGig.objects.create(title='AI assistants', url='https://www.fiverr.com/s/AAA')
        gig.projects.set(Project.objects.filter(slug='documind'))
        gig.services.set([self.ai])

    def test_auto_turns_fiverr_on_when_a_gig_exists(self):
        self.assertContains(self.client.get(reverse('home')), 'Hire on Fiverr')
        self.assertContains(self.client.get(reverse('hire_fiverr')), 'fiverr.com/s/AAA')

    def test_project_with_gig_links_to_it_and_project_without_does_not(self):
        with_gig = self.client.get(reverse('project_detail', args=['documind'])).content.decode()
        without = self.client.get(reverse('project_detail', args=['bookit'])).content.decode()
        self.assertIn('fiverr.com/s/AAA', with_gig)
        self.assertNotIn('Order on Fiverr', without)
        self.assertIn('Get your project plan', without)

    def test_service_button_only_where_a_project_has_a_gig(self):
        self.assertContains(self.client.get(reverse('solution_detail', args=['ai'])), 'Order on Fiverr')
        self.assertNotContains(self.client.get(reverse('solution_detail', args=['book'])), 'Order on Fiverr')

    def test_one_gig_covers_several_projects(self):
        from apps.content.models import FiverrGig, Project
        FiverrGig.objects.get(url='https://www.fiverr.com/s/AAA').projects.add(Project.objects.get(slug='bookit'))
        self.assertContains(self.client.get(reverse('project_detail', args=['bookit'])), 'fiverr.com/s/AAA')
        hire = self.client.get(reverse('hire_fiverr')).content.decode()
        self.assertEqual(hire.count('<div class="gig">'), 1)  # one row for the gig, not one per project

    def test_service_without_its_own_gig_shows_no_fiverr(self):
        from apps.content.models import FiverrGig, Project
        # BookIt is covered by the gig, but the gig is not ticked for the Book service
        FiverrGig.objects.get(url='https://www.fiverr.com/s/AAA').projects.add(Project.objects.get(slug='bookit'))
        self.assertNotContains(self.client.get(reverse('solution_detail', args=['book'])), 'Order on Fiverr')
        self.assertContains(self.client.get(reverse('solution_detail', args=['ai'])), 'fiverr.com/s/AAA')

    def test_inactive_gig_is_hidden(self):
        from apps.content.models import FiverrGig
        FiverrGig.objects.update(active=False)
        self.assertNotContains(self.client.get(reverse('home')), 'Hire on Fiverr')

    def test_off_still_hides_everything(self):
        from apps.content.models import SiteSetting
        SiteSetting.objects.create(key='fiverr_enabled', label='s', value='off')
        self.assertNotContains(self.client.get(reverse('project_detail', args=['documind'])), 'fiverr.com')


@override_settings(TURNSTILE_SECRET_KEY='', TURNSTILE_SITE_KEY='', OWNER_EMAIL='owner@example.com',
                   EMAIL_HOST='smtp.example.com', EMAIL_HOST_USER='sender@example.com',
                   EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class InquiryEmailTest(TestCase):
    def setUp(self):
        cache.clear()

    def post_inquiry(self):
        return self.client.post(reverse('start_project'), {
            'name': 'Asha', 'email': 'asha@clinic.example', 'service': 'answer_faster',
            'problem': 'Reception answers the same phone questions for 3 hours a day.',
            'data_available': 'documents', 'timeline': 'month', 'consent': 'on'})

    def test_owner_gets_an_email_with_reply_to_the_client(self):
        from django.core import mail
        self.assertEqual(self.post_inquiry().status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ['owner@example.com'])
        self.assertEqual(email.reply_to, ['asha@clinic.example'])
        self.assertIn('3 hours a day', email.body)

    def test_inquiry_is_saved_even_when_email_fails(self):
        from unittest import mock as m
        with m.patch('django.core.mail.EmailMessage.send', side_effect=OSError('smtp down')):
            self.assertEqual(self.post_inquiry().status_code, 302)
        self.assertEqual(Inquiry.objects.count(), 1)

    @override_settings(EMAIL_HOST='')
    def test_no_email_settings_still_saves(self):
        from django.core import mail
        self.post_inquiry()
        self.assertEqual(Inquiry.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 0)
