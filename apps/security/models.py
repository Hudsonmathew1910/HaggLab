from django.db import models
from django.conf import settings

class AuditEvent(models.Model):
    """
    Read-only audit event log for sensitive actions:
    Admin login, failed login, object creation, modification, deletion, export.
    IP is truncated/anonymized to protect visitor privacy.
    """
    timestamp = models.DateTimeField(auto_now_add=True)
    actor = models.CharField(max_length=150, default='anonymous')
    action = models.CharField(max_length=100)
    object_repr = models.CharField(max_length=255, blank=True)
    ip_address = models.CharField(max_length=45, blank=True)
    details = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Audit Event'
        verbose_name_plural = 'Audit Events'

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {self.actor} - {self.action}: {self.object_repr}"
