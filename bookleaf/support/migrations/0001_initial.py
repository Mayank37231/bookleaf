from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Author",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("phone", models.CharField(blank=True, max_length=32)),
                ("instagram_handle", models.CharField(blank=True, max_length=80)),
                ("dashboard_name", models.CharField(blank=True, max_length=160)),
                ("book_title", models.CharField(max_length=220)),
                ("isbn", models.CharField(blank=True, max_length=32)),
                ("package", models.CharField(default="Standard", max_length=120)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("in_review", "In Review"), ("published", "Published"), ("printing", "Printing"), ("shipped", "Shipped")], default="in_review", max_length=32)),
                ("submitted_at", models.DateField(blank=True, null=True)),
                ("published_at", models.DateField(blank=True, null=True)),
                ("expected_publish_at", models.DateField(blank=True, null=True)),
                ("author_copy_status", models.CharField(blank=True, max_length=160)),
                ("tracking_number", models.CharField(blank=True, max_length=80)),
                ("royalty_balance", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("sales_count", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="KnowledgeArticle",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("category", models.CharField(max_length=120)),
                ("title", models.CharField(max_length=220)),
                ("body", models.TextField()),
                ("tags", models.CharField(blank=True, max_length=300)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="IdentityLink",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("platform", models.CharField(choices=[("email", "Email"), ("whatsapp", "WhatsApp"), ("instagram", "Instagram"), ("dashboard", "Dashboard"), ("name", "Name"), ("book_title", "Book Title")], max_length=32)),
                ("identifier", models.CharField(max_length=220)),
                ("confidence", models.FloatField(default=0)),
                ("action", models.CharField(choices=[("auto_linked", "Auto Linked"), ("suggested", "Suggested"), ("manual_review", "Manual Review"), ("approved", "Approved"), ("rejected", "Rejected")], default="suggested", max_length=32)),
                ("verified", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("author", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="identity_links", to="support.author")),
            ],
        ),
        migrations.CreateModel(
            name="QueryLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("channel", models.CharField(default="web", max_length=40)),
                ("query", models.TextField()),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("intent", models.CharField(max_length=80)),
                ("confidence", models.FloatField(default=0)),
                ("response", models.TextField()),
                ("escalated", models.BooleanField(default=False)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("author", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="support.author")),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
