import json

from django.test import TestCase

from support.models import QueryLog
from support.management.commands.seed_demo import AUTHORS, ARTICLES


class SupportAutomationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.core.management import call_command

        call_command("seed_demo", verbosity=0)

    def test_seed_demo_creates_fixture_data(self):
        from support.models import Author, KnowledgeArticle

        self.assertEqual(Author.objects.count(), len(AUTHORS))
        self.assertEqual(KnowledgeArticle.objects.count(), len(ARTICLES))

    def test_chat_classifies_resolves_author_and_logs(self):
        response = self.client.post(
            "/api/chat",
            data=json.dumps(
                {
                    "email": "sara.johnson@example.com",
                    "channel": "web",
                    "query": "Is my book live yet?",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["intent"], "book_status")
        self.assertFalse(payload["escalated"])
        self.assertEqual(payload["author"]["email"], "sara.johnson@example.com")
        self.assertIn("Whispers of the Soul", payload["response"])
        self.assertEqual(QueryLog.objects.count(), 1)

    def test_low_confidence_unknown_query_escalates(self):
        response = self.client.post(
            "/api/chat",
            data=json.dumps({"query": "blue triangle banana"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["intent"], "unknown")
        self.assertTrue(payload["escalated"])

    def test_identity_matching_suggests_near_match(self):
        response = self.client.post(
            "/api/identify",
            data=json.dumps({"identifier": "Sara Jonson", "platform": "name"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn(payload["status"], {"suggested", "auto_linked"})
        self.assertEqual(payload["author"]["email"], "sara.johnson@example.com")
