# Assignment Submission

## Candidate Submission Summary

Selected use case: **Shopify/eCommerce Automation**

This repository contains a working AI-powered eCommerce support automation prototype. The system analyzes Shopify-like support tickets, classifies the customer intent, resolves order context, retrieves relevant policy guidance with local RAG-style search, recommends business actions, flags operational risk, routes cases across a multi-model architecture, and escalates sensitive cases to human review.

## Deliverables

- GitHub repository: https://github.com/Mayank37231/ai_ecommerce_automation
- Working prototype/POC: `automation_engine.py`, `app.py`, `static/`, `data/`
- Documentation/report: `docs/REPORT.md`
- Workflow diagram: `docs/workflow.md`
- Demo walkthrough: `docs/DEMO_WALKTHROUGH.md`
- Run instructions: `README.md`
- Tests: `test_automation.py`

## How To Run

```powershell
python app.py
```

Open:

```text
http://127.0.0.1:8088
```

Run CLI demo:

```powershell
python automation_engine.py
```

Run tests:

```powershell
python test_automation.py
```

## Evaluation Coverage

- Research depth: compares OpenAI, Claude, Gemini, n8n, and Pinecone.
- Practical AI understanding: demonstrates classification, retrieval, action recommendation, escalation, and model routing.
- Prototype quality: dependency-free runnable Python app with API endpoints and browser UI.
- Architecture thinking: includes recommended production architecture, scaling plan, and risk controls.
- Tool selection reasoning: explains why each model/platform is selected.
- Business impact: maps workflow to reduced support load, faster response, and safer automation.

## Bonus Coverage

- AI agents: agent-style decision layer with recommended next actions.
- RAG systems: local TF-IDF policy retrieval over store policies.
- Multi-model workflows: model routing across Gemini Flash-Lite, GPT-5.4 mini, Claude Sonnet, and human review.
- Shopify/eCommerce automation: order lookup, tracking response, cancellation flow, return/refund routing.
- Cost optimization analysis: monthly model and infrastructure estimates in `docs/REPORT.md`.
- Production deployment thinking: queues, PostgreSQL, Pinecone, n8n, audit logs, monitoring, and evaluation plan.
