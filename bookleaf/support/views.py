import json

from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import Author, IdentityLink, QueryLog
from .services.classifier import classify_query
from .services.identity import find_author
from .services.responder import generate_response


def chat_page(request):
    return render(request, "chat.html")


def identity_page(request):
    return render(request, "identity.html")


def logs_page(request):
    return render(request, "logs.html")


@csrf_exempt
@require_POST
def chat_api(request):
    payload = _json_payload(request)
    query = (payload.get("query") or "").strip()
    email = (payload.get("email") or "").strip()
    channel = (payload.get("channel") or "web").strip()

    if not query:
        return JsonResponse({"error": "Query is required."}, status=400)

    classification = classify_query(query, email)
    result = generate_response(query, classification)
    author = result["author"]
    log = QueryLog.objects.create(
        channel=channel,
        query=query,
        email=email or classification.get("entities", {}).get("email", ""),
        intent=classification["intent"],
        confidence=float(classification["confidence"]),
        response=result["response"],
        escalated=result["escalated"],
        author=author,
        metadata={
            "entities": classification.get("entities", {}),
            "kb": [_article_payload(item["article"], item["score"]) for item in result["kb_results"]],
        },
    )

    return JsonResponse(
        {
            "id": log.id,
            "response": result["response"],
            "intent": classification["intent"],
            "confidence": float(classification["confidence"]),
            "escalated": result["escalated"],
            "author": _author_payload(author) if author else None,
            "kb": log.metadata["kb"],
        }
    )


@require_GET
def logs_api(request):
    logs = QueryLog.objects.select_related("author").all()
    intent = request.GET.get("intent")
    escalated = request.GET.get("escalated")
    if intent:
        logs = logs.filter(intent=intent)
    if escalated in {"true", "false"}:
        logs = logs.filter(escalated=escalated == "true")

    return JsonResponse({"logs": [_log_payload(log) for log in logs[:200]]})


@csrf_exempt
@require_POST
def identify_api(request):
    payload = _json_payload(request)
    identifier = (payload.get("identifier") or "").strip()
    platform = (payload.get("platform") or "").strip()
    if not identifier:
        return JsonResponse({"error": "Identifier is required."}, status=400)

    result = find_author(identifier, platform)
    return JsonResponse(
        {
            "status": result["status"],
            "confidence": result["confidence"],
            "linkId": result["link"].id if result["link"] else None,
            "author": _author_payload(result["author"]) if result["author"] else None,
            "matches": [
                {"author": _author_payload(item["author"]), "confidence": item["confidence"]}
                for item in result["matches"]
            ],
        }
    )


@require_GET
def authors_api(request):
    return JsonResponse({"authors": [_author_payload(author) for author in Author.objects.all()]})


@csrf_exempt
@require_POST
def identity_verify_api(request):
    payload = _json_payload(request)
    link = get_object_or_404(IdentityLink, id=payload.get("linkId"))
    action = payload.get("action")
    if action not in {"approved", "rejected"}:
        return JsonResponse({"error": "Action must be approved or rejected."}, status=400)
    link.action = action
    link.verified = action == "approved"
    link.save(update_fields=["action", "verified"])
    return JsonResponse({"ok": True, "linkId": link.id, "action": link.action, "verified": link.verified})


@require_GET
def health_api(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_ok = True
    except Exception:
        db_ok = False
    return JsonResponse(
        {
            "database": "ok" if db_ok else "error",
            "llm": "configured" if settings.OPENAI_API_KEY else "fallback",
            "threshold": settings.CONFIDENCE_THRESHOLD,
        }
    )


def _json_payload(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return {}


def _author_payload(author):
    return {
        "id": author.id,
        "name": author.name,
        "email": author.email,
        "phone": author.phone,
        "instagram": author.instagram_handle,
        "dashboardName": author.dashboard_name,
        "bookTitle": author.book_title,
        "isbn": author.isbn,
        "package": author.package,
        "status": author.get_status_display(),
        "submittedAt": author.submitted_at.isoformat() if author.submitted_at else None,
        "publishedAt": author.published_at.isoformat() if author.published_at else None,
        "expectedPublishAt": author.expected_publish_at.isoformat() if author.expected_publish_at else None,
        "authorCopyStatus": author.author_copy_status,
        "trackingNumber": author.tracking_number,
        "royaltyBalance": float(author.royalty_balance),
        "salesCount": author.sales_count,
    }


def _article_payload(article, score):
    return {"title": article.title, "category": article.category, "score": score}


def _log_payload(log):
    return {
        "id": log.id,
        "createdAt": log.created_at.isoformat(),
        "query": log.query,
        "email": log.email,
        "intent": log.intent,
        "confidence": log.confidence,
        "response": log.response,
        "escalated": log.escalated,
        "channel": log.channel,
        "author": log.author.name if log.author else "",
    }
