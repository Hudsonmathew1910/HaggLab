from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand, CommandError

from apps.leads.notify import email_configured


class Command(BaseCommand):
    help = 'Send a test email to OWNER_EMAIL using the EMAIL_* settings, to check new-inquiry alerts will arrive.'

    def handle(self, *args, **options):
        if not email_configured():
            raise CommandError('Email is not configured. Set EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD and OWNER_EMAIL.')
        try:
            EmailMessage(
                subject='[HaggLab] Test email: inquiry alerts work',
                body='If you can read this, new project inquiries from the website will reach this inbox.',
                to=[settings.OWNER_EMAIL],
            ).send(fail_silently=False)
        except Exception as exc:
            raise CommandError(f'Sending failed: {type(exc).__name__}: {exc}')
        self.stdout.write(self.style.SUCCESS(f'Test email sent from {settings.EMAIL_HOST_USER} to {settings.OWNER_EMAIL}.'))
