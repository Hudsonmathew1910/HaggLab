"""
The single connection between the website and the AI providers: Hero's AI and Google Gemini.

Every Try it page posts to /api/try/<slug>/, which calls run(). Nothing else calls an AI,
so this is the only file to change if an API's address, keys or format change.

Fallback order (provider_chain): the providers take turns, key by key, until one answers:
    Gemini key 1 -> Hero's AI key 1 -> Gemini key 2 -> Hero's AI key 2 -> Hero's AI key 3
Gemini goes first because it answers in a few seconds; Hero's AI needs 25-40 seconds.
A key that is over its limit (HTTP 429), down (5xx) or too slow rests for REST_SECONDS: it moves to the end
of the chain, so the next questions don't wait for it first.

Hero's AI:  POST {HEROS_API_URL}/chat/completions   (OpenAI-style)
            Authorization: Bearer <key>
            {"model": HEROS_MODEL, "messages": [...], "temperature": ..., "type": "text", "search": false}
            reply: choices[0].message.content
Gemini:     POST https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent
            x-goog-api-key: <key>
            {"systemInstruction": {...}, "contents": [...], "generationConfig": {"temperature": ...}}
            reply: candidates[0].content.parts[].text
"""
import json
import logging
import re
import time
from itertools import zip_longest

import httpx
from django.conf import settings
from django.core.cache import cache

from . import trace, usage
from .prompts import NotReady, build_messages, guard

logger = logging.getLogger(__name__)

# Keys the Try it page knows how to show (see static/js/try.js)
REPLY_KEYS = ('text', 'source', 'labels', 'items', 'table', 'steps')

GEMINI_URL = 'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'

REST_SECONDS = 120


class NotConnected(Exception):
    """No AI provider is configured, or every key of every provider failed."""


class DailyCapReached(NotConnected):
    """The site-wide daily AI limit is used up. Subclass of NotConnected, so tools that can work without the AI
    (ReportBot, ForecastBoard) simply show their numbers without the written summary."""


def provider_chain():
    """[(provider, key number, key), ...] in fallback order: Gemini 1, Hero 1, Gemini 2, Hero 2, Hero 3."""
    heros = [('hero', n, k) for n, k in enumerate(settings.HEROS_API_KEYS, 1)] if settings.HEROS_API_URL else []
    geminis = [('gemini', n, k) for n, k in enumerate(getattr(settings, 'GEMINI_API_KEYS', []), 1)]
    return [step for pair in zip_longest(geminis, heros) for step in pair if step]


def rest_key(provider, number):
    return f'ai-rest:{provider}:{number}'


def ordered_chain():
    """provider_chain() with resting keys moved to the end (they are still tried if nothing else answers)."""
    chain = provider_chain()
    resting = cache.get_many([rest_key(p, n) for p, n, _ in chain])
    return ([step for step in chain if rest_key(*step[:2]) not in resting]
            + [step for step in chain if rest_key(*step[:2]) in resting])


def is_configured():
    return bool(provider_chain())


def call_hero(key, messages, temperature):
    res = httpx.post(
        settings.HEROS_API_URL.rstrip('/') + '/chat/completions',
        json={'model': settings.HEROS_MODEL, 'messages': messages, 'temperature': temperature,
              'type': 'text', 'search': False},
        headers={'Authorization': f'Bearer {key}'},
        timeout=settings.HEROS_API_TIMEOUT,
    )
    res.raise_for_status()
    return res.json()['choices'][0]['message']['content']


def call_gemini(key, messages, temperature):
    """Gemini has no chat roles list: system text goes to systemInstruction, assistant turns become 'model'."""
    system = '\n\n'.join(m['content'] for m in messages if m['role'] == 'system')
    contents = [{'role': 'model' if m['role'] == 'assistant' else 'user', 'parts': [{'text': m['content']}]}
                for m in messages if m['role'] != 'system']
    body = {'contents': contents, 'generationConfig': {'temperature': temperature}}
    if system:
        body['systemInstruction'] = {'parts': [{'text': system}]}
    res = httpx.post(GEMINI_URL.format(model=settings.GEMINI_MODEL), json=body,
                     headers={'x-goog-api-key': key}, timeout=settings.GEMINI_API_TIMEOUT)
    res.raise_for_status()
    parts = res.json()['candidates'][0]['content']['parts']
    text = ''.join(p.get('text', '') for p in parts if not p.get('thought'))
    if not text.strip():
        raise ValueError('empty Gemini reply')
    return text


PROVIDERS = {
    'hero': ("Hero's AI", call_hero),
    'gemini': ('Gemini', call_gemini),
}


def chat(messages, temperature=0.3):
    """Send a chat to the first provider that answers and return the reply text."""
    chain = ordered_chain()
    if not chain:
        raise NotConnected('not configured')
    try:
        usage.take_one()
    except usage.DailyCapReached as exc:
        trace.show(f'   Daily AI limit reached ({exc}); no AI call made')
        raise DailyCapReached(str(exc)) from exc
    trace.ai_request(messages, len(chain))
    for position, (provider, number, key) in enumerate(chain, 1):
        name, call = PROVIDERS[provider]
        label = f'{name} key {number}'
        model = settings.GEMINI_MODEL if provider == 'gemini' else settings.HEROS_MODEL
        next_step = 'trying the next one' if position < len(chain) else 'nothing left to try'
        started = time.perf_counter()
        try:
            content = call(key, messages, temperature)
        except httpx.HTTPStatusError as exc:
            trace.ai_attempt(label, model, time.perf_counter() - started, f'FAILED (HTTP {exc.response.status_code})', next_step)
            logger.warning('%s failed with HTTP %s', label, exc.response.status_code)
            if exc.response.status_code == 429 or exc.response.status_code >= 500:
                cache.set(rest_key(provider, number), True, REST_SECONDS)
            continue
        except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError) as exc:
            if isinstance(exc, (httpx.TimeoutException, httpx.ConnectError)):
                cache.set(rest_key(provider, number), True, REST_SECONDS)
            trace.ai_attempt(label, model, time.perf_counter() - started, f'FAILED ({type(exc).__name__})', next_step)
            logger.warning('%s failed: %s', label, type(exc).__name__)
            continue
        trace.ai_attempt(label, model, time.perf_counter() - started, 'OK')
        trace.ai_reply(content)
        return content
    raise NotConnected('all providers failed')


def find_json_object(text):
    """The reply's JSON object, even when the model adds a fence or a sentence around it. None if there is none."""
    fenced = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.S)
    candidates = [fenced.group(1)] if fenced else []
    candidates.append(text)
    decoder = json.JSONDecoder()
    for candidate in candidates:
        for start in [i for i, ch in enumerate(candidate) if ch == '{']:
            try:
                data, _ = decoder.raw_decode(candidate[start:])
            except ValueError:
                continue
            if isinstance(data, dict) and any(key in data for key in REPLY_KEYS):
                return data
    return None


def parse_reply(content):
    """Turn the model's answer into the Try it reply shape. JSON is expected; plain text still works."""
    text = (content or '').strip()
    data = find_json_object(text)
    if data is None:
        return {'text': text}
    # Drop empty values (for example "source": null) so the page never shows "None"
    return {key: data[key] for key in REPLY_KEYS if data.get(key) not in (None, '', [])} or {'text': text}


def run(slug, payload):
    """Answer one Try it request for a project."""
    try:
        messages, temperature = build_messages(slug, payload)
    except NotReady as exc:
        raise NotConnected('project needs calculation code') from exc
    trace.show('2. Prompt built: project instructions + the relevant data (Pinecone chunks, or the whole file)')
    reply = guard(slug, parse_reply(chat(messages, temperature)))
    trace.show('3. AI reply turned into page fields', list(reply))
    return reply
