import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit
from .models import AnalyticsEvent

VALID_EVENTS = {
    'project_view',
    'demo_start',
    'demo_complete',
    'fiverr_click',
    'form_start',
    'form_submit',
    'cta_click',
}

@csrf_exempt
@ratelimit(key='ip', rate='30/m', block=True)
@require_POST
def record_event_view(request):

    """
    Lightweight, rate-limited endpoint for client-side first-party event tracking.
    Same-origin only. Truncates IP address for user privacy.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    event_name = data.get('event', '').strip()
    if event_name not in VALID_EVENTS:
        return HttpResponseBadRequest("Invalid event type")

    path = data.get('path', '')[:255]
    target = data.get('target', '')[:150]

    # Anonymize IP (keep only network prefix)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        raw_ip = x_forwarded_for.split(',')[0].strip()
    else:
        raw_ip = request.META.get('REMOTE_ADDR', '')

    if '.' in raw_ip:
        parts = raw_ip.split('.')
        ip_prefix = f"{parts[0]}.{parts[1]}.{parts[2]}.0"
    else:
        ip_prefix = raw_ip[:16]

    AnalyticsEvent.objects.create(
        event_name=event_name,
        path=path,
        target=target,
        ip_prefix=ip_prefix
    )

    return JsonResponse({'status': 'recorded'})
