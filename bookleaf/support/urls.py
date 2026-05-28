from django.urls import path

from . import views

urlpatterns = [
    path("", views.chat_page, name="chat_page"),
    path("identity/", views.identity_page, name="identity_page"),
    path("logs/", views.logs_page, name="logs_page"),
    path("api/chat", views.chat_api, name="chat_api"),
    path("api/logs", views.logs_api, name="logs_api"),
    path("api/identify", views.identify_api, name="identify_api"),
    path("api/authors", views.authors_api, name="authors_api"),
    path("api/identity/verify", views.identity_verify_api, name="identity_verify_api"),
    path("api/health", views.health_api, name="health_api"),
]
