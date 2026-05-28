from difflib import SequenceMatcher

from support.models import Author, IdentityLink


def _ratio(a, b):
    a = (a or "").lower().strip()
    b = (b or "").lower().strip()
    if not a or not b:
        return 0.0
    try:
        from rapidfuzz.fuzz import ratio

        return ratio(a, b) / 100
    except Exception:
        return SequenceMatcher(None, a, b).ratio()


def detect_platform(identifier, platform=""):
    identifier = identifier.strip()
    if platform:
        return platform
    if "@" in identifier and "." in identifier and not identifier.startswith("@"):
        return "email"
    if identifier.startswith("@"):
        return "instagram"
    if identifier.replace("+", "").replace(" ", "").isdigit():
        return "whatsapp"
    return "name"


def find_author(identifier, platform=""):
    platform = detect_platform(identifier, platform)
    exact = _exact_match(identifier, platform)
    if exact:
        link = IdentityLink.objects.create(
            author=exact,
            platform=platform,
            identifier=identifier,
            confidence=0.98,
            action="auto_linked",
            verified=True,
        )
        return {"status": "auto_linked", "confidence": 0.98, "author": exact, "link": link, "matches": []}

    matches = []
    for author in Author.objects.all():
        fields = [
            author.email,
            author.phone,
            author.instagram_handle,
            author.name,
            author.dashboard_name,
            author.book_title,
        ]
        score = max(_ratio(identifier, field) for field in fields)
        if score >= 0.35:
            matches.append({"author": author, "confidence": round(score, 2)})

    matches.sort(key=lambda item: item["confidence"], reverse=True)
    if not matches:
        return {"status": "manual_review", "confidence": 0, "author": None, "link": None, "matches": []}

    best = matches[0]
    action = "auto_linked" if best["confidence"] >= 0.9 else "suggested" if best["confidence"] >= 0.6 else "manual_review"
    link = IdentityLink.objects.create(
        author=best["author"],
        platform=platform,
        identifier=identifier,
        confidence=best["confidence"],
        action=action,
        verified=action == "auto_linked",
    )
    return {"status": action, "confidence": best["confidence"], "author": best["author"], "link": link, "matches": matches[:5]}


def _exact_match(identifier, platform):
    lookup = identifier.strip()
    if platform == "email":
        return Author.objects.filter(email__iexact=lookup).first()
    if platform == "instagram":
        return Author.objects.filter(instagram_handle__iexact=lookup).first()
    if platform == "whatsapp":
        return Author.objects.filter(phone__iexact=lookup).first()
    return None
