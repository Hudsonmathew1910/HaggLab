import json
from unittest import mock

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.content import gig_details
from apps.content.models import FAQ, FiverrGig, SiteSetting, Solution
from apps.tryit import hero_client

from . import assistant, knowledge, search


def make_service():
    s = Solution.objects.create(
        title='AI chatbots and RAG assistants', slug='ai-chatbots-rag-assistants', headline='Stop answering the same questions',
        problem='Staff answer the same questions.', cost_today='Search files.', step1_desc='Connect', step2_desc='Answer',
        step3_desc='Review', expected_outcome='Fewer repeat questions', metrics='repeat questions per week', order=1)
    gig = FiverrGig.objects.create(title='Gig A', url=gig_details.GIG_A)
    gig.services.add(s)
    gig_details.apply(FiverrGig, FAQ)
    return s, gig


class KnowledgeTest(TestCase):
    def setUp(self):
        cache.clear()
        knowledge.clear()
        self.service, self.gig = make_service()

    def test_passages_come_from_the_live_content(self):
        _v, chunks = knowledge.get_chunks()
        titles = [c['title'] for c in chunks]
        self.assertIn('Packages and prices: AI chatbots and RAG assistants', titles)
        self.assertTrue(any(t.startswith('FAQ: ') for t in titles))
        self.assertTrue(any(t.startswith('Privacy policy') for t in titles))  # pages are read too
        pricing = next(c for c in chunks if c['title'].startswith('Packages and prices'))
        self.assertIn('$150', pricing['text'])

    def test_an_admin_change_reaches_haggi_at_once(self):
        knowledge.get_chunks()
        self.gig.refresh_from_db()
        packages = self.gig.packages
        packages[1]['price'] = 175
        self.gig.packages = packages
        self.gig.save()  # the signal clears the knowledge
        _v, chunks = knowledge.get_chunks()
        pricing = next(c for c in chunks if c['title'].startswith('Packages and prices'))
        self.assertIn('$175', pricing['text'])
        self.assertNotIn('$150', pricing['text'])

    def test_search_finds_the_prices_for_a_cost_question(self):
        top = search.search('how much does a chatbot cost', top=3)
        self.assertTrue(any(c['title'].startswith('Packages and prices') for c in top))


class AnswerTest(TestCase):
    def setUp(self):
        cache.clear()
        knowledge.clear()
        make_service()

    def test_the_ai_gets_rules_and_passages_and_the_reply_is_cleaned(self):
        reply = 'The Standard package is $150. <b>Hi</b> [See packages](/solutions/ai-chatbots-rag-assistants/#pkg-title) [bad](https://evil.example)'
        with mock.patch.object(hero_client, 'chat', return_value=reply) as chat:
            out = assistant.answer('How much is a chatbot?', [])
        system = chat.call_args[0][0][0]['content']
        self.assertIn('Answer ONLY from the KNOWLEDGE', system)
        self.assertIn('Packages and prices: AI chatbots and RAG assistants', system)
        self.assertIn('Start a project form', system)
        self.assertNotIn('<b>', out['text'])
        self.assertEqual(out['links'][0]['url'], '/solutions/ai-chatbots-rag-assistants/#pkg-title')
        self.assertEqual(len(out['links']), 1)  # a link that is not in the knowledge is not offered

    def test_fiverr_visitors_are_kept_on_fiverr(self):
        with mock.patch.object(hero_client, 'chat', return_value='Message us on Fiverr.') as chat:
            assistant.answer('How do I order?', [], is_fiverr=True)
        system = chat.call_args[0][0][0]['content']
        self.assertIn('came from Fiverr', system)
        self.assertNotIn('point to the Start a project form', system)

    def test_page_steers_follow_up_questions(self):
        with mock.patch.object(hero_client, 'chat', return_value='ok') as chat:
            assistant.answer('How much is the Premium one?', [], page='/solutions/ai-chatbots-rag-assistants/')
        system = chat.call_args[0][0][0]['content']
        self.assertIn('reading the "AI chatbots and RAG assistants" service page', system)

    def test_too_long_or_empty_messages_are_refused(self):
        with self.assertRaises(assistant.AssistantError):
            assistant.answer('x' * 501, [])
        with self.assertRaises(assistant.AssistantError):
            assistant.answer('   ', [])


@override_settings(ASSISTANT_RATE='3/m', RATELIMIT_ENABLE=True)
class ApiTest(TestCase):
    def setUp(self):
        cache.clear()
        knowledge.clear()
        make_service()
        self.url = reverse('assistant_api')

    def post(self, body):
        return self.client.post(self.url, json.dumps(body), content_type='application/json')

    def test_conversation_is_kept_in_the_session_and_can_be_reset(self):
        with mock.patch.object(hero_client, 'chat', return_value='We build AI chatbots.'):
            r = self.post({'message': 'What do you build?', 'page': '/'})
        self.assertEqual(r.json()['text'], 'We build AI chatbots.')
        messages = self.client.get(self.url).json()['messages']
        self.assertEqual([m['role'] for m in messages], ['user', 'assistant'])
        self.post({'reset': True})
        self.assertEqual(self.client.get(self.url).json()['messages'], [])

    def test_busy_ai_gives_a_friendly_error(self):
        with mock.patch.object(hero_client, 'chat', side_effect=hero_client.NotConnected('down')):
            r = self.post({'message': 'Hello'})
        self.assertEqual(r.status_code, 503)
        self.assertIn('busy', r.json()['error'])

    def test_rate_limit(self):
        with mock.patch.object(hero_client, 'chat', return_value='ok'):
            codes = [self.post({'message': 'Hi'}).status_code for _ in range(4)]
        self.assertEqual(codes[-1], 429)

    def test_switch_off_hides_the_chat_and_the_api(self):
        self.assertContains(self.client.get(reverse('about')), 'data-haggi')
        SiteSetting.objects.update_or_create(key='assistant_enabled', defaults={'label': 'x', 'value': 'off'})
        self.assertNotContains(self.client.get(reverse('about')), 'data-haggi')
        self.assertEqual(self.client.get(self.url).status_code, 404)


class RicherKnowledgeTest(TestCase):
    def setUp(self):
        cache.clear()
        knowledge.clear()
        make_service()

    def test_a_new_product_in_the_admin_reaches_haggi_and_the_pages(self):
        from apps.content.models import Product
        knowledge.get_chunks()
        Product.objects.create(name='Nova', slug='nova', kind='Booking app', pitch='our booking app.',
                               description='A booking app.', url='https://nova.example.com/', order=5,
                               features=[{'name': 'Nova Calendar', 'kind': 'Calendar', 'desc': 'Shared calendar.'}])
        _v, chunks = knowledge.get_chunks()
        titles = [c['title'] for c in chunks]
        self.assertIn('Product: Nova', titles)
        self.assertIn('Product: Heros', titles)  # added by migration 0020
        overview = next(c for c in chunks if c['title'] == 'All our products')
        self.assertIn('Nova', overview['text'])
        self.assertIn('https://nova.example.com/', knowledge.get_directory())
        home = self.client.get(reverse('home'))
        self.assertContains(home, 'Visit Nova')
        self.assertContains(home, 'Visit Heros')
        self.assertContains(self.client.get(reverse('about')), 'Nova Calendar')

    def test_list_questions_get_the_overview_first(self):
        self.assertEqual(search.search('what services do you offer', top=1)[0]['title'], 'All our services')
        self.assertEqual(search.search('which products do you have?', top=1)[0]['title'], 'All our products')

    def test_service_passages_carry_choose_links_and_the_directory_lists_pages(self):
        _v, chunks = knowledge.get_chunks()
        pricing = next(c for c in chunks if c['title'].startswith('Packages and prices'))
        self.assertIn('/start/?service=ai_chatbots&package_choice=ai_chatbots%7CStandard', pricing['text'])
        directory = knowledge.get_directory()
        for url in ('/solutions/ai-chatbots-rag-assistants/#pkg-title', '/start/', '/privacy/', '/terms/'):
            self.assertIn(url, directory)

    def test_links_from_the_directory_are_allowed(self):
        out = assistant.links_from('See [the terms](/terms/) and [x](/nowhere/).', [])
        self.assertEqual([l['url'] for l in out], ['/terms/'])


class LinkChipTest(TestCase):
    def test_links_written_inside_a_passage_get_a_chip(self):
        passages = [{'title': 'Packages and prices: NLP', 'url': '/solutions/nlp/#pkg-title',
                     'text': 'Choose it: /start/?service=nlp_ml&package_choice=nlp_ml%7CStandard. '
                             'Or on Fiverr: https://www.fiverr.com/x/gig'}]
        reply = ('[Start a project form](/start/?service=nlp_ml&package_choice=nlp_ml%7CStandard) or '
                 '[Fiverr](https://www.fiverr.com/x/gig) or [made up](https://evil.example/)')
        out = assistant.links_from(reply, passages)
        self.assertEqual([l['title'] for l in out], ['Start a project', 'Order on Fiverr'])


class CompanyQuestionTest(TestCase):
    def setUp(self):
        cache.clear()
        knowledge.clear()
        make_service()

    def test_general_questions_always_get_the_company_basics(self):
        with mock.patch.object(hero_client, 'chat', return_value='We are a software and AI studio.') as chat:
            out = assistant.answer('Tell me about the company', [])
        system = chat.call_args[0][0][0]['content']
        self.assertIn('] About HaggLab (link: /about/)', system)
        self.assertIn('"The company"', system)
        self.assertEqual(out['links'], [])  # no unrelated chip under an answer without links

    def test_company_words_find_the_about_passage(self):
        top = [c['title'] for c in search.search('tell me about the company', top=3)]
        self.assertTrue(top[0].startswith('About'), top)
        self.assertFalse(any('Tell us the problem' in t for t in top))


class ChipLabelTest(TestCase):
    def test_fixed_pages_get_clean_labels(self):
        passages = [{'title': 'About: Already built and deployed', 'url': '/about/', 'text': ''}]
        out = assistant.links_from('See [About](/about/) and [form](/start/).', passages)
        self.assertEqual([l['title'] for l in out], ['About HaggLab', 'Start a project'])
