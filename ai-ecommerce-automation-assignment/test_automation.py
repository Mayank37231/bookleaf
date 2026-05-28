from automation_engine import classify_intent, load_json, retrieve_policies, run_ticket


def test_order_status_ticket():
    result = run_ticket(
        {
            "ticket_id": "TEST-1",
            "customer_email": "maya@example.com",
            "message": "Where is my order BL-1001?",
        }
    )
    assert result.intent == "order_status"
    assert result.order_id == "BL-1001"
    assert not result.escalated
    assert "tracking" in " ".join(result.recommended_actions).lower()


def test_delay_escalates():
    result = run_ticket(
        {
            "ticket_id": "TEST-2",
            "customer_email": "dev@example.com",
            "message": "My order BL-1004 is delayed again.",
        }
    )
    assert result.intent == "delay_complaint"
    assert result.escalated
    assert "shipping_delay" in result.risk_flags
    assert result.model_route == "claude-sonnet-review"
    assert "logistics" in " ".join(result.recommended_actions).lower()


def test_cancellation_before_dispatch():
    result = run_ticket(
        {
            "ticket_id": "TEST-3",
            "customer_email": "anika@example.com",
            "message": "Can I cancel order BL-1003 before it ships?",
        }
    )
    assert result.intent == "cancellation"
    assert result.model_route == "gemini-flash-lite-fast-path"
    assert "Cancel order before dispatch" in result.recommended_actions


def test_policy_retrieval():
    policies = load_json("policies.json")
    results = retrieve_policies("refund return payment", policies)
    titles = [item["policy"]["title"] for item in results]
    assert "Refund processing" in titles or "Return eligibility" in titles


def run_all():
    test_order_status_ticket()
    test_delay_escalates()
    test_cancellation_before_dispatch()
    test_policy_retrieval()
    print("All tests passed.")


if __name__ == "__main__":
    run_all()
