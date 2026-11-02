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

    def test_fiverr_visitor_can_leave_fiverr_mode(self):
        self.client.get(reverse('home') + '?ref=fiverr')
        self.assertContains(self.client.get(reverse('start_project')), 'Not from Fiverr?')
        response = self.client.get(reverse('start_project') + '?ref=site')
        self.assertContains(response, 'Send project details')
        self.assertNotContains(self.client.get(reverse('home')), 'You came from Fiverr')

    def test_found_you_on_fiverr_link_does_not_switch_the_site(self):
        self.assertContains(self.client.get(reverse('start_project') + '?origin=fiverr'), 'Message us on Fiverr')
        self.assertContains(self.client.get(reverse('start_project')), 'Send project details')

    def test_valid_form_submission(self):
        # Valid Path B submission
        data = {
            'name': 'Alice Smith',
            'email': 'alice@example.com',
            'service': 'ai_chatbots',
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
            'service': 'ai_chatbots',
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
            'name': 'Alice Smith', 'email': 'alice@example.com', 'service': 'ai_chatbots',
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
            'name': 'Asha', 'email': 'asha@clinic.example', 'service': 'ai_chatbots',
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


@override_settings(TURNSTILE_SECRET_KEY='', TURNSTILE_SITE_KEY='')
class PackagePickTest(TestCase):
    """/start lets a visitor pick a package and extras of the chosen service's gig."""
    def setUp(self):
        cache.clear()
        from apps.content.models import Solution, FiverrGig, FAQ, SiteSetting
        from apps.content import gig_details
        solution = Solution.objects.create(
            title='AI chatbots and RAG assistants', slug='ai-chatbots-rag-assistants', headline='h', problem='p',
            cost_today='c', step1_desc='1', step2_desc='2', step3_desc='3', expected_outcome='e', metrics='m')
        gig = FiverrGig.objects.create(title='Gig A', url=gig_details.GIG_A)
        gig.services.add(solution)
        gig_details.apply(FiverrGig, FAQ)
        SiteSetting.objects.update_or_create(key='inr_rate', defaults={'label': 'rate', 'value': '95'})
        self.data = {
            'name': 'Alice Smith', 'email': 'alice@example.com', 'service': 'ai_chatbots',
            'problem': 'We spend 8 hours every week answering repeat questions.', 'data_available': 'documents',
            'timeline': 'month', 'consent': 'on',
        }
        self.answers = {
            'ask_ai_chatbots_0': 'Answer customer questions from our FAQ.', 'ask_ai_chatbots_1': 'On my website',
            'ask_ai_chatbots_2': 'FAQ text', 'ask_ai_chatbots_3': 'About 40 a week',
        }

    def test_form_lists_packages_with_rupees(self):
        response = self.client.get(reverse('start_project') + '?service=ai_chatbots&package_choice=ai_chatbots|Standard')
        self.assertContains(response, 'RAG Document Assistant')
        self.assertContains(response, '≈ ₹14,300')  # 150 x 95, to the nearest 100
        self.assertContains(response, 'value="ai_chatbots|Standard" data-price="150" selected')

    def test_package_and_extras_are_saved(self):
        response = self.client.post(reverse('start_project'), dict(
            self.data, **self.answers, package_choice='ai_chatbots|Premium',
            extra_choices=['ai_chatbots|3', 'ai_chatbots|6']))
        self.assertEqual(response.status_code, 302)
        inquiry = Inquiry.objects.get()
        self.assertIn('Premium: RAG, Tools and Fallback ($250', inquiry.package)
        self.assertIn('RAG on your files', inquiry.extras)
        self.assertIn('Additional revision', inquiry.extras)
        self.assertEqual(inquiry.answers[1], {'question': 'Where will the chatbot be used?', 'answer': 'On my website'})
        self.assertEqual(inquiry.answers[4]['answer'], '')  # the file link is optional
        # The service's own questions replace "Describe the problem" and "Do you have documents or data?"
        self.assertEqual(inquiry.problem, 'Answer customer questions from our FAQ.')
        self.assertEqual(inquiry.data_available, 'see_answers')

    def test_package_of_another_service_is_dropped(self):
        self.client.post(reverse('start_project'), dict(
            self.data, service='nlp_ml', package_choice='ai_chatbots|Basic', extra_choices=['ai_chatbots|3']))
        inquiry = Inquiry.objects.get()
        self.assertEqual((inquiry.package, inquiry.extras), ('', ''))

    def test_no_rate_hides_rupees(self):
        from apps.content.models import SiteSetting
        SiteSetting.objects.filter(key='inr_rate').update(value='')
        self.assertNotContains(self.client.get(reverse('start_project') + '?service=ai_chatbots'), '₹')

    def test_package_answers_timeline_and_budget(self):
        data = dict(self.data, **self.answers, package_choice='ai_chatbots|Standard', extra_choices=['ai_chatbots|3'])
        del data['timeline']
        self.assertEqual(self.client.post(reverse('start_project'), data).status_code, 302)
        inquiry = Inquiry.objects.get()
        self.assertEqual(inquiry.timeline, 'package')
        self.assertEqual(inquiry.budget_band, 'Package total: $240 ≈ ₹22,800')  # 150 + 90 extra

    def test_service_needs_a_package_and_answers(self):
        response = self.client.post(reverse('start_project'), dict(self.data, ask_ai_chatbots_1='Not a real option'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please choose a package.')
        self.assertContains(response, 'Please answer this question.')
        self.assertFalse(Inquiry.objects.exists())

    def test_custom_project_needs_a_timeline_not_a_package(self):
        data = dict(self.data, service='not_sure', package_choice='ai_chatbots|Basic')
        del data['timeline']
        response = self.client.post(reverse('start_project'), data)
        self.assertContains(response, 'Please choose when you need it.')
        self.assertNotContains(response, 'Please choose a package.')
        data['timeline'] = 'month'
        self.assertEqual(self.client.post(reverse('start_project'), data).status_code, 302)
        self.assertEqual(Inquiry.objects.get().package, '')  # a package is dropped for a custom project

    def test_custom_project_needs_the_problem_and_data_questions(self):
        data = dict(self.data, service='not_sure', problem='')
        del data['data_available']
        response = self.client.post(reverse('start_project'), data)
        self.assertContains(response, 'Please describe the problem.')
        self.assertContains(response, 'Please choose an answer.')
        self.assertFalse(Inquiry.objects.exists())


class ServiceWithoutGigTest(TestCase):
    """AI integration and support has no Fiverr gig: its packages live on the service."""
    def setUp(self):
        cache.clear()
        from apps.content.models import Solution, FAQ
        from apps.content import gig_details
        Solution.objects.create(
            title='AI integration and support', slug='ai-integration-support', headline='h', problem='p',
            cost_today='c', step1_desc='1', step2_desc='2', step3_desc='3', expected_outcome='e', metrics='m')
        gig_details.apply_services(Solution, FAQ)

    def test_service_page_shows_packages_without_fiverr(self):
        response = self.client.get(reverse('solution_detail', kwargs={'slug': 'ai-integration-support'}))
        self.assertContains(response, 'AI with Fallback and Tests')
        self.assertContains(response, 'Can you work on an app someone else built?')
        self.assertNotContains(response, 'Order on Fiverr')
        # Every Start a project link on the page picks this service
        self.assertContains(response, '/start/?service=ai_integration')

    def test_start_form_offers_its_packages(self):
        response = self.client.get(reverse('start_project') + '?service=ai_integration')
        self.assertContains(response, 'Production Fix and Support')
        self.assertContains(response, '<option value="ai_integration" selected>')


import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile

_UPLOAD_DIR = tempfile.mkdtemp()


@override_settings(TURNSTILE_SECRET_KEY='', TURNSTILE_SITE_KEY='', PRIVATE_STORAGE_ROOT=_UPLOAD_DIR)
class AttachmentUploadTest(PackagePickTest):
    """The optional "Attachment" order question takes a real file, stored privately."""

    def post(self, upload):
        data = dict(self.data, **self.answers, package_choice='ai_chatbots|Basic', ask_ai_chatbots_4=upload)
        return self.client.post(reverse('start_project'), data)

    def test_pdf_is_saved_privately(self):
        response = self.post(SimpleUploadedFile('policy handbook.pdf', b'%PDF-1.7\nsample', 'application/pdf'))
        self.assertEqual(response.status_code, 302)
        inquiry = Inquiry.objects.get()
        item = inquiry.files.get()
        self.assertEqual(item.original_name, 'policy handbook.pdf')
        self.assertTrue(item.path.startswith(str(inquiry.uuid)))
        self.assertNotIn('handbook', item.path)  # stored under a random name
        self.assertEqual(inquiry.answers[4]['answer'], 'policy handbook.pdf')

    def test_renamed_file_is_refused(self):
        response = self.post(SimpleUploadedFile('notes.pdf', b'MZ\x90\x00 not a pdf', 'application/pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'does not look like a real .pdf file')
        self.assertFalse(Inquiry.objects.exists())

    def test_wrong_type_is_refused(self):
        response = self.post(SimpleUploadedFile('run.exe', b'MZ\x90\x00', 'application/octet-stream'))
        self.assertContains(response, 'Please attach a PDF, CSV, Excel, Word, TXT, PNG or JPG file.')

    def test_too_large_is_refused(self):
        from apps.leads import uploads
        big = SimpleUploadedFile('data.csv', b'a,b\n' + b'1,2\n' * (uploads.MAX_BYTES // 4 + 1), 'text/csv')
        self.assertContains(self.post(big), 'The file is too large.')

    def test_only_staff_can_download(self):
        from django.contrib.auth.models import User
        self.post(SimpleUploadedFile('sales.csv', b'month,sales\njan,10\n', 'text/csv'))
        url = reverse('inquiry_file', args=[Inquiry.objects.get().files.get().pk])
        self.assertEqual(self.client.get(url).status_code, 302)  # sent to the login page
        User.objects.create_user('staff', password='pw-12345-x', is_staff=True)
        self.client.login(username='staff', password='pw-12345-x')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertEqual(b''.join(response.streaming_content), b'month,sales\njan,10\n')


@override_settings(TURNSTILE_SECRET_KEY='', TURNSTILE_SITE_KEY='')
class FormLimitsTest(TestCase):
    def test_oversized_problem_text_is_refused(self):
        cache.clear()
        response = self.client.post(reverse('start_project'), {
            'name': 'A', 'email': 'a@example.com', 'service': 'not_sure', 'problem': 'x' * 5001,
            'data_available': 'documents', 'timeline': 'month', 'consent': 'on'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Inquiry.objects.exists())

    def test_script_in_a_field_is_shown_as_text_not_run(self):
        cache.clear()
        response = self.client.post(reverse('start_project'), {
            'name': '<script>alert(1)</script>', 'email': 'not-an-email', 'service': 'not_sure'})
        self.assertNotContains(response, '<script>alert(1)</script>')
        self.assertContains(response, '&lt;script&gt;alert(1)&lt;/script&gt;')
