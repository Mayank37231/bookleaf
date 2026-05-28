import math
import re
from collections import Counter

from support.models import KnowledgeArticle


STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "for", "from", "how",
    "i", "in", "is", "it", "my", "of", "on", "or", "the", "to", "what", "when",
    "where", "why", "will", "with", "you", "your",
}


def tokenize(text):
    return [token for token in re.findall(r"[a-z0-9]+", text.lower()) if token not in STOPWORDS]


def search_kb(query, limit=3):
    articles = list(KnowledgeArticle.objects.all())
    if not articles:
        return []

    query_terms = Counter(tokenize(query))
    if not query_terms:
        return []

    docs = [tokenize(f"{article.title} {article.category} {article.tags} {article.body}") for article in articles]
    doc_freq = Counter(term for doc in docs for term in set(doc))
    total_docs = len(docs)
    results = []

    for article, terms in zip(articles, docs):
        term_counts = Counter(terms)
        score = 0.0
        
        # TF-IDF scoring with title boost
        title_terms = Counter(tokenize(article.title))
        category_terms = Counter(tokenize(article.category))
        
        for term, query_count in query_terms.items():
            if term in term_counts:
                idf = math.log((1 + total_docs) / (1 + doc_freq[term])) + 1
                base_score = query_count * term_counts[term] * idf
                
                # Boost score if term appears in title or category
                title_boost = 3.0 if term in title_terms else 1.0
                category_boost = 2.0 if term in category_terms else 1.0
                
                score += base_score * title_boost * category_boost
        
        if score > 0:
            results.append({"article": article, "score": round(score, 3)})

    return sorted(results, key=lambda item: item["score"], reverse=True)[:limit]
