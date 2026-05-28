from django.contrib import admin

from .models import Author, IdentityLink, KnowledgeArticle, QueryLog


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "book_title", "package", "status", "published_at", "royalty_balance")
    search_fields = ("name", "email", "phone", "instagram_handle", "book_title", "isbn")
    list_filter = ("status", "package")


@admin.register(KnowledgeArticle)
class KnowledgeArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category")
    search_fields = ("title", "body", "tags")
    list_filter = ("category",)


@admin.register(IdentityLink)
class IdentityLinkAdmin(admin.ModelAdmin):
    list_display = ("identifier", "platform", "author", "confidence", "action", "verified")
    search_fields = ("identifier", "author__name", "author__email")
    list_filter = ("platform", "action", "verified")


@admin.register(QueryLog)
class QueryLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "intent", "confidence", "escalated", "email", "channel")
    search_fields = ("query", "response", "email", "author__name")
    list_filter = ("intent", "escalated", "channel")
