import json
import logging

from django.conf import settings
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from apps.content.gigs import gig_for
from apps.content.models import Project

from . import engines, hero_client, trace
from .specs import SPECS, InvalidInput, clean_payload

logger = logging.getLogger(__name__)

# Only these reply keys are passed on to the browser
REPLY_KEYS = ('text', 'source', 'labels', 'items', 'table', 'steps', 'code')


def try_rate(group, request):
    return settings.TRY_RATE


def try_view(request, slug):
    project = get_object_or_404(Project.objects.public(), slug=slug)
    spec = SPECS.get(slug)
    if not spec:
        raise Http404
    return render(request, 'pages/try.html', {
        'project': project,
        'spec': spec,
        'tools': [p for p in Project.objects.public().order_by('order') if p.slug in SPECS],
        'gig': gig_for(project),
    })


@require_POST
@ratelimit(key='ip', rate=try_rate, method='POST', block=False)
def try_api(request, slug):
    if not Project.objects.public().filter(slug=slug).exists():
        return JsonResponse({'ok': False, 'error': 'This tool is not available.'}, status=404)
    if getattr(request, 'limited', False):
        return JsonResponse(
            {'ok': False, 'error': 'You have reached the limit of tries for now. Please try again in an hour.'},
            status=429)
    try:
        data = json.loads(request.body or b'{}')
        payload = clean_payload(slug, data if isinstance(data, dict) else {})
    except InvalidInput as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=400)
    except ValueError:
        return JsonResponse({'ok': False, 'error': 'Please check your input and try again.'}, status=400)
    started = trace.start(slug, payload)
    try:
        reply = engines.run(slug, payload)
    except engines.UserError as exc:
        trace.end(started, f'refused: {exc}')
        return JsonResponse({'ok': False, 'error': str(exc)}, status=400)
    except hero_client.DailyCapReached:
        trace.end(started, 'daily AI limit reached')
        return JsonResponse({'ok': False, 'error': 'Our AI tools have reached their limit for today. '
                             'Please try again tomorrow, or send us your project details.'}, status=429)
    except hero_client.NotConnected as exc:
        trace.end(started, f"busy (Hero's AI unavailable: {exc})")
        return JsonResponse(
            {'ok': False, 'error': 'This tool is busy right now. Please try again in a few minutes.'}, status=503)
    except MemoryError:
        logger.exception('Try it %s ran out of memory', slug)
        return JsonResponse({'ok': False, 'error': 'The server is short of memory right now. Please try again shortly.'}, status=503)
    except Exception:  # never show a broken page; the full error goes to the server log
        logger.exception('Try it %s failed', slug)
        return JsonResponse({'ok': False, 'error': 'Something went wrong on our side (error 500). Please try again.'}, status=500)
    out = {key: reply[key] for key in REPLY_KEYS if key in reply}
    trace.end(started, 'OK', out)
    return JsonResponse({'ok': True, **out})
