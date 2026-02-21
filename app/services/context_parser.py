import json
import re
from pathlib import Path
from typing import Optional, List, Set

import pymorphy3
from pydantic import BaseModel


_MORPH = pymorphy3.MorphAnalyzer()

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CATEGORIES_PATH = DATA_DIR / "categories.json"
BRANDS_PATH = DATA_DIR / "brands.json"

_STREET_PATTERNS = [
    r"на\s+улице\s+([А-Яа-яA-Za-z0-9\-\s]+)",
    r"на\s+ул\.?\s+([А-Яа-яA-Za-z0-9\-\s]+)",
    r"на\s+проспекте\s+([А-Яа-яA-Za-z0-9\-\s]+)",
    r"на\s+пер(?:еулке)?\.?\s*([А-Яа-яA-Za-z0-9\-\s]+)",
    r"на\s+([А-Яа-яA-Za-z0-9\-\s]+)$",  # "на Троицком"
    r"в\s+районе\s+([А-Яа-яA-Za-z0-9\-\s]+)",
]


class ParsedContext(BaseModel):
    category: Optional[str] = None
    brand: Optional[str] = None
    street: Optional[str] = None


def _load_json(path: Path):
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


_CATEGORIES_CONFIG = _load_json(CATEGORIES_PATH) or {}
_BRANDS = _load_json(BRANDS_PATH) or []


def _normalize_text(text: str) -> str:
    """Lowercase, remove punctuation except hyphen, normalize spaces."""
    text = text.lower()
    text = re.sub(r"[\,\.\;\:\?!]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


_TOKEN_RE = re.compile(r"[A-Za-zА-Яа-я0-9\-]+")


def _tokens(text: str) -> List[str]:
    """Return list of tokens from string."""
    return _TOKEN_RE.findall(text)


def _lemmatize_token(token: str) -> str:
    # return normal form (lemma) from pymorphy3
    parsed = _MORPH.parse(token)
    if parsed:
        return parsed[0].normal_form
    return token


def _lemmatize_list(tokens: List[str]) -> List[str]:
    return [_lemmatize_token(t) for t in tokens]


def _build_lemma_keyword_sets(categories_config: dict) -> dict:
    """
    Build dict: {category: set(lemma_keywords)}
    Lemmatize keywords from config to allow matching across cases/cases.
    """
    out = {}
    for cat, keywords in categories_config.items():
        lemmas = set()
        for kw in keywords:
            kw_norm = _normalize_text(kw)
            kw_tokens = _tokens(kw_norm)
            kw_lemmas = _lemmatize_list(kw_tokens)
            lemmas.update(kw_lemmas)
        out[cat] = lemmas
    return out


_CATEGORY_LEMMAS = _build_lemma_keyword_sets(_CATEGORIES_CONFIG)

_BRAND_LEMMA_MAP = {}
for b in _BRANDS:
    b_norm = _normalize_text(b)
    tokens = _tokens(b_norm)
    lemmas = _lemmatize_list(tokens)
    key = " ".join(lemmas)
    _BRAND_LEMMA_MAP[key] = b


def _detect_street(original_text: str, normalized_text: str) -> Optional[str]:
    for pat in _STREET_PATTERNS:
        m = re.search(pat, original_text, flags=re.IGNORECASE)
        if m:
            street_raw = m.group(1).strip()
            street_raw = re.sub(r"\s+(улица|ул|проспект|пр|пер|переулок|район)$", "", street_raw, flags=re.IGNORECASE)
            street_norm = street_raw.lower()
            tokens = _tokens(street_norm)
            lemmas = _lemmatize_list(tokens)
            return " ".join(lemmas).strip()
    m2 = re.search(r"на\s+([а-яa-z0-9\-\s]+)$", normalized_text)
    if m2:
        street_norm = m2.group(1).strip().lower()
        tokens = _tokens(street_norm)
        lemmas = _lemmatize_list(tokens)
        return " ".join(lemmas).strip()
    return None


def _detect_category_from_lemmas(lemmas: Set[str]) -> Optional[str]:
    # For each category take intersection size; choose best match by largest intersection
    best_cat = None
    best_score = 0
    for cat, kw_lemmas in _CATEGORY_LEMMAS.items():
        score = len(lemmas & kw_lemmas)
        if score > best_score:
            best_score = score
            best_cat = cat
    # require at least one matching lemma to claim category
    if best_score > 0:
        return best_cat
    return None


def _detect_brand_from_lemmas(lemmas: List[str]) -> Optional[str]:
    """
    Try to match brands by comparing sequences of lemmas.
    We create sliding n-gram from lemmas and check presence in BRAND_LEMMA_MAP keys.
    """
    joined = " ".join(lemmas)
    # direct exact match first
    if joined in _BRAND_LEMMA_MAP:
        return _BRAND_LEMMA_MAP[joined]
    # sliding window up to length of brand tokens (max 4 words maybe)
    lemma_list = lemmas
    n = len(lemma_list)
    brand_keys = list(_BRAND_LEMMA_MAP.keys())
    max_brand_len = max((len(k.split()) for k in brand_keys), default=0)
    for size in range(max_brand_len, 0, -1):
        for i in range(0, n - size + 1):
            seg = " ".join(lemma_list[i : i + size])
            if seg in _BRAND_LEMMA_MAP:
                return _BRAND_LEMMA_MAP[seg]
    # heuristic fallback: proper noun detection via original tokens capitalization (optional)
    return None


def parse_context(text: str) -> ParsedContext:
    """
    Parse Russian natural-language search context into structured ParsedContext.

    Requires pymorphy3 installed.

    Returns:
        ParsedContext(category, brand, street)
    """
    if not text or not text.strip():
        return ParsedContext()

    original = text.strip()
    normalized = _normalize_text(original)
    toks = _tokens(normalized)
    lemmas = _lemmatize_list(toks)
    lemma_set = set(lemmas)

    category = _detect_category_from_lemmas(lemma_set)
    brand = _detect_brand_from_lemmas(lemmas)
    street = _detect_street(original, normalized)

    return ParsedContext(category=category, brand=brand, street=street)
