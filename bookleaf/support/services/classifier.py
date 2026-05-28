import json
import re

from django.conf import settings


INTENTS = {
    "book_status": {
        "keywords": ["book", "live", "published", "publish", "status", "review", "timeline", "when"],
        "entities": ["email", "book_title"],
    },
    "royalty_info": {
        "keywords": ["royalty", "payment", "payout", "earn", "earning", "razorpay", "balance", "profit"],
        "entities": ["email"],
    },
    "dashboard_access": {
        "keywords": ["login", "password", "dashboard", "credential", "account", "reset", "access"],
        "entities": ["email"],
    },
    "addon_service": {
        "keywords": ["bestseller", "award", "copyright", "global", "distribution", "package", "addon", "add-on"],
        "entities": ["email", "service"],
    },
    "author_copy": {
        "keywords": ["copy", "copies", "shipping", "tracking", "dispatch", "coupon", "delivery", "courier"],
        "entities": ["email"],
    },
    "book_sales": {
        "keywords": ["sales", "sold", "report", "amazon", "flipkart", "stock", "out of stock", "prime"],
        "entities": ["email", "book_title"],
    },
    "isbn_distribution": {
        "keywords": ["isbn", "listed", "marketplace", "distribution", "international", "global"],
        "entities": ["email", "book_title"],
    },
    "writing_challenge": {
        "keywords": ["challenge", "21-day", "21 day", "write", "poem", "hindi", "hinglish", "registration"],
        "entities": [],
    },
    "refund_policy": {
        "keywords": ["refund", "cancel", "cancellation", "money back", "policy"],
        "entities": ["email"],
    },
}


def extract_entities(query, email=""):
    found_email = email or ""
    match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", query)
    if match:
        found_email = match.group(0)

    handle = ""
    handle_match = re.search(r"@[\w_.]+", query)
    if handle_match and not found_email:
        handle = handle_match.group(0)

    return {"email": found_email, "instagram_handle": handle}


def classify_query(query, email=""):
    if settings.OPENAI_API_KEY:
        result = _classify_with_openai(query, email)
        if result:
            return result
    return _classify_with_keywords(query, email)


def _classify_with_openai(query, email=""):
    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        prompt = (
            "Classify this BookLeaf Publishing support query. Return only JSON with "
            "intent, confidence between 0 and 1, and entities. Valid intents: "
            f"{', '.join(INTENTS.keys())}, unknown.\nQuery: {query}\nEmail: {email}"
        )
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a precise support intent classifier."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content)
        data.setdefault("entities", {})
        data["entities"] = {**extract_entities(query, email), **data["entities"]}
        return data
    except Exception:
        return None


def _classify_with_keywords(query, email=""):
    normalized = query.lower().strip()
    if len(normalized) < 3:
        return {"intent": "unknown", "confidence": 0.1, "entities": extract_entities(query, email)}

    scores = {}
    for intent, config in INTENTS.items():
        score = 0
        for keyword in config["keywords"]:
            if keyword in normalized:
                score += 2 if " " in keyword else 1
        scores[intent] = score / max(len(config["keywords"]), 1)

    intent, score = max(scores.items(), key=lambda item: item[1])
    if score == 0:
        return {"intent": "unknown", "confidence": 0.35, "entities": extract_entities(query, email)}

    confidence = min(0.95, 0.55 + score)
    return {"intent": intent, "confidence": round(confidence, 2), "entities": extract_entities(query, email)}
