"""
Query Processing & Intent Engine for PriceWise.
Normalizes raw user queries, applies autocorrect & synonyms, and extracts
brand, model, specifications, variant details, and product type.
"""

import re
import logging
from typing import Optional, List, Dict, Set
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Common brand dictionary
BRANDS: Dict[str, str] = {
    "apple": "Apple",
    "iphone": "Apple",
    "macbook": "Apple",
    "samsung": "Samsung",
    "galaxy": "Samsung",
    "nike": "Nike",
    "jordan": "Nike",
    "air jordan": "Nike",
    "sony": "Sony",
    "boat": "boAt",
    "rockerz": "boAt",
    "levis": "Levi's",
    "levi's": "Levi's",
    "maybelline": "Maybelline",
    "philips": "Philips",
    "amul": "Amul",
    "nescafe": "Nescafe",
    "decathlon": "Decathlon",
    "oneplus": "OnePlus",
    "nord": "OnePlus",
    "nykaa": "Nykaa",
    "croma": "Croma",
}

# Synonyms for product types
SYNONYMS: Dict[str, str] = {
    "mobile": "smartphone",
    "phone": "smartphone",
    "cellphone": "smartphone",
    "laptop": "laptop",
    "notebook": "laptop",
    "macbook": "laptop",
    "earbuds": "headphones",
    "tws": "headphones",
    "earphones": "headphones",
    "headphone": "headphones",
    "sneakers": "shoes",
    "footwear": "shoes",
    "denim": "jeans",
    "foundation": "makeup",
    "airfryer": "air fryer",
}

# Common typos / autocorrect mappings
AUTOCORRECT: Dict[str, str] = {
    "iphon": "iphone",
    "ipon": "iphone",
    "samung": "samsung",
    "samsun": "samsung",
    "nik": "nike",
    "snakers": "shoes",
    "headfone": "headphones",
    "headfones": "headphones",
    "coffe": "coffee",
}

# Accessory keywords — queries explicitly containing these indicate an accessory search
ACCESSORY_KEYWORDS: Set[str] = {
    "case", "cover", "screen guard", "tempered glass", "charger", "cable",
    "adapter", "strap", "pouch", "stand", "skin", "protector"
}


class ParsedQuery(BaseModel):
    raw_query: str
    normalized_query: str
    brand: Optional[str] = None
    model: Optional[str] = None
    storage: Optional[str] = None
    size_qty: Optional[str] = None
    color: Optional[str] = None
    product_type: Optional[str] = None
    is_accessory_query: bool = False
    tokens: List[str] = Field(default_factory=list)


def parse_user_query(query: Optional[str]) -> ParsedQuery:
    """
    Parses a raw user search query into structured intent attributes.
    """
    if not query or not query.strip():
        return ParsedQuery(
            raw_query="",
            normalized_query="__trending__",
            tokens=[],
        )

    raw_str = query.strip()
    clean_str = re.sub(r"[^\w\s\-\.]", " ", raw_str.lower())
    words = [w.strip() for w in clean_str.split() if w.strip()]

    # 1. Autocorrect
    corrected_words = [AUTOCORRECT.get(w, w) for w in words]
    normalized_text = " ".join(corrected_words)

    # 2. Check accessory intent
    is_accessory = any(acc in normalized_text for acc in ACCESSORY_KEYWORDS)

    # 3. Extract Brand
    detected_brand = None
    for token in corrected_words:
        if token in BRANDS:
            detected_brand = BRANDS[token]
            break

    # 4. Extract Storage / RAM spec (e.g. 128gb, 256gb, 8gb)
    storage_match = re.search(r"\b(\d+\s*(?:gb|tb))\b", normalized_text)
    detected_storage = storage_match.group(1).replace(" ", "").upper() if storage_match else None

    # 5. Extract Size / Quantity spec (e.g. 1l, 200g, 30ml, 8mm, pack of 2)
    qty_match = re.search(r"\b(\d+\s*(?:l|litre|liter|ml|g|kg|gm|mm))\b", normalized_text)
    detected_qty = qty_match.group(1).replace(" ", "").lower() if qty_match else None

    # 6. Extract Color
    colors = ["black", "white", "blue", "red", "green", "starlight", "indigo", "chicago", "gold", "silver", "grey", "gray"]
    detected_color = None
    for c in colors:
        if c in words:
            detected_color = c.title()
            break

    # 7. Extract Product Type via Synonyms
    detected_type = None
    for token in corrected_words:
        if token in SYNONYMS:
            detected_type = SYNONYMS[token]
            break

    # 8. Extract Model (e.g. "iphone 15", "galaxy s24 ultra", "macbook air m2", "wh-1000xm5", "501")
    model_match = re.search(
        r"\b((?:iphone\s+\d+|galaxy\s+s\d+(?:\s+ultra)?|macbook\s+air(?:\s+m\d+)?|wh-\d+xm\d+|air\s+jordan\s+\d+|501|fit\s+me|hd\d+))\b",
        normalized_text,
    )
    detected_model = model_match.group(1).title() if model_match else None

    logger.debug(
        f"[QueryParser] Query='{query}' -> Brand={detected_brand}, Model={detected_model}, "
        f"Storage={detected_storage}, Qty={detected_qty}, Accessory={is_accessory}"
    )

    return ParsedQuery(
        raw_query=raw_str,
        normalized_query=normalized_text,
        brand=detected_brand,
        model=detected_model,
        storage=detected_storage,
        size_qty=detected_qty,
        color=detected_color,
        product_type=detected_type,
        is_accessory_query=is_accessory,
        tokens=corrected_words,
    )
