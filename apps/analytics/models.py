from django.db import models

class AnalyticsEvent(models.Model):
    """
    First-party, privacy-preserving analytics event.
    No cookies, no full IP, no user identifiers.
    Tracks only key site engagement events from Development.md section 7:
    - project_view
    - demo_start
    - demo_complete
    - fiverr_click
    - form_start
    - form_submit
    - cta_click
    """
    EVENT_CHOICES = [
        ('project_view', 'Project View'),
        ('demo_start', 'Demo Start'),
        ('demo_complete', 'Demo Complete'),
        ('fiverr_click', 'Fiverr Click'),
        ('form_start', 'Form Start'),
        ('form_submit', 'Form Submit'),
        ('cta_click', 'CTA Click'),
    ]

    timestamp = models.DateTimeField(auto_now_add=True)
    event_name = models.CharField(max_length=50, choices=EVENT_CHOICES)
    path = models.CharField(max_length=255, blank=True)
    target = models.CharField(max_length=150, blank=True, help_text="Specific gig, demo name, or CTA text")
    ip_prefix = models.CharField(max_length=45, blank=True, help_text="Truncated anonymized IP")

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Analytics Event'
        verbose_name_plural = 'Analytics Events'

    def __str__(self):
        return f"{self.event_name} on {self.path} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"
