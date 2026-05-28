# AI-Powered Shopify/eCommerce Workflow Automation

This repository is a technical-assignment submission for an AI Researcher / AI Innovation Engineer role.

Selected use case: **Shopify/eCommerce Automation**

The prototype demonstrates an AI-style support workflow for an online store:

- Classifies customer tickets into business intents.
- Resolves Shopify-like order records from order ID or customer email.
- Retrieves relevant policy snippets using local TF-IDF RAG.
- Recommends next actions such as send tracking, cancel order, issue store credit, or create logistics follow-up.
- Escalates risky, delayed, or low-confidence cases to human review.
- Shows model routing decisions for a production multi-model workflow.
- Runs without external dependencies or API keys.

## Run The Prototype

```powershell
python app.py
```

Open:

```text
http://127.0.0.1:8088
```

CLI demo:

```powershell
python automation_engine.py
```

Tests:

```powershell
python test_automation.py
```

## API Endpoints

- `GET /api/demo` runs all sample tickets.
- `GET /api/tickets` returns sample tickets.
- `POST /api/analyze` analyzes a single ticket.

Example:

```json
{
  "customer_email": "dev@example.com",
  "message": "My running shoes order BL-1004 is delayed again. Please help."
}
```

## Deliverables

- Working POC: `app.py`, `automation_engine.py`, `static/`, `data/`
- Recommendation report: `docs/REPORT.md`
- Workflow diagram: `docs/workflow.md`
- Demo walkthrough: `docs/DEMO_WALKTHROUGH.md`
