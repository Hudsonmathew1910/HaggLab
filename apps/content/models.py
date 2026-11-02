from django.conf import settings
from django.db import models

class SiteSetting(models.Model):
    """
    Key-value site settings for all bracketed items or runtime customizations
    (e.g., support window, reply time, code ownership, budget bands, founder photo URL).
    An item with an empty value is hidden on the frontend.
    """
    key = models.CharField(max_length=100, unique=True, help_text="e.g. founder_photo_url, support_window, ownership_terms")
    label = models.CharField(max_length=200, help_text="Human-readable description")
    value = models.TextField(blank=True, help_text="Setting value. If blank, associated frontend blocks remain hidden.")

    class Meta:
        ordering = ['key']
        verbose_name = 'Site Setting'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return f"{self.label} ({self.key})"


class Solution(models.Model):
    """
    Represents one of the 5 business problem categories.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    headline = models.CharField(max_length=255)
    problem = models.TextField(help_text="The visitor's pain point in plain words.")
    cost_today = models.TextField(help_text="How it is handled today without automation.")
    
    # 3-step fix
    step1_title = models.CharField(max_length=150, default="Connect")
    step1_desc = models.TextField()
    step2_title = models.CharField(max_length=150, default="Process")
    step2_desc = models.TextField()
    step3_title = models.CharField(max_length=150, default="Deliver")
    step3_desc = models.TextField()

    expected_outcome = models.TextField(help_text="Expected, not guaranteed outcome.")
    metrics = models.CharField(max_length=255, help_text="Specific numbers tracked, e.g. repeat questions per week, first-reply time")
    
    order = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)

    # Packages for a service with no Fiverr gig (AI integration and support). A service whose active gig has
    # packages uses the gig's instead, so Fiverr and the site stay the same.
    package_summary = models.TextField(blank=True, help_text="What the packages deliver, in a few sentences.")
    packages = models.JSONField(default=list, blank=True, help_text=(
        "List of packages: tier, title, desc, price (USD), days, revisions, included (list of lines)."))
    extras = models.JSONField(default=list, blank=True, help_text="List of extras: name, price (USD), days, desc.")
    requirements = models.JSONField(default=list, blank=True, help_text=(
        "Questions asked after ordering: question, kind (Free text, Multiple choice, Attachment), options."))

    class Meta:
        ordering = ['order', 'title']
        verbose_name = 'Solution'
        verbose_name_plural = 'Solutions'

    def __str__(self):
        return self.title


class ProjectQuerySet(models.QuerySet):
    def public(self):
        """Projects visitors may see: published and with a working Try it page.
        PREVIEW_UNFINISHED_PROJECTS (dev only) also shows projects still being built."""
        qs = self.filter(published=True)
        if not getattr(settings, 'PREVIEW_UNFINISHED_PROJECTS', False):
            qs = qs.filter(try_ready=True)
        return qs


class Project(models.Model):
    """
    Represents a specific project (e.g. DocuMind, InsightDesk, ShopAssist).
    Honesty Rule: Status badge text comes strictly from the status field.
    Delivered is reserved only for real client work.
    """
    STATUS_CHOICES = [
        ('Concept', 'Concept'),
        ('Prototype', 'Prototype'),
        ('Live demo', 'Live demo'),
        ('Delivered', 'Delivered'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    headline = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Concept')
    solutions = models.ManyToManyField(Solution, related_name='projects', blank=True)
    
    problem = models.TextField(help_text="The problem solved in plain words.")
    cost_today = models.TextField(help_text="How it is done today.")

    # 3-step fix
    step1_title = models.CharField(max_length=150, default="Connect")
    step1_desc = models.TextField()
    step2_title = models.CharField(max_length=150, default="Process")
    step2_desc = models.TextField()
    step3_title = models.CharField(max_length=150, default="Deliver")
    step3_desc = models.TextField()

    # Demos and Media
    demo_url = models.URLField(blank=True, help_text="Not used by the site (the Try it page replaced it). Kept for old data.")
    video_url = models.URLField(blank=True, help_text="Backup 60-second walkthrough video URL.")
    demo_note = models.CharField(max_length=255, blank=True, default="Demo data. Not real customer information.")

    # Honest results
    measured_text = models.TextField(blank=True, help_text="Measured results from demo testing. If empty, the block is completely hidden.")
    expected_text = models.TextField(blank=True, help_text="Expected, not guaranteed outcome.")
    inside_text = models.TextField(blank=True, help_text="What's inside: stack, architecture, sandboxing.")

    # Outbound Links
    github_url = models.URLField(blank=True)
    fiverr_gig_slug = models.CharField(max_length=100, blank=True, help_text="Gig identifier for UTM tagged Fiverr links.")
    
    # Public presentation
    built_for = models.CharField(max_length=255, blank=True,
                                 help_text="Industries it suits, separated by ' · '. Example: Clinics · Coaching centres")
    use_cases = models.TextField(blank=True, help_text="One concrete scenario per line (3 is ideal).")
    delivered_count = models.PositiveIntegerField(
        default=0, help_text="Real client deliveries only. Shown as 'Delivered for N clients' once above 0.")
    try_ready = models.BooleanField(
        default=False,
        help_text="Turn on only when the Try it page works end to end. Projects are public only when this is on.")

    order = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)

    objects = ProjectQuerySet.as_manager()

    class Meta:
        ordering = ['order', 'title']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def __str__(self):
        return f"{self.title} ({self.status})"

    @property
    def use_case_list(self):
        return [line.strip() for line in self.use_cases.splitlines() if line.strip()]

    @property
    def built_for_list(self):
        return [part.strip() for part in self.built_for.split('·') if part.strip()]

    @property
    def status_slug(self):
        return self.status.lower().replace(' ', '-')


class FAQ(models.Model):
    """
    Frequently asked questions.
    """
    PAGE_CHOICES = [
        ('all', 'All pages'),
        ('home', 'Home page only'),
        ('faq', 'FAQ page only'),
        ('solution', 'Solution pages'),
    ]

    question = models.CharField(max_length=255)
    answer = models.TextField()
    page = models.CharField(max_length=20, choices=PAGE_CHOICES, default='all')
    solution_slug = models.SlugField(blank=True, help_text="If attached to a specific solution.")
    order = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question


class FiverrGig(models.Model):
    """
    One Fiverr gig. Enter the link once, tick the projects it sells and the service page(s) it belongs to.
    Project, Try it and service pages show a Fiverr button only when a gig is ticked for them.
    """
    title = models.CharField(max_length=150, help_text="Short name shown on the Hire on Fiverr page, e.g. 'AI assistants and support tools'.")
    url = models.URLField(help_text="The gig link from Fiverr, e.g. https://www.fiverr.com/s/2ppPDx8")
    projects = models.ManyToManyField(Project, related_name='fiverr_gigs', blank=True,
                                      help_text="Every project this gig sells (their project and Try it pages show the gig).")
    services = models.ManyToManyField(Solution, related_name='fiverr_gigs', blank=True,
                                      help_text="The service pages that show this gig. A service with no gig shows the contact form.")
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True, help_text="Untick to hide this gig without deleting it.")

    # Shown on the service page under "Packages and prices". Keep them the same as the gig on Fiverr.
    summary = models.TextField(blank=True, help_text="What the gig delivers, in a few sentences (company voice: 'we').")
    packages = models.JSONField(default=list, blank=True, help_text=(
        "List of packages: tier, title, desc, price (USD), days, revisions, included (list of lines)."))
    extras = models.JSONField(default=list, blank=True, help_text="List of gig extras: name, price (USD), days, desc.")
    requirements = models.JSONField(default=list, blank=True, help_text=(
        "Questions asked after ordering: question, kind (Free text, Multiple choice, Attachment), options."))

    class Meta:
        ordering = ['order', 'title']
        verbose_name = 'Fiverr gig'
        verbose_name_plural = 'Fiverr gigs'

    def __str__(self):
        return self.title


class Product(models.Model):
    """
    A product the studio built and runs itself (not client work), e.g. Heros.
    Shown on the home page (one line), the About page (card + features) and known by Haggi, the chat assistant.
    Add a new product here and it appears everywhere; untick Published to hide it.
    """
    name = models.CharField(max_length=80)
    slug = models.SlugField(unique=True)
    kind = models.CharField(max_length=80, help_text="Short label, e.g. 'AI assistant platform'.")
    pitch = models.CharField(max_length=200, help_text="One line for the home page, after the name.")
    description = models.TextField(help_text="A few sentences for the About page and Haggi. Facts, no guarantees.")
    url = models.URLField(blank=True, help_text="Live link (shows a Visit button).")
    features = models.JSONField(default=list, blank=True, help_text=(
        "Features or apps inside it: a list of {name, kind, desc, url}. url is optional."))
    order = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.name
