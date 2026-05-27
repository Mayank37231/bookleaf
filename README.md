# BookLeaf AI Automation System

A Django implementation of the BookLeaf author-support automation demo. It handles natural-language author queries, resolves author data from SQLite, enriches answers with a local knowledge base, unifies cross-platform identities, and logs every interaction.

## Features

- Chat API and premium web chat page
- Intent classification with OpenAI when available, keyword fallback when not
- SQLite author database with Django ORM
- Knowledge-base search over seeded BookLeaf support articles
- Identity matching across email, phone, Instagram handle, name, and book title
- Query logs dashboard with filters and export-ready JSON endpoint
- Confidence threshold with automatic escalation below 80%

## Quick Start

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Open:

- Chat: http://127.0.0.1:8000/
- Identity: http://127.0.0.1:8000/identity/
- Logs: http://127.0.0.1:8000/logs/
- Admin: http://127.0.0.1:8000/admin/

Optional `.env`:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
DJANGO_SECRET_KEY=change-me
DEBUG=True
```

Without `OPENAI_API_KEY`, the app uses the offline fallback classifier and template responses.

## Import Your Markdown Knowledge Base

After migration, import your converted Google Drive Markdown file:

```powershell
python manage.py import_kb_md "C:\path\to\bookleaf-kb.md"
```

The importer expects category headings as `## Category` and article headings as `### Article title`. The built-in `seed_demo` command already adds a starter KB, so importing your file will expand or replace matching article titles.
