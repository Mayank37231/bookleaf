import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

INTENTS = {
    "order_status": ["where", "order", "track", "tracking", "delivery", "arrive", "eta", "order status"],
    "return_refund": ["return", "refund", "exchange", "money", "payment"],
    "cancellation": ["cancel", "cancellation", "stop", "before it ships"],
    "delay_complaint": ["delayed", "late", "again", "not moving", "angry", "frustrated"],
    "general": ["help", "question", "support"],
}

RETRIEVAL_EXPANSIONS = {
    "order_status": "shipping delivery tracking eta parcel",
    "return_refund": "return refund payment store credit quality check",
    "cancellation": "cancel cancellation dispatch shipped",
    "delay_complaint": "shipping delivery delay tracking eta logistics compensation",
    "general": "support policy help",
}

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "for", "from", "how",
    "i", "in", "is", "it", "my", "of", "on", "or", "the", "to", "what", "when",
    "where", "why", "will", "with", "you", "your", "please",
}


@dataclass
class AutomationResult:
    ticket_id: str
    intent: str
    confidence: float
    order_id: str
    response: str
    recommended_actions: list
    escalated: bool
    risk_flags: list
    model_route: str
    retrieved_policy_titles: list


def load_json(name):
    with (DATA_DIR / name).open("r", encoding="utf-8") as file:
        return json.load(file)


def tokenize(text):
    return [token for token in re.findall(r"[a-z0-9]+", text.lower()) if token not in STOPWORDS]


def classify_intent(message):
    normalized = message.lower()
    scores = {}
    for intent, keywords in INTENTS.items():
        score = 0
        for keyword in keywords:
            if keyword in normalized:
                score += 2 if " " in keyword else 1
        scores[intent] = score / len(keywords)

    if re.search(r"\b[A-Z]{2}-\d{4}\b", message.upper()):
        scores["order_status"] += 0.2

    intent, score = max(scores.items(), key=lambda item: item[1])
    if score == 0:
        return "general", 0.42
    return intent, round(min(0.96, 0.55 + score), 2)


def find_order(message, customer_email, orders):
    order_match = re.search(r"\b[A-Z]{2}-\d{4}\b", message.upper())
    if order_match:
        order_id = order_match.group(0)
        for order in orders:
            if order["order_id"] == order_id:
                return order

    for order in orders:
        if order["customer_email"].lower() == customer_email.lower():
            return order
    return None


def retrieve_policies(query, policies, limit=2):
    query_terms = Counter(tokenize(query))
    docs = [tokenize(f"{item['category']} {item['title']} {' '.join(item['tags'])} {item['body']}") for item in policies]
    doc_freq = Counter(term for doc in docs for term in set(doc))
    results = []

    for policy, terms in zip(policies, docs):
        score = 0.0
        counts = Counter(terms)
        title_terms = set(tokenize(policy["title"]))
        for term, query_count in query_terms.items():
            if term in counts:
                idf = math.log((1 + len(docs)) / (1 + doc_freq[term])) + 1
                boost = 2.2 if term in title_terms else 1.0
                score += query_count * counts[term] * idf * boost
        if score > 0:
            results.append({"policy": policy, "score": round(score, 3)})

    return sorted(results, key=lambda item: item["score"], reverse=True)[:limit]


def recommend_actions(intent, order, confidence):
    actions = []
    escalated = confidence < 0.7

    if order is None:
        return ["Ask customer for order ID or registered email", "Create manual review task"], True

    if intent in {"order_status", "delay_complaint"}:
        actions.append("Send tracking and ETA")
        if order["status"] == "delayed":
            actions.append("Create logistics follow-up task")
            actions.append("Offer retention coupon after review")
            escalated = True
    if intent == "return_refund":
        actions.append("Send return eligibility and refund timeline")
        if order["total"] <= 5000 and order["risk_score"] < 0.2:
            actions.append("Offer instant store credit")
        else:
            actions.append("Route refund to quality-check workflow")
    if intent == "cancellation":
        if order["status"] == "processing":
            actions.append("Cancel order before dispatch")
        else:
            actions.append("Explain return/refusal flow because order has shipped")
            escalated = True

    return actions or ["Send policy-based answer"], escalated


def identify_risk_flags(intent, order, confidence):
    flags = []
    if confidence < 0.7:
        flags.append("low_confidence")
    if order is None:
        flags.append("order_not_found")
        return flags
    if order["status"] == "delayed":
        flags.append("shipping_delay")
    if order["risk_score"] >= 0.2:
        flags.append("customer_or_order_risk")
    if order["total"] >= 7500:
        flags.append("high_value_order")
    if intent == "cancellation" and order["status"] != "processing":
        flags.append("post_dispatch_cancellation")
    return flags


def choose_model_route(intent, confidence, risk_flags):
    if "order_not_found" in risk_flags or confidence < 0.7:
        return "human-review-with-llm-summary"
    if risk_flags:
        return "claude-sonnet-review"
    if intent in {"order_status", "cancellation"}:
        return "gemini-flash-lite-fast-path"
    return "gpt-5.4-mini-default"


def draft_response(ticket, intent, confidence, order, policies, actions, escalated):
    name = order["customer_name"] if order else "there"
    policy_text = " ".join(item["policy"]["body"] for item in policies)

    if order and intent in {"order_status", "delay_complaint"}:
        tracking = f" Tracking: {order['carrier']} {order['tracking_number']}." if order["tracking_number"] else ""
        response = (
            f"Hi {name}, your order {order['order_id']} is currently {order['status'].replace('_', ' ')} "
            f"with an estimated date of {order['eta']}.{tracking}"
        )
    elif order and intent == "return_refund":
        response = f"Hi {name}, your order {order['order_id']} can be checked against our return policy. {policy_text}"
    elif order and intent == "cancellation":
        response = f"Hi {name}, order {order['order_id']} is currently {order['status'].replace('_', ' ')}. {policy_text}"
    else:
        response = f"Hi {name}, I found this policy guidance: {policy_text or 'I need one more detail to help accurately.'}"

    if escalated:
        response += " I have also flagged this for human review so the team can verify the next action."
    return response


def run_ticket(ticket):
    orders = load_json("orders.json")
    policies = load_json("policies.json")
    intent, confidence = classify_intent(ticket["message"])
    order = find_order(ticket["message"], ticket.get("customer_email", ""), orders)
    retrieved = retrieve_policies(f"{ticket['message']} {intent} {RETRIEVAL_EXPANSIONS[intent]}", policies)
    actions, escalated = recommend_actions(intent, order, confidence)
    risk_flags = identify_risk_flags(intent, order, confidence)
    escalated = escalated or bool(risk_flags)
    model_route = choose_model_route(intent, confidence, risk_flags)
    response = draft_response(ticket, intent, confidence, order, retrieved, actions, escalated)

    return AutomationResult(
        ticket_id=ticket["ticket_id"],
        intent=intent,
        confidence=confidence,
        order_id=order["order_id"] if order else "",
        response=response,
        recommended_actions=actions,
        escalated=escalated,
        risk_flags=risk_flags,
        model_route=model_route,
        retrieved_policy_titles=[item["policy"]["title"] for item in retrieved],
    )


def run_demo():
    tickets = load_json("tickets.json")
    return [run_ticket(ticket) for ticket in tickets]


def result_to_dict(result):
    return {
        "ticket_id": result.ticket_id,
        "intent": result.intent,
        "confidence": result.confidence,
        "order_id": result.order_id,
        "response": result.response,
        "recommended_actions": result.recommended_actions,
        "escalated": result.escalated,
        "risk_flags": result.risk_flags,
        "model_route": result.model_route,
        "retrieved_policy_titles": result.retrieved_policy_titles,
    }


if __name__ == "__main__":
    output = {
        "generated_at": date.today().isoformat(),
        "workflow": "Shopify/eCommerce customer support automation",
        "results": [result_to_dict(item) for item in run_demo()],
    }
    print(json.dumps(output, indent=2))
