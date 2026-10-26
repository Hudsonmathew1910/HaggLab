"""
Site-wide daily cap on AI calls (setting AI_DAILY_CAP; 0 = no cap).

Each call to an AI provider counts once, however many keys the fallback chain tries. The count is per UTC day
and lives in the database (AiUsage), so all server processes share it.
"""
from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import F
from django.utils import timezone

from .models import AiUsage


class DailyCapReached(Exception):
    """The site has used its AI calls for today."""


def cap():
    return int(getattr(settings, 'AI_DAILY_CAP', 0) or 0)


def calls_today():
    row = AiUsage.objects.filter(day=timezone.now().date()).first()
    return row.calls if row else 0


def take_one():
    """Reserve one AI call for today, or raise DailyCapReached. Does nothing when there is no cap."""
    limit = cap()
    if limit <= 0:
        return
    today = timezone.now().date()
    try:
        with transaction.atomic():
            AiUsage.objects.get_or_create(day=today)
    except IntegrityError:  # another process created today's row at the same moment
        pass
    # Increase only while under the limit, in one database statement, so two visitors cannot both take the last call
    updated = AiUsage.objects.filter(day=today, calls__lt=limit).update(calls=F('calls') + 1)
    if not updated:
        raise DailyCapReached(f'{limit} AI calls used today')
