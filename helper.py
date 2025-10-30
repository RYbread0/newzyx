import re
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from datetime import datetime

# ==================== HELPER FUNCTIONS ====================
TRACKING_PARAMS = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "fbclid", "gclid", "mc_cid",
                   "mc_eid"}
PUNCT = re.compile(r"[^\w\s]")
STOP = set("a an and are as at be by for from has have in is it its of on or that the to was were with will".split())
AD_WORDS = ["deal", "discount", "sale", "buy", "price", "offer", "coupon", "promo", "% off", "save $", "get the new"]
DEFAULT_EXCLUDE_DOMAINS = [
    "news.google.com", "news.yahoo.com", "finance.yahoo.com", "yahoo.com",
    "msn.com", "flipboard.com", "apple.news", "feedproxy.google.com",
    "pressreader.com", "newsnow.co.uk"
]


def _norm_url(u: str) -> str:
    """Strip scheme, www, tracking params, fragments"""
    p = urlparse(u or "")
    netloc = p.netloc.lower().removeprefix("www.")
    q = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
         if k.lower() not in TRACKING_PARAMS]
    return urlunparse(("", netloc, p.path.rstrip("/"), "", urlencode(q, doseq=True), ""))


def _base_title(t: str) -> str:
    """Take title before ' - Publisher', remove parens at end, lowercase & depunctuate"""
    t = (t or "").strip()
    if " - " in t:
        t = t.split(" - ")[0]
    t = re.sub(r"\s*\([^)]*\)\s*$", "", t)
    t = PUNCT.sub("", t.lower())
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _title_signature(t: str, k: int = 8) -> str:
    """Word signature ignoring stopwords; order-insensitive"""
    words = [w for w in _base_title(t).split() if w not in STOP]
    return " ".join(sorted(words)[:k])


def _is_ad(title: str) -> bool:
    """Check if title contains advertising keywords"""
    tl = (title or "").lower()
    return any(b in tl for b in AD_WORDS)


def get_current_date_filename():
    """Returns current date in M.D.YY format"""
    today = datetime.now()
    return f"{today.month}.{today.day}.{str(today.year % 100).zfill(2)}"
