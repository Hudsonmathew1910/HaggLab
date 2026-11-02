from django.db import models
import uuid

class Inquiry(models.Model):
    """
    Direct inquiry lead submission for visitors on Path B (non-Fiverr).
    Uses UUID for public-safe id references.
    """
    SERVICE_CHOICES = [
        ('ai_chatbots', 'AI chatbots and RAG assistants'),
        ('saas_mvp', 'SaaS MVPs and AI web apps'),
        ('nlp_ml', 'NLP and machine learning models'),
        ('python_automation', 'Python programs and automation'),
        ('ai_integration', 'AI integration and support'),
        ('not_sure', 'Not sure yet, or something custom'),
    ]

    DATA_CHOICES = [
        ('none', 'None yet'),
        ('spreadsheets', 'Spreadsheets'),
        ('documents', 'PDFs or documents'),
        ('database', 'A database'),
        ('other', 'Other'),
        ('see_answers', 'See the order answers'),  # set by the form for a service with order questions
    ]

    TIMELINE_CHOICES = [
        ('asap', 'As soon as possible'),
        ('month', 'Within a month'),
        ('quarter', 'Within 3 months'),
        ('exploring', 'Just exploring'),
        ('package', 'Package delivery time'),  # set by the form when a package is picked
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
    package = models.CharField(max_length=200, blank=True, help_text="Package picked on the form, with its price.")
    extras = models.TextField(blank=True, help_text="Extras picked on the form, one per line.")
    answers = models.JSONField(default=list, blank=True, help_text="Answers to the service's order questions.")
    business = models.CharField(max_length=200, blank=True)
    source = models.CharField(max_length=200, blank=True)
    ip_address = models.CharField(max_length=45, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Inquiry'
        verbose_name_plural = 'Inquiries'

    def __str__(self):
        return f"{self.name} - {self.get_service_display()} ({self.created_at.strftime('%Y-%m-%d')})"


class InquiryFile(models.Model):
    """A file attached on /start. Stored privately (apps/leads/uploads.py); only staff can download it."""
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, related_name='files')
    question = models.CharField(max_length=300, blank=True)
    path = models.CharField(max_length=300, help_text="Location inside private_uploads/inquiries (random name).")
    original_name = models.CharField(max_length=150)
    content_type = models.CharField(max_length=120)
    size = models.PositiveIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['uploaded_at']
        verbose_name = 'Attached file'
        verbose_name_plural = 'Attached files'

    def __str__(self):
        return self.original_name

    def size_label(self):
        return f'{self.size / 1024:.0f} KB' if self.size < 1024 * 1024 else f'{self.size / 1024 / 1024:.1f} MB'

    def delete(self, *args, **kwargs):
        from .uploads import private_storage
        private_storage().delete(self.path)
        return super().delete(*args, **kwargs)
