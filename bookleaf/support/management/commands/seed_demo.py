from datetime import date

from django.core.management.base import BaseCommand

from support.models import Author, KnowledgeArticle


AUTHORS = [
    {
        "name": "Sara Johnson",
        "email": "sara.johnson@example.com",
        "phone": "+91 9876543210",
        "instagram_handle": "@sarapoetry23",
        "dashboard_name": "Sara J.",
        "book_title": "Whispers of the Soul",
        "isbn": "978-81-19123-01-2",
        "package": "Standard",
        "status": "published",
        "submitted_at": date(2026, 1, 22),
        "published_at": date(2026, 3, 15),
        "expected_publish_at": date(2026, 3, 18),
        "author_copy_status": "Your free author copy coupon was issued for India delivery",
        "tracking_number": "BLF784512IN",
        "royalty_balance": 1840,
        "sales_count": 46,
    },
    {
        "name": "Aarav Mehta",
        "email": "aarav.mehta@example.com",
        "phone": "+91 9988776655",
        "instagram_handle": "@aaravwrites",
        "dashboard_name": "Aarav M",
        "book_title": "Rain on Marine Drive",
        "isbn": "978-81-19123-02-9",
        "package": "Bestseller Package",
        "status": "in_review",
        "submitted_at": date(2026, 5, 2),
        "expected_publish_at": date(2026, 6, 1),
        "author_copy_status": "Bestseller package physical copies are queued after review approval",
        "royalty_balance": 3250,
        "sales_count": 0,
    },
    {
        "name": "Nisha Verma",
        "email": "nisha.verma@example.com",
        "phone": "+91 9123456780",
        "instagram_handle": "@nishaverse",
        "dashboard_name": "Nisha V",
        "book_title": "Letters I Never Sent",
        "isbn": "978-81-19123-03-6",
        "package": "Global Distribution",
        "status": "printing",
        "submitted_at": date(2026, 3, 9),
        "published_at": date(2026, 4, 21),
        "expected_publish_at": date(2026, 4, 25),
        "author_copy_status": "Author copy is being printed",
        "royalty_balance": 920,
        "sales_count": 19,
    },
    {
        "name": "Kabir Anand",
        "email": "kabir.anand@example.com",
        "phone": "+91 9000011112",
        "instagram_handle": "@kabirink",
        "dashboard_name": "Kabir Anand",
        "book_title": "Small Town Stardust",
        "isbn": "",
        "package": "Standard",
        "status": "draft",
        "submitted_at": date(2026, 5, 20),
        "expected_publish_at": date(2026, 7, 10),
        "author_copy_status": "",
        "royalty_balance": 0,
        "sales_count": 0,
    },
]


ARTICLES = [
    ("21-Day Writing Challenge", "Challenge registration", "The 21-Day Writing Challenge registration fee is Rs. 1999. Authors can write in English, Hindi, or Hinglish and may request a 7-day extension.", "challenge hindi hinglish registration fee extension"),
    ("Login & Credentials", "Dashboard credentials", "Login credentials are usually delivered within 2 minutes. Authors should check spam and use password reset if credentials are missing.", "login password dashboard credentials spam reset"),
    ("Dashboard & Submission", "Submission flow", "Authors can submit poems, add acknowledgements and dedication, save drafts, preview, finish, and rearrange poems from the dashboard.", "submission poems dedication draft preview"),
    ("Cover Design", "Cover upload requirements", "Custom front cover uploads should use a 5x8 inch format. Back cover text is limited to around 60 words. Mobile upload is not recommended.", "cover upload back cover author photo"),
    ("Publishing Timeline", "Standard publishing timeline", "Standard publishing typically takes 30-45 business days after review. Bestseller Package publishing is usually prioritized within 18-22 business days.", "publish live review timeline bestseller"),
    ("Add-on Services", "BookLeaf add-ons", "Global Distribution, Emily Dickinson Award, Copyright support, and Bestseller Package are tracked as paid add-on services.", "global distribution award copyright bestseller addon"),
    ("Author Copies", "Author copy policy", "Standard authors receive a free coupon code for India-only author copies around 10 business days after review. Bestseller authors receive 5 physical copies.", "author copy coupon shipping tracking bestseller"),
    ("Royalties", "Royalty payout policy", "Standard authors receive 80% of profit. Bestseller authors receive 100% of profit. Minimum payout threshold is Rs. 2000 or $100.", "royalty payout profit razorpay threshold"),
    ("Sales Reports", "Sales report updates", "Live eBook sales may appear faster, while Indian and international sales reports are generally updated monthly after the 15th.", "sales report amazon flipkart monthly isbn"),
    ("Amazon Issues", "Amazon sync delays", "Amazon out-of-stock or Prime sync issues can take 24-48 hours to resolve because print-on-demand marketplace data updates asynchronously.", "amazon stock prime pod delivery"),
    ("Bestseller Package", "Bestseller benefits", "The Bestseller Package includes a publishing consultant, priority publishing, 13 Amazon marketplaces, Flipkart, and copyright-registration support.", "bestseller consultant priority marketplaces flipkart"),
    ("Policies", "Ownership and changes", "Authors retain 100% ownership. Post-publishing changes may require a paid revision fee, and publishing certificates are available after publication.", "ownership refund policy certificate changes"),
]


class Command(BaseCommand):
    help = "Seed BookLeaf demo authors and knowledge-base articles."

    def handle(self, *args, **options):
        for data in AUTHORS:
            Author.objects.update_or_create(email=data["email"], defaults=data)

        for category, title, body, tags in ARTICLES:
            KnowledgeArticle.objects.update_or_create(
                title=title,
                defaults={"category": category, "body": body, "tags": tags},
            )

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(AUTHORS)} authors and {len(ARTICLES)} KB articles."))
