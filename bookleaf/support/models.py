from django.db import models


class Author(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("in_review", "In Review"),
        ("published", "Published"),
        ("printing", "Printing"),
        ("shipped", "Shipped"),
    ]

    name = models.CharField(max_length=160)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=32, blank=True)
    instagram_handle = models.CharField(max_length=80, blank=True)
    dashboard_name = models.CharField(max_length=160, blank=True)
    book_title = models.CharField(max_length=220)
    isbn = models.CharField(max_length=32, blank=True)
    package = models.CharField(max_length=120, default="Standard")
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="in_review")
    submitted_at = models.DateField(null=True, blank=True)
    published_at = models.DateField(null=True, blank=True)
    expected_publish_at = models.DateField(null=True, blank=True)
    author_copy_status = models.CharField(max_length=160, blank=True)
    tracking_number = models.CharField(max_length=80, blank=True)
    royalty_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sales_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.book_title}"


class KnowledgeArticle(models.Model):
    category = models.CharField(max_length=120)
    title = models.CharField(max_length=220)
    body = models.TextField()
    tags = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class IdentityLink(models.Model):
    PLATFORM_CHOICES = [
        ("email", "Email"),
        ("whatsapp", "WhatsApp"),
        ("instagram", "Instagram"),
        ("dashboard", "Dashboard"),
        ("name", "Name"),
        ("book_title", "Book Title"),
    ]

    ACTION_CHOICES = [
        ("auto_linked", "Auto Linked"),
        ("suggested", "Suggested"),
        ("manual_review", "Manual Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="identity_links")
    platform = models.CharField(max_length=32, choices=PLATFORM_CHOICES)
    identifier = models.CharField(max_length=220)
    confidence = models.FloatField(default=0)
    action = models.CharField(max_length=32, choices=ACTION_CHOICES, default="suggested")
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.platform}: {self.identifier} -> {self.author.name}"


class QueryLog(models.Model):
    channel = models.CharField(max_length=40, default="web")
    query = models.TextField()
    email = models.EmailField(blank=True)
    intent = models.CharField(max_length=80)
    confidence = models.FloatField(default=0)
    response = models.TextField()
    escalated = models.BooleanField(default=False)
    author = models.ForeignKey(Author, null=True, blank=True, on_delete=models.SET_NULL)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.intent} ({self.confidence:.2f})"
