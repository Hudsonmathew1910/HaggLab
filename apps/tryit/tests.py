import json
from unittest import mock

import httpx

from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from apps.content.models import Project, Solution
from apps.tryit import hero_client
from apps.tryit.specs import InvalidInput, clean_payload


def make_project(slug, try_ready):
    return Project.objects.create(
        title=slug.title(), slug=slug, headline=f'{slug} headline', problem='A problem.',
        cost_today='Today.', step1_desc='a', step2_desc='b', step3_desc='c', try_ready=try_ready)


@override_settings(PREVIEW_UNFINISHED_PROJECTS=False, HEROS_API_KEYS=[])
class PublicVisibilityTest(TestCase):
    """Only projects with a working Try it page are shown to visitors."""

    def setUp(self):
        self.ready = make_project('documind', True)
        self.unfinished = make_project('bookit', False)

    def test_unfinished_project_is_hidden_everywhere(self):
        self.assertEqual(self.client.get(reverse('project_detail', args=['bookit'])).status_code, 404)
        self.assertEqual(self.client.get(reverse('try_project', args=['bookit'])).status_code, 404)
        hub = self.client.get(reverse('projects_hub'))
        self.assertContains(hub, 'documind headline')
        self.assertNotContains(hub, 'bookit headline')
        self.assertNotContains(self.client.get(reverse('sitemap')), 'bookit')

    def test_ready_project_has_a_try_page(self):
        response = self.client.get(reverse('try_project', args=['documind']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-try-url="/api/try/documind/"')

    def test_no_status_or_demo_labels_on_public_pages(self):
        for url in (reverse('home'), reverse('projects_hub'), reverse('project_detail', args=['documind']),
                    reverse('try_project', args=['documind'])):
            html = self.client.get(url).content.decode()
            for word in ('Concept', 'Live demo', 'Prototype', 'not built yet'):
                self.assertNotIn(word, html, f'{word!r} shown on {url}')

    def test_delivered_count_shows_only_when_real(self):
        url = reverse('project_detail', args=['documind'])
        self.assertNotContains(self.client.get(url), 'Delivered for')
        self.ready.delivered_count = 2
        self.ready.save()
        self.assertContains(self.client.get(url), 'Delivered for 2 clients')


@override_settings(PREVIEW_UNFINISHED_PROJECTS=False, HEROS_API_KEYS=[])
class TryApiTest(TestCase):
    def setUp(self):
        cache.clear()
        make_project('documind', True)
        make_project('bookit', False)
        self.client = Client(enforce_csrf_checks=False)
        self.url = reverse('try_api', args=['documind'])

    def post(self, data, url=None):
        return self.client.post(url or self.url, data=json.dumps(data), content_type='application/json')

    def test_unfinished_project_api_is_refused(self):
        self.assertEqual(self.post({'message': 'hi'}, reverse('try_api', args=['bookit'])).status_code, 404)

    def test_get_is_not_allowed(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_empty_input_is_rejected(self):
        response = self.post({})
        self.assertEqual(response.status_code, 400)
        self.assertIn('type something', response.json()['error'])

    def test_not_connected_gives_friendly_503(self):
        response = self.post({'message': 'How many leave days?'})
        self.assertEqual(response.status_code, 503)
        self.assertFalse(response.json()['ok'])

    def test_reply_is_passed_through_and_filtered(self):
        fake = {'text': 'Ten days a year.', 'source': 'Handbook p.3', 'secret': 'x'}
        with mock.patch.object(hero_client, 'run', return_value=fake) as run:
            response = self.post({'message': 'How many leave days?', 'evil': 'drop'})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['text'], 'Ten days a year.')
        self.assertNotIn('secret', body)
        run.assert_called_once_with('documind', {'message': 'How many leave days?'})

    @override_settings(TRY_RATE='2/h', RATELIMIT_ENABLE=True)
    def test_visitor_limit(self):
        with mock.patch.object(hero_client, 'run', return_value={'text': 'ok'}):
            codes = [self.post({'message': 'hi'}).status_code for _ in range(3)]
        self.assertEqual(codes, [200, 200, 429])


class CleanPayloadTest(TestCase):
    def test_text_is_trimmed_to_limit(self):
        self.assertEqual(len(clean_payload('shopassist', {'message': 'x' * 5000})['message']), 400)

    def test_choice_must_be_listed(self):
        with self.assertRaises(InvalidInput):
            clean_payload('insightdesk', {'dataset': 'other', 'message': 'q'})

    def test_number_range(self):
        with self.assertRaises(InvalidInput):
            clean_payload('forecastboard', {'dataset': 'retail-sales', 'weeks': 99})

    def test_unknown_project(self):
        with self.assertRaises(InvalidInput):
            clean_payload('nope', {'message': 'hi'})


@override_settings(HEROS_API_URL='https://hero.example/api/v1', HEROS_API_KEYS=['k1', 'k2'],
                   HEROS_MODEL='baymax-4.5', HEROS_API_TIMEOUT=1)
class HeroClientTest(TestCase):
    def setUp(self):
        cache.clear()

    def ok(self, content):
        return httpx.Response(200, json={'choices': [{'message': {'content': content}}]},
                              request=httpx.Request('POST', 'https://hero.example'))

    def fail(self, code=500):
        return httpx.Response(code, request=httpx.Request('POST', 'https://hero.example'))

    def test_sends_openai_style_request_with_first_key(self):
        with mock.patch('httpx.post', return_value=self.ok('{"text": "18 days."}')) as post:
            reply = hero_client.run('documind', {'message': 'How much leave?'})
        self.assertEqual(reply, {'text': '18 days.'})
        url = post.call_args.args[0]
        body = post.call_args.kwargs['json']
        self.assertEqual(url, 'https://hero.example/api/v1/chat/completions')
        self.assertEqual(body['model'], 'baymax-4.5')
        self.assertEqual(body['type'], 'text')
        self.assertIs(body['search'], False)
        self.assertEqual(post.call_args.kwargs['headers']['Authorization'], 'Bearer k1')
        self.assertIn('How much leave?', body['messages'][1]['content'])

    def test_falls_back_to_second_key(self):
        with mock.patch('httpx.post', side_effect=[self.fail(429), self.ok('{"text": "ok"}')]) as post:
            self.assertEqual(hero_client.run('documind', {'message': 'hi'}), {'text': 'ok'})
        self.assertEqual(post.call_args_list[1].kwargs['headers']['Authorization'], 'Bearer k2')

    def test_network_error_also_falls_back(self):
        with mock.patch('httpx.post', side_effect=[httpx.ConnectError('down'), self.ok('plain words')]):
            self.assertEqual(hero_client.run('documind', {'message': 'hi'}), {'text': 'plain words'})

    def test_both_keys_failing_raises_not_connected(self):
        with mock.patch('httpx.post', side_effect=[self.fail(), self.fail()]):
            with self.assertRaises(hero_client.NotConnected):
                hero_client.run('documind', {'message': 'hi'})

    def test_calculation_projects_are_not_sent_to_the_ai(self):
        with mock.patch('httpx.post') as post:
            with self.assertRaises(hero_client.NotConnected):
                hero_client.run('insightdesk', {'dataset': 'retail-sales', 'message': 'q'})
        post.assert_not_called()

    def test_reply_parsing(self):
        fenced = '```json\n{"labels": ["Urgent"], "x": 1}\n```'
        self.assertEqual(hero_client.parse_reply(fenced), {'labels': ['Urgent']})
        self.assertEqual(hero_client.parse_reply('Just text'), {'text': 'Just text'})


class PromptDataTest(TestCase):
    def test_every_ai_project_builds_messages(self):
        from apps.tryit.prompts import BUILDERS, build_messages
        for slug in BUILDERS:
            messages, _ = build_messages(slug, {'message': 'hello', 'page_text': 'Some page.'})
            self.assertEqual(messages[0]['role'], 'system')
            self.assertIn('JSON', messages[0]['content'])


class SandboxTest(TestCase):
    def test_runs_pandas_on_the_real_table(self):
        from apps.tryit.analysis import sandbox
        out = sandbox.run('retail-sales', "result = df.groupby('region').revenue.sum().round(0)")
        self.assertEqual(out['columns'], ['region', 'revenue'])
        self.assertEqual(len(out['rows']), 5)

    def test_row_numbers_are_not_shown_as_a_column(self):
        from apps.tryit.analysis import sandbox
        code = ("result = df.groupby('product', as_index=False)['revenue'].sum()"
                ".sort_values(by='revenue', ascending=False).head(5)")
        self.assertEqual(sandbox.run('retail-sales', code)['columns'], ['product', 'revenue'])

    def test_dangerous_code_is_refused(self):
        from apps.tryit.analysis import sandbox
        for code in ('import os', 'df.to_csv("x.csv")', 'result = df.__class__', 'pd.read_csv("http://x")',
                     'while True:\n    pass', 'result = open("x").read()', 'def f():\n    return 1'):
            with self.subTest(code=code), self.assertRaises(sandbox.SandboxError):
                sandbox.run('retail-sales', code)


@override_settings(HEROS_API_KEYS=[])
class CalculationEngineTest(TestCase):
    """Numbers are calculated even when the AI is unavailable."""

    def test_report_numbers_without_ai(self):
        from apps.tryit import engines
        reply = engines.run('reportbot', {'dataset': 'cafe-orders', 'period': 'last-month'})
        self.assertEqual(reply['table']['rows'][0][0], 'Revenue')
        self.assertIn('not available right now', reply['text'])
        json.dumps(reply)

    def test_forecast_reports_its_error(self):
        from apps.tryit import engines
        reply = engines.run('forecastboard', {'category': 'Fitness', 'weeks': 3})
        self.assertEqual(len(reply['table']['rows']), 3)
        self.assertTrue(any('Backtest error' in label for label in reply['labels']))
        json.dumps(reply)


class BookingTest(TestCase):
    def test_no_double_booking(self):
        from django.utils import timezone
        from apps.tryit import engines
        day = (timezone.localdate() + timezone.timedelta(days=3)).isoformat()
        slot = engines.run('bookit', {'action': 'slots', 'resource': 'turf-b', 'date': day})['items'][0]['slot']
        engines.run('bookit', {'action': 'book', 'resource': 'turf-b', 'date': day, 'slot': slot, 'name': 'A'})
        with self.assertRaises(engines.UserError):
            engines.run('bookit', {'action': 'book', 'resource': 'turf-b', 'date': day, 'slot': slot, 'name': 'B'})

    def test_dates_are_limited(self):
        from django.utils import timezone
        from apps.tryit import engines
        for days in (-1, 30):
            day = (timezone.localdate() + timezone.timedelta(days=days)).isoformat()
            with self.assertRaises(engines.UserError):
                engines.run('bookit', {'action': 'slots', 'resource': 'turf-a', 'date': day})


class InsightFlowTest(TestCase):
    def test_code_runs_and_is_explained(self):
        from apps.tryit import engines
        replies = ["```python\nresult = df.groupby('region').revenue.sum().sort_values(ascending=False).round(0)\n```",
                   '{"text": "Online sold the most."}']
        with mock.patch.object(hero_client, 'chat', side_effect=replies):
            reply = engines.run('insightdesk', {'dataset': 'retail-sales', 'message': 'Which region sold the most?'})
        self.assertEqual(reply['text'], 'Online sold the most.')
        self.assertEqual(reply['table']['rows'][0][0], 'Online')
        self.assertIn('groupby', reply['code'])

    def test_bad_code_gets_one_retry(self):
        from apps.tryit import engines
        replies = ['```python\nimport os\n```', '```python\nresult = df.revenue.sum()\n```', '{"text": "Total revenue."}']
        with mock.patch.object(hero_client, 'chat', side_effect=replies):
            reply = engines.run('insightdesk', {'dataset': 'retail-sales', 'message': 'Total revenue?'})
        self.assertEqual(reply['table']['columns'], ['result'])


class CannotAnswerTest(TestCase):
    def test_ai_can_say_the_table_cannot_answer(self):
        from apps.tryit import engines
        refusal = 'CANNOT: there is no customer age in this table | TRY: revenue by region last month'
        with mock.patch.object(hero_client, 'chat', return_value=refusal) as chat:
            reply = engines.run('insightdesk', {'dataset': 'retail-sales', 'message': 'Which age group buys most?'})
        self.assertIn("This data can't answer that: there is no customer age", reply['text'])
        self.assertIn('revenue by region last month', reply['text'])
        self.assertEqual(chat.call_count, 1)  # no code was run and no explanation call was needed

    def test_retail_data_has_profit(self):
        from apps.tryit.analysis import datasets
        self.assertIn('profit', datasets.schema('retail-sales'))


# Tests never touch the real Pinecone index: RAG is off unless a test turns it on with a fake response.
_no_pinecone = override_settings(PINECONE_API_KEY='', GEMINI_API_KEYS=[])  # and no real Gemini calls


def setUpModule():
    _no_pinecone.enable()


def tearDownModule():
    _no_pinecone.disable()


@override_settings(PINECONE_API_KEY='test-key', PINECONE_INDEX='test-index')
class RagTest(TestCase):
    def setUp(self):
        from apps.tryit import rag
        rag.host.cache_clear()
        self.rag = rag

    def fake(self, matches):
        def post(url, **kwargs):
            return httpx.Response(200, json={'matches': matches}, request=httpx.Request('POST', url))
        return post

    def test_search_sends_text_query_to_documents_api(self):
        matches = [{'_id': 'documind-0003', '_score': 0.44, 'title': '4. Annual leave', 'chunk_text': '18 days a year.'}]
        with mock.patch.object(self.rag, 'host', return_value='https://idx.example'), \
                mock.patch('httpx.post', side_effect=self.fake(matches)) as post:
            hits = self.rag.search('documind', 'How much leave?')
        self.assertEqual(hits, [{'text': '18 days a year.', 'source': '4. Annual leave', 'score': 0.44}])
        url = post.call_args.args[0]
        body = post.call_args.kwargs['json']
        self.assertEqual(url, 'https://idx.example/namespaces/documind/documents/search')
        self.assertEqual(body['score_by'][0], {'type': 'embed', 'fields': ['chunk_text'], 'query': 'How much leave?'})
        self.assertEqual(post.call_args.kwargs['headers']['X-Pinecone-Api-Version'], '2026-07')

    def test_prompt_uses_only_retrieved_chunks(self):
        from apps.tryit.prompts import build_messages
        matches = [{'_id': 'a', '_score': 0.5, 'title': 'Leave', 'chunk_text': 'UNIQUE-CHUNK-TEXT'}]
        with mock.patch.object(self.rag, 'host', return_value='https://idx.example'), \
                mock.patch('httpx.post', side_effect=self.fake(matches)):
            messages, _ = build_messages('documind', {'message': 'leave?'})
        self.assertIn('UNIQUE-CHUNK-TEXT', messages[1]['content'])
        self.assertNotIn('Northwind Supplies', messages[1]['content'].replace('UNIQUE-CHUNK-TEXT', ''))

    def test_falls_back_to_whole_file_when_pinecone_fails(self):
        from apps.tryit.prompts import build_messages
        with mock.patch.object(self.rag, 'host', return_value='https://idx.example'), \
                mock.patch('httpx.post', side_effect=httpx.ConnectError('down')):
            messages, _ = build_messages('documind', {'message': 'leave?'})
        self.assertIn('Annual leave', messages[1]['content'])

    def test_every_rag_source_builds_chunks(self):
        for project, build in self.rag.SOURCES.items():
            with self.subTest(project=project):
                chunks = build()
                self.assertTrue(chunks)
                self.assertTrue(all(c['text'] and c['source'] for c in chunks))



@override_settings(HEROS_API_URL='https://hero.example/api/v1', HEROS_API_KEYS=['h1', 'h2', 'h3'],
                   GEMINI_API_KEYS=['g1', 'g2'], GEMINI_MODEL='gemini-test', HEROS_API_TIMEOUT=1, GEMINI_API_TIMEOUT=1)
class ProviderChainTest(TestCase):
    def setUp(self):
        cache.clear()

    def test_order_alternates_hero_and_gemini(self):
        order = [(p, n) for p, n, _ in hero_client.provider_chain()]
        self.assertEqual(order, [('gemini', 1), ('hero', 1), ('gemini', 2), ('hero', 2), ('hero', 3)])

    def test_falls_through_the_whole_chain_in_order(self):
        calls = []

        def post(url, **kwargs):
            headers = kwargs['headers']
            calls.append(headers.get('Authorization') or headers.get('x-goog-api-key'))
            if len(calls) < 5:
                return httpx.Response(503, request=httpx.Request('POST', url))
            return httpx.Response(200, json={'choices': [{'message': {'content': 'last one'}}]},
                                  request=httpx.Request('POST', url))
        with mock.patch('httpx.post', side_effect=post):
            self.assertEqual(hero_client.chat([{'role': 'user', 'content': 'hi'}]), 'last one')
        self.assertEqual(calls, ['g1', 'Bearer h1', 'g2', 'Bearer h2', 'Bearer h3'])

    def test_gemini_request_and_reply_format(self):
        def post(url, **kwargs):
            return httpx.Response(200, json={'candidates': [{'content': {'parts': [{'text': '{"text": "from gemini"}'}]}}]},
                                  request=httpx.Request('POST', url))
        messages = [{'role': 'system', 'content': 'RULES'}, {'role': 'user', 'content': 'Q1'},
                    {'role': 'assistant', 'content': 'A1'}, {'role': 'user', 'content': 'Q2'}]
        with mock.patch('httpx.post', side_effect=post) as p:
            self.assertEqual(hero_client.chat(messages, temperature=0.1), '{"text": "from gemini"}')
        url, kwargs = p.call_args.args[0], p.call_args.kwargs
        self.assertIn('/models/gemini-test:generateContent', url)
        self.assertEqual(kwargs['json']['systemInstruction'], {'parts': [{'text': 'RULES'}]})
        self.assertEqual([c['role'] for c in kwargs['json']['contents']], ['user', 'model', 'user'])
        self.assertEqual(kwargs['json']['generationConfig']['temperature'], 0.1)

    def test_a_key_over_its_limit_rests_at_the_end_of_the_chain(self):
        calls = []

        def post(url, **kwargs):
            headers = kwargs['headers']
            calls.append(headers.get('Authorization') or headers.get('x-goog-api-key'))
            if calls[-1] == 'g1':
                return httpx.Response(429, request=httpx.Request('POST', url))
            return httpx.Response(200, json={'choices': [{'message': {'content': 'ok'}}]},
                                  request=httpx.Request('POST', url))
        with mock.patch('httpx.post', side_effect=post):
            hero_client.chat([{'role': 'user', 'content': 'first'}])
            calls.clear()
            hero_client.chat([{'role': 'user', 'content': 'second'}])
        self.assertEqual(calls, ['Bearer h1'])  # g1 is resting, so the second question skips straight past it
        self.assertEqual([p for p, n, _ in hero_client.ordered_chain()][-1], 'gemini')

    def test_all_failing_raises_not_connected(self):
        with mock.patch('httpx.post', side_effect=httpx.ConnectError('down')):
            with self.assertRaises(hero_client.NotConnected):
                hero_client.chat([{'role': 'user', 'content': 'hi'}])


class OutputGuardTest(TestCase):
    def test_shopassist_drops_invented_and_out_of_stock_products(self):
        from apps.tryit.prompts import catalog_names, guard
        real = next(r for r in catalog_names().values() if r['availability'] == 'In stock')
        gone = next(r for r in catalog_names().values() if r['availability'] == 'Out of stock')
        reply = guard('shopassist', {'text': 't', 'items': [
            {'title': real['name'].upper(), 'meta': 'wrong price'},
            {'title': 'Imaginary Jacket 3000', 'meta': '1 USD'},
            {'title': gone['name'], 'meta': ''}]})
        self.assertEqual([i['title'] for i in reply['items']], [real['name']])
        self.assertIn(real['availability'], reply['items'][0]['meta'])

    def test_supportflow_labels_are_always_valid(self):
        from apps.tryit.prompts import DRAFT_NOTE, guard
        reply = guard('supportflow', {'labels': ['urgent', 'Refunds please'], 'text': 'Hello'})
        self.assertEqual(reply['labels'], ['Other', 'Urgent'])
        self.assertTrue(reply['text'].endswith(DRAFT_NOTE))

    def test_deskpilot_blocks_unsafe_steps_and_forces_approval(self):
        from apps.tryit.prompts import guard
        reply = guard('deskpilot', {'text': 'Plan.', 'steps': [
            {'text': 'list_files: list invoices', 'needs_approval': False},
            {'text': 'rename_file: rename each invoice', 'needs_approval': False},
            {'text': 'delete_file: delete the old copies', 'needs_approval': True},
            {'text': 'move_file: delete originals after moving', 'needs_approval': True},
            {'text': 'copy_file: copy to backup (do not delete the original)', 'needs_approval': False}]})
        self.assertEqual([s['text'].split(':')[0] for s in reply['steps']], ['list_files', 'rename_file', 'copy_file'])
        self.assertEqual([s['needs_approval'] for s in reply['steps']], [False, True, True])
        self.assertTrue(reply['text'].startswith('This is a plan; nothing has been run.'))


class ParseReplyTest(TestCase):
    def test_text_before_json_is_ignored(self):
        content = 'You can carry over 5 days.\n{"text": "You can carry over 5 days.", "source": "Section 4"}'
        self.assertEqual(hero_client.parse_reply(content), {'text': 'You can carry over 5 days.', 'source': 'Section 4'})

    def test_null_values_are_dropped(self):
        self.assertEqual(hero_client.parse_reply('{"text": "Hi", "source": null}'), {'text': 'Hi'})

    def test_braces_inside_strings(self):
        self.assertEqual(hero_client.parse_reply('```json\n{"text": "use {curly} braces"}\n```'), {'text': 'use {curly} braces'})


@override_settings(AI_DAILY_CAP=2, HEROS_API_URL='https://hero.example/api/v1', HEROS_API_KEYS=['h1'],
                   GEMINI_API_KEYS=[], HEROS_API_TIMEOUT=1)
class DailyCapTest(TestCase):
    def ok(self, content='{"text": "fine"}'):
        return httpx.Response(200, json={'choices': [{'message': {'content': content}}]},
                              request=httpx.Request('POST', 'https://hero.example'))

    def test_cap_stops_calls_after_the_limit(self):
        from apps.tryit import usage
        with mock.patch('httpx.post', return_value=self.ok()) as post:
            hero_client.chat([{'role': 'user', 'content': 'a'}])
            hero_client.chat([{'role': 'user', 'content': 'b'}])
            with self.assertRaises(hero_client.DailyCapReached):
                hero_client.chat([{'role': 'user', 'content': 'c'}])
        self.assertEqual(post.call_count, 2)          # the third call never reached the AI
        self.assertEqual(usage.calls_today(), 2)

    def test_fallback_keys_count_once(self):
        from apps.tryit import usage
        failing = httpx.Response(503, request=httpx.Request('POST', 'https://hero.example'))
        with override_settings(HEROS_API_KEYS=['h1', 'h2']), mock.patch('httpx.post', side_effect=[failing, self.ok()]):
            hero_client.chat([{'role': 'user', 'content': 'a'}])
        self.assertEqual(usage.calls_today(), 1)

    def test_visitor_sees_a_clear_message(self):
        from apps.tryit.models import AiUsage
        from django.utils import timezone
        AiUsage.objects.create(day=timezone.now().date(), calls=2)
        with mock.patch('apps.tryit.views.Project.objects.public') as public:
            public.return_value.filter.return_value.exists.return_value = True
            res = self.client.post(reverse('try_api', args=['documind']), data=json.dumps({'message': 'hi'}),
                                   content_type='application/json')
        self.assertEqual(res.status_code, 429)
        self.assertIn('limit for today', res.json()['error'])

    def test_report_still_shows_numbers_when_the_cap_is_reached(self):
        from apps.tryit import engines
        from apps.tryit.models import AiUsage
        from django.utils import timezone
        AiUsage.objects.create(day=timezone.now().date(), calls=2)
        reply = engines.run('reportbot', {'dataset': 'cafe-orders', 'period': 'last-month'})
        self.assertEqual(reply['table']['rows'][0][0], 'Revenue')

    @override_settings(AI_DAILY_CAP=0)
    def test_zero_means_no_limit(self):
        from apps.tryit import usage
        with mock.patch('httpx.post', return_value=self.ok()):
            for _ in range(5):
                hero_client.chat([{'role': 'user', 'content': 'x'}])
        self.assertEqual(usage.calls_today(), 0)
