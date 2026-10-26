from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import AuditEvent

def get_client_ip(request):
    if not request:
        return ''
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    # Truncate / mask last octet for privacy
    if '.' in ip:
        parts = ip.split('.')
        return f"{parts[0]}.{parts[1]}.{parts[2]}.0"
    return ip

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    AuditEvent.objects.create(
        actor=user.username,
        action='LOGIN_SUCCESS',
        object_repr='User Session',
        ip_address=get_client_ip(request),
        details='Staff user logged in successfully.'
    )

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    username = credentials.get('username', 'unknown')
    AuditEvent.objects.create(
        actor=username,
        action='LOGIN_FAILED',
        object_repr='Authentication',
        ip_address=get_client_ip(request),
        details='Failed login attempt.'
    )
