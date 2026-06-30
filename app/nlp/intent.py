"""
Intent detection using spaCy NLP for the Citizen Services Assistant.
Detects user intent and mentioned scheme from a chat message.
"""

import spacy
from app.catalog import CATEGORIES

# Load spaCy model once at module level
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    raise RuntimeError(
        "spaCy model 'en_core_web_sm' not found. "
        "Install it with: python -m spacy download en_core_web_sm"
    )

# Intent keyword mappings
INTENT_KEYWORDS = {
    "eligibility_check": [
        "eligible", "qualify", "eligibility", "can i get", "am i eligible",
        "do i qualify", "criteria", "requirement", "who can apply",
        "check eligibility", "eligible for",
    ],
    "application_steps": [
        "how to apply", "apply", "application", "process", "steps",
        "procedure", "registration", "register", "enroll", "enrolment",
        "sign up", "how do i", "how can i apply",
    ],
    "document_list": [
        "documents", "papers", "required documents", "what documents",
        "paperwork", "supporting documents", "document list",
        "docs needed", "docs required", "certificates",
    ],
    "office_locate": [
        "where", "office", "centre", "center", "nearest", "location",
        "address", "visit", "go to", "find office", "locate",
    ],
}


def _build_scheme_lookup() -> dict:
    """Build a flat lookup: lowered scheme name/id → (scheme_id, category)."""
    lookup = {}
    for cat_id, cat_info in CATEGORIES.items():
        for scheme_id, scheme_info in cat_info["schemes"].items():
            # Map by scheme_id
            lookup[scheme_id.lower()] = (scheme_id, cat_id)
            # Map by display name (lowered)
            lookup[scheme_info["name"].lower()] = (scheme_id, cat_id)
            # Map by individual words in the scheme name (3+ chars) for fuzzy matching
            for word in scheme_info["name"].lower().split():
                cleaned = word.strip("()")
                if len(cleaned) >= 4 and cleaned not in ("yojana", "pradhan", "mantri", "national"):
                    lookup[cleaned] = (scheme_id, cat_id)
    return lookup


SCHEME_LOOKUP = _build_scheme_lookup()


def detect_intent(message: str, category: str = "") -> dict:
    """
    Detect the intent and mentioned scheme from a user message.

    Args:
        message: The user's chat message.
        category: The currently selected category (default context).

    Returns:
        dict with keys:
            - intent: one of the recognized intent strings
            - scheme: scheme_id if detected, else None
            - category: detected or passed-through category
    """
    doc = nlp(message.lower())
    text_lower = message.lower()

    # --- Detect intent ---
    detected_intent = "general_info"  # default fallback

    # Check multi-word phrases first (higher priority)
    phrase_priority = [
        ("eligibility_check", ["can i get", "am i eligible", "do i qualify", "check eligibility", "eligible for", "who can apply"]),
        ("application_steps", ["how to apply", "how do i", "how can i apply"]),
        ("document_list", ["required documents", "what documents", "supporting documents", "document list", "docs needed", "docs required"]),
        ("office_locate", ["find office",]),
    ]
    phrase_found = False
    for intent, phrases in phrase_priority:
        for phrase in phrases:
            if phrase in text_lower:
                detected_intent = intent
                phrase_found = True
                break
        if phrase_found:
            break

    # If no phrase matched, check single-token keywords
    if not phrase_found:
        token_lemmas = {token.lemma_.lower() for token in doc}
        token_texts = {token.text.lower() for token in doc}
        all_tokens = token_lemmas | token_texts

        # Score each intent by number of keyword matches
        best_intent = "general_info"
        best_score = 0
        for intent, keywords in INTENT_KEYWORDS.items():
            score = 0
            for kw in keywords:
                if " " not in kw and kw in all_tokens:
                    score += 1
            if score > best_score:
                best_score = score
                best_intent = intent
        detected_intent = best_intent

    # --- Detect scheme ---
    detected_scheme = None
    detected_category = category if category else None

    # Check if any scheme name or id appears in the message
    # Try longer matches first
    sorted_keys = sorted(SCHEME_LOOKUP.keys(), key=len, reverse=True)
    for key in sorted_keys:
        if key in text_lower:
            scheme_id, cat_id = SCHEME_LOOKUP[key]
            detected_scheme = scheme_id
            if not detected_category:
                detected_category = cat_id
            break

    # If we still have no category, check if a category name is mentioned
    if not detected_category:
        for cat_id, cat_info in CATEGORIES.items():
            if cat_id in text_lower or cat_info["name"].lower() in text_lower:
                detected_category = cat_id
                break

    return {
        "intent": detected_intent,
        "scheme": detected_scheme,
        "category": detected_category or category or "",
    }
