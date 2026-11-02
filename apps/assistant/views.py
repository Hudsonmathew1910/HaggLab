"""
Haggi's API, used by static/js/assistant.js.

GET  /api/assistant/            -> {"ok": true, "messages": [...]}  the conversation so far (restores the chat)
POST /api/assistant/ {"message": "...", "page": "/current/path/"}  -> {"ok": true, "text": "...", "links": [...]}
POST /api/assistant/ {"reset": true}                                -> starts a new conversation

The conversation lives in the visitor's session only (last few turns), so nothing they type is stored in the database.
"""
import json
import logging

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit

from apps.core.fiverr import fiverr_enabled
from apps.tryit import hero_client

from . import assistant

logger = logging.getLogger(__name__)

KEEP = assistant.HISTORY_TURNS * 2


def assistant_rate(group, request):
    return settings.ASSISTANT_RATE


def enabled():
    from apps.content.models import SiteSetting
    value = SiteSetting.objects.filter(key='assistant_enabled').values_list('value', flat=True).first()
    return (value or 'on').strip().lower() not in ('off', 'no', 'false', '0')


def is_fiverr(request):
    return fiverr_enabled() and bool(getattr(request, 'is_fiverr', False) or request.session.get('is_fiverr'))


@require_http_methods(['GET', 'POST'])
@ratelimit(key='ip', rate=assistant_rate, method='POST', block=False)
def assistant_api(request):
    if not enabled():
        return JsonResponse({'ok': False, 'error': 'The assistant is switched off.'}, status=404)
    history = request.session.get(assistant.SESSION_KEY, [])

    if request.method == 'GET':
        # The chat just opened: build the knowledge now, so the visitor's first question is fast
        try:
            from . import search
            search.search('warm up', top=1)
        except Exception:
            logger.exception('Haggi warm-up failed')
        return JsonResponse({'ok': True, 'messages': history})

    if getattr(request, 'limited', False):
        return JsonResponse({'ok': False, 'error': 'You have sent a lot of messages. Please try again in an hour.'},
                            status=429)
    try:
        data = json.loads(request.body or b'{}')
        if not isinstance(data, dict):
            raise ValueError
    except ValueError:
        return JsonResponse({'ok': False, 'error': 'Please try again.'}, status=400)

    if data.get('reset'):
        request.session[assistant.SESSION_KEY] = []
        return JsonResponse({'ok': True, 'messages': []})

    message = data.get('message') if isinstance(data.get('message'), str) else ''
    try:
        reply = assistant.answer(message, history, page=data.get('page', ''), is_fiverr=is_fiverr(request))
    except assistant.AssistantError as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=400)
    except hero_client.DailyCapReached:
        return JsonResponse({'ok': False, 'error': 'I have answered a lot of questions today and need a rest. '
                             'Please try again tomorrow, or send us your project details.'}, status=429)
    except hero_client.NotConnected:
        return JsonResponse({'ok': False, 'error': 'I am busy right now. Please try again in a minute.'}, status=503)
    except Exception:  # never break the page; the details go to the server log
        logger.exception('Haggi failed')
        return JsonResponse({'ok': False, 'error': 'Something went wrong on our side. Please try again.'}, status=500)

    history = (history + [{'role': 'user', 'content': message.strip()},
                          {'role': 'assistant', 'content': reply['text'], 'links': reply['links']}])[-KEEP:]
    request.session[assistant.SESSION_KEY] = history
    return JsonResponse({'ok': True, **reply})
