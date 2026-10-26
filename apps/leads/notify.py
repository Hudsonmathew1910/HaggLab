"""
Email the owner about a new inquiry. The inquiry is always saved in the admin first, so a failed email never
loses a lead; the failure is logged instead of hidden.
"""
import logging

from django.conf import settings
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)


def email_configured():
    return bool(settings.EMAIL_HOST and settings.EMAIL_HOST_USER and settings.OWNER_EMAIL)


def notify_owner(inquiry):
    """Send the new-inquiry email. Returns True when it was sent."""
    if not email_configured():
        logger.warning('Inquiry %s saved, but email is not configured (EMAIL_HOST, EMAIL_HOST_USER, OWNER_EMAIL).',
                       inquiry.pk)
        return False
    lines = [
        f'Name: {inquiry.name}',
        f'Email: {inquiry.email}',
        f'Business: {inquiry.business or "-"}',
        f'Service: {inquiry.get_service_display()}',
        f'Data available: {inquiry.get_data_available_display()}',
        f'Timeline: {inquiry.get_timeline_display()}',
        f'Budget: {inquiry.budget_band or "-"}',
        f'How they found us: {inquiry.source or "-"}',
        '',
        'Problem:',
        inquiry.problem,
        '',
        f'Reply to this email to answer {inquiry.name} directly.',
        f'All inquiries: {settings.SITE_URL.rstrip("/")}/{settings.ADMIN_URL_PATH}leads/inquiry/',
    ]
    message = EmailMessage(
        subject=f'[HaggLab] New project inquiry: {inquiry.name} ({inquiry.get_service_display()})',
        body='\n'.join(lines),
        to=[settings.OWNER_EMAIL],
        reply_to=[inquiry.email],
    )
    try:
        message.send(fail_silently=False)
    except Exception:
        logger.exception('Inquiry %s saved, but the notification email could not be sent.', inquiry.pk)
        return False
    return True
