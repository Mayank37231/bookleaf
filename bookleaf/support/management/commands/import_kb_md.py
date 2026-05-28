from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from support.models import KnowledgeArticle


class Command(BaseCommand):
    help = "Import a Markdown knowledge base into KnowledgeArticle rows."

    def add_arguments(self, parser):
        parser.add_argument("path", help="Path to a Markdown file.")

    def handle(self, *args, **options):
        path = Path(options["path"]).expanduser()
        if not path.exists():
            raise CommandError(f"Markdown file not found: {path}")

        text = path.read_text(encoding="utf-8")
        articles = self._parse_markdown(text)
        if not articles:
            raise CommandError("No articles found. Use Markdown headings such as ## Category and ### Article title.")

        for article in articles:
            KnowledgeArticle.objects.update_or_create(
                title=article["title"],
                defaults={
                    "category": article["category"],
                    "body": article["body"],
                    "tags": article["tags"],
                },
            )

        self.stdout.write(self.style.SUCCESS(f"Imported {len(articles)} knowledge-base articles."))

    def _parse_markdown(self, text):
        category = "Imported Knowledge Base"
        current = None
        articles = []

        for raw_line in text.splitlines():
            line = raw_line.strip()
            if line.startswith("## ") and not line.startswith("### "):
                category = line[3:].strip()
                continue
            if line.startswith("### "):
                if current:
                    articles.append(current)
                current = {"category": category, "title": line[4:].strip(), "body": "", "tags": ""}
                continue
            if current and line:
                current["body"] = f"{current['body']} {line}".strip()

        if current:
            articles.append(current)

        for article in articles:
            words = article["body"].lower().split()
            article["tags"] = " ".join(sorted(set(word.strip(".,:;!?()[]") for word in words[:80]))[:20])

        return [article for article in articles if article["title"] and article["body"]]
