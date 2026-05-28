# Demo Walkthrough

## 1. Start the app

```powershell
python app.py
```

Open `http://127.0.0.1:8088`.

## 2. Run sample tickets

Click **Run demo tickets**. The app analyzes four sample eCommerce tickets:

- Delivery tracking
- Refund/return request
- Delayed shipment complaint
- Cancellation before dispatch

## 3. Show a live ticket

Use:

```text
Customer: dev@example.com
Message: My running shoes order BL-1004 is delayed again. Please help.
```

Expected result:

- Intent: `delay_complaint`
- Order: `BL-1004`
- Escalation: human review
- Model route: `claude-sonnet-review`
- Risk flags: `shipping_delay`, `customer_or_order_risk`
- Recommended actions: send tracking, create logistics follow-up, review retention coupon

## 4. Explain the production path

In production, the rule-based classifier can be replaced or augmented by OpenAI/Gemini/Claude. Local policy retrieval can move to Pinecone or Weaviate once the knowledge base becomes large. n8n can connect the workflow to Shopify, Gmail, Slack, Zendesk, Freshdesk, or a CRM. The model route shown in the UI demonstrates how cheap, fast models can handle routine tickets while stronger models review riskier cases.
