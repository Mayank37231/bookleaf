from datetime import date

from django.conf import settings

from support.models import Author
from support.services.identity import find_author
from support.services.kb import search_kb


def resolve_author(query, entities):
    email = entities.get("email") or ""
    if email:
        author = Author.objects.filter(email__iexact=email).first()
        if author:
            return author

    handle = entities.get("instagram_handle") or ""
    if handle:
        match = find_author(handle, "instagram")
        return match.get("author")

    return None


def generate_response(query, classification):
    intent = classification["intent"]
    confidence = float(classification["confidence"])
    entities = classification.get("entities", {})
    author = resolve_author(query, entities)
    kb_results = search_kb(query, limit=3)
    
    has_strong_kb_match = kb_results and kb_results[0]["score"] > 5.0

    if intent == "unknown" or confidence < settings.CONFIDENCE_THRESHOLD:
        if has_strong_kb_match:
            article = kb_results[0]["article"]
            response = f"Based on our knowledge base: {article.body[:400]}"
            return {
                "response": response,
                "author": author,
                "kb_results": kb_results,
                "escalated": False,
            }
        return {
            "response": "I'm not fully confident about this one, so I'm escalating it to a human support agent with your query context.",
            "author": author,
            "kb_results": kb_results,
            "escalated": True,
        }

    if author is None and intent not in {"writing_challenge", "refund_policy"}:
        if has_strong_kb_match:
            article = kb_results[0]["article"]
            response = f"Here's relevant information: {article.body[:400]}"
            return {
                "response": response,
                "author": None,
                "kb_results": kb_results,
                "escalated": False,
            }
        return {
            "response": "I couldn't find your author record yet. Please share your registered email, phone number, or book title so I can check the exact status.",
            "author": None,
            "kb_results": kb_results,
            "escalated": True,
        }

    response_map = {
        "book_status": _book_status,
        "royalty_info": _royalty_info,
        "dashboard_access": _dashboard_access,
        "addon_service": _addon_service,
        "author_copy": _author_copy,
        "book_sales": _book_sales,
        "isbn_distribution": _isbn_distribution,
        "writing_challenge": _writing_challenge,
        "refund_policy": _refund_policy,
    }
    message = response_map.get(intent, _fallback)(author, kb_results)
    return {"response": message, "author": author, "kb_results": kb_results, "escalated": False}


def _format_date(value):
    if not value:
        return "not available yet"
    if isinstance(value, date):
        return value.strftime("%d %b %Y")
    return str(value)


def _book_status(author, kb_results):
    if author.status == "published":
        return f"Your book '{author.book_title}' is live. It was published on {_format_date(author.published_at)}. ISBN: {author.isbn or 'being updated'}."
    return f"Your book '{author.book_title}' is currently {author.get_status_display()}. Expected publishing date: {_format_date(author.expected_publish_at)}."


def _royalty_info(author, kb_results):
    rate = "100%" if "bestseller" in author.package.lower() else "80%"
    return f"Your current royalty balance is Rs. {author.royalty_balance}. Your package earns {rate} of profit. Payouts are processed once the minimum threshold is met."


def _dashboard_access(author, kb_results):
    return f"Your dashboard account is linked to {author.email}. Use the password reset option on the author dashboard, then check inbox and spam for the reset email."


def _addon_service(author, kb_results):
    return f"Your active package is {author.package}. Bestseller and add-on services are tracked alongside your publishing status: {author.get_status_display()}."


def _author_copy(author, kb_results):
    details = author.author_copy_status or "Author copy details are being prepared."
    tracking = f" Tracking number: {author.tracking_number}." if author.tracking_number else ""
    return f"{details}.{tracking}"


def _book_sales(author, kb_results):
    return f"'{author.book_title}' currently shows {author.sales_count} recorded sales in this demo database. Marketplace sales reports are usually updated monthly after the 15th."


def _isbn_distribution(author, kb_results):
    return f"ISBN for '{author.book_title}': {author.isbn or 'not assigned yet'}. Distribution depends on your package and marketplace sync status."


def _writing_challenge(author, kb_results):
    return "The 21-Day Writing Challenge supports English, Hindi, and Hinglish submissions. The registration fee is Rs. 1999 and eligible authors can request a 7-day extension."


def _refund_policy(author, kb_results):
    return "BookLeaf's demo policy reference says refunds are handled within the stated 14-day refund window, subject to package and service conditions."


def _fallback(author, kb_results):
    if kb_results:
        article = kb_results[0]["article"]
        return f"Based on our support knowledge base: {article.body[:350]}"
    return "This looks like a specific support case, so I'm escalating it to the team."
