"""
Product Relevance Engine for PriceWise.
Computes a robust 0.0 - 1.0 relevance score comparing user intent
against candidate e-commerce product titles and categories.
Applies heavy penalties for accessory mismatches, wrong models, or wrong variants.
"""

import re
import logging
from typing import Optional, List
from app.services.query_parser import ParsedQuery, ACCESSORY_KEYWORDS

logger = logging.getLogger(__name__)

# Minimum score threshold to consider a product relevant to the user search
MINIMUM_RELEVANCE_THRESHOLD = 0.40


def compute_relevance_score(
    intent: ParsedQuery,
    product_name: str,
    category: str = "General",
    description: Optional[str] = None,
) -> float:
    """
    Computes a normalized relevance score between 0.0 and 1.0.
    """
    if not intent.raw_query or intent.normalized_query == "__trending__":
        return 1.0  # Trending queries return all catalog items with full score

    title_lower = product_name.lower()
    desc_lower = (description or "").lower()
    cat_lower = category.lower()
    full_text = f"{title_lower} {cat_lower} {desc_lower}"

    score = 0.0

    # 1. Brand Match (+0.25)
    if intent.brand:
        if intent.brand.lower() in full_text:
            score += 0.25
        else:
            score -= 0.15

    # 2. Model Match (+0.35)
    if intent.model:
        model_clean = intent.model.lower()
        if model_clean in title_lower:
            score += 0.35
        elif any(part in title_lower for part in model_clean.split()):
            score += 0.20
        else:
            score -= 0.25

    # 3. Specification / Storage / Variant Match (+0.20)
    if intent.storage:
        if intent.storage.lower() in title_lower:
            score += 0.20
        else:
            # Storage penalty if different storage variant
            storage_in_title = re.search(r"\b(\d+\s*(?:gb|tb))\b", title_lower)
            if storage_in_title and storage_in_title.group(1).replace(" ", "") != intent.storage.lower():
                score -= 0.35

    if intent.size_qty:
        if intent.size_qty.lower() in title_lower:
            score += 0.20

    # 4. Token Overlap Match (+0.20)
    if intent.tokens:
        matched_tokens = sum(1 for token in intent.tokens if token in full_text)
        token_ratio = matched_tokens / len(intent.tokens)
        score += token_ratio * 0.20

    # 5. Accessory Mismatch Heavy Penalty (-0.60)
    is_item_accessory = any(acc in title_lower for acc in ACCESSORY_KEYWORDS)
    if is_item_accessory and not intent.is_accessory_query:
        logger.debug(f"[RelevanceEngine] Accessory penalty applied to '{product_name}'")
        score -= 0.60

    # 6. Specific Model Mismatch Penalty
    # e.g., if searching "iphone 15", penalize "iphone 14", "iphone 13", "iphone 15 pro" unless specified
    if "iphone 15" in intent.normalized_query:
        if "iphone 15 pro" in title_lower and "pro" not in intent.normalized_query:
            score -= 0.25
        elif "iphone 14" in title_lower or "iphone 13" in title_lower:
            score -= 0.50

    # Normalize bounded score between 0.0 and 1.0
    final_score = max(0.0, min(1.0, round(score, 2)))

    logger.debug(
        f"[RelevanceEngine] Query='{intent.raw_query}' vs Title='{product_name}' -> Score={final_score}"
    )

    return final_score
