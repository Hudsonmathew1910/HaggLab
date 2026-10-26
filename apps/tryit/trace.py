"""
Step-by-step trace of a Try it request, printed to the runserver terminal.

AI_TRACE = True        one line per step (on in dev.py, off in production)
AI_TRACE_DETAIL = True also print the prompts, AI replies and results under each step
Never prints API keys. Plain ASCII only, so any Windows terminal can show it.
"""
import json
import time

from django.conf import settings

LINE = '-' * 72


def enabled():
    return getattr(settings, 'AI_TRACE', False)


def detailed():
    return enabled() and getattr(settings, 'AI_TRACE_DETAIL', False)


def short(value, limit=600):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, default=str)
    return text if len(text) <= limit else f'{text[:limit]} ... [+{len(text) - limit:,} more characters]'


def out(text):
    """Print one line. Never lets a terminal encoding problem break a request."""
    try:
        print(text, flush=True)
    except (UnicodeEncodeError, OSError):
        try:
            print(text.encode('ascii', 'replace').decode('ascii'), flush=True)
        except (UnicodeEncodeError, OSError):
            pass


def show(title, body=None):
    """One line for the step; the body is printed only in detail mode."""
    if not enabled():
        return
    out(f'> {title}')
    if body is not None and detailed():
        for line in short(body).splitlines() or ['']:
            out(f'      {line}')


def start(slug, payload):
    if not enabled():
        return 0.0
    out(f'\n{LINE}\nTRY IT | {slug}')
    show('1. Visitor input received and checked', payload)
    return time.perf_counter()


def end(started, outcome, reply=None):
    if not enabled():
        return
    show(f'Done | {outcome} | total {time.perf_counter() - started:.1f}s', reply)
    out(LINE)


def ai_request(messages, providers):
    if not enabled():
        return
    tokens = sum(len(m['content']) for m in messages) // 4
    show(f'   Calling the AI (~{tokens:,} tokens, {providers} provider keys in the fallback chain)')
    if detailed():
        for m in messages:
            show(f"      [{m['role']}]", m['content'])


def ai_attempt(label, model, seconds, status, detail=''):
    show(f'   {label} ({model}): {status} in {seconds:.1f}s{" -> " + detail if detail else ""}')


def ai_reply(content):
    if detailed():
        show('      AI raw reply', content)
