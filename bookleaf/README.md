# BookLeaf AI Customer Support Automation POC

Submission-ready prototype for the AI Researcher / AI Innovation Engineer assignment. The selected use case is **Customer Support Automation** for BookLeaf author support.

The app handles natural-language author queries, resolves author data from SQLite, enriches answers with a local knowledge base, unifies cross-platform identities, escalates low-confidence cases, and logs every interaction.

## Features

- Chat API and premium web chat page
- Intent classification with OpenAI when available and keyword fallback when not
- SQLite author database with Django ORM
- Lightweight local RAG over seeded BookLeaf support articles
- Identity matching across email, phone, Instagram handle, name, and book title
- Query logs dashboard with filters and export-ready JSON endpoint
- Confidence threshold with automatic escalation below 80%
- Research and architecture report in [REPORT.md](REPORT.md)

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
OPENAI_MODEL=gpt-4.1-mini
DJANGO_SECRET_KEY=change-me
DEBUG=True
CONFIDENCE_THRESHOLD=0.80
```

Without `OPENAI_API_KEY`, the app uses the offline fallback classifier and template responses.

## Verification

```powershell
python manage.py test
python manage.py check
```

## Demo Flow

1. Open `http://127.0.0.1:8000/`.
2. Ask `Is my book live yet?` with `sara.johnson@example.com`.
3. Ask `blue triangle banana` to demonstrate low-confidence escalation.
4. Open `http://127.0.0.1:8000/logs/` to show the audit trail.
5. Open `http://127.0.0.1:8000/identity/` and search `Sara Jonson` to show fuzzy identity linking.

## Import Your Markdown Knowledge Base

After migration, import your converted Google Drive Markdown file:

```powershell
python manage.py import_kb_md "C:\path\to\bookleaf-kb.md"
```

The importer expects category headings as `## Category` and article headings as `### Article title`. The built-in `seed_demo` command already adds a starter KB, so importing your file will expand or replace matching article titles.
