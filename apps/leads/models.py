from django.db import models
import uuid

class Inquiry(models.Model):
    """
    Direct inquiry lead submission for visitors on Path B (non-Fiverr).
    Uses UUID for public-safe id references.
    """
    SERVICE_CHOICES = [
        ('answer_faster', 'Answer customers and staff faster'),
        ('buy_or_book', 'Help visitors buy or book'),
        ('numbers_to_decisions', 'Turn numbers into decisions'),
        ('remove_repetitive_work', 'Remove repetitive work'),
        ('idea_to_product', 'Turn an idea into a product'),
        ('not_sure', 'Not sure yet'),
    ]

    DATA_CHOICES = [
        ('none', 'None yet'),
        ('spreadsheets', 'Spreadsheets'),
        ('documents', 'PDFs or documents'),
        ('database', 'A database'),
        ('other', 'Other'),
    ]

    TIMELINE_CHOICES = [
        ('asap', 'As soon as possible'),
        ('month', 'Within a month'),
        ('quarter', 'Within 3 months'),
        ('exploring', 'Just exploring'),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # 6 required fields
    name = models.CharField(max_length=150)
    email = models.EmailField()
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    problem = models.TextField(help_text="Problem description with starting number")
    data_available = models.CharField(max_length=50, choices=DATA_CHOICES)
    timeline = models.CharField(max_length=50, choices=TIMELINE_CHOICES)
    consent = models.BooleanField(default=False)

    # Optional fields
    budget_band = models.CharField(max_length=100, blank=True)
    business = models.CharField(max_length=200, blank=True)
    source = models.CharField(max_length=200, blank=True)
    ip_address = models.CharField(max_length=45, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Inquiry'
        verbose_name_plural = 'Inquiries'

    def __str__(self):
        return f"{self.name} - {self.get_service_display()} ({self.created_at.strftime('%Y-%m-%d')})"
