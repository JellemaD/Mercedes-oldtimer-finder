"""
Shared helpers and the listing contract for all source modules.

Every source module in this package defines:
    NAME    = 'Marktplaats'          # display name
    COUNTRY = 'NL'                   # ISO code shown on the site
    RUNNER  = 'github' | 'laptop'    # where the scrape can run (see PLAN.md, phase 1)
    def scrape() -> list[dict]       # all listings found, deduplicated by id

A listing dict has these keys (use listing() to build one):
    required: source, country, id (unique, prefixed per source), url (absolute), title
    optional: text (description/snippet), price (int EUR), year (int), mileage (int km),
              fuel (raw string from the site), location, image (absolute url), attrs (dict)

Rules for scrapers:
- Be polite: fetch() waits DELAY seconds between requests; keep total requests per source < ~40.
- Filter what the site can filter (category = cars, brand = Mercedes, year <= 1987) so the
  classifier gets less noise. The classifier (classify.py) makes the final decision.
- Never raise on a single bad item; skip it. Raise only if the whole source fails.
"""

import re
import time

import requests

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36')
DELAY = 1.5
TIMEOUT = 30

# Search terms per series. Sources pick what fits their search box.
TERMS_W124 = ['w124', 'mercedes 250d', 'mercedes 300d', 'mercedes 300e', 'mercedes 260e', 'mercedes 230e']
TERMS_W201 = ['mercedes 190', 'w201']

HEADERS = {
    'User-Agent': UA,
    'Accept': 'text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8',
    'Accept-Language': 'nl-NL,nl;q=0.9,en;q=0.8,de;q=0.7,es;q=0.6,pt;q=0.5',
}
MODE_HEADERS = {
    # browser navigation headers (car.gr accepts these, plain requests get a Cloudflare 403)
    'nav': {'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'none',
            'Upgrade-Insecure-Requests': '1'},
    # Wallapop API wants app-like headers
    'wallapop': {'Accept': 'application/json', 'X-DeviceOS': '0',
                 'Origin': 'https://es.wallapop.com', 'Referer': 'https://es.wallapop.com/'},
}

_session = requests.Session()
_session.headers.update(HEADERS)
_last = 0.0


def fetch(url, mode='requests', headers=None, params=None):
    """GET with polite delay. mode: requests | nav | wallapop | cffi (Chrome TLS impersonation).
    Returns the response; raises for HTTP errors. Body is always decoded as UTF-8 via text_of()."""
    global _last
    wait = DELAY - (time.time() - _last)
    if wait > 0:
        time.sleep(wait)
    try:
        if mode == 'cffi':
            from curl_cffi import requests as cffi_requests
            r = cffi_requests.get(url, params=params, impersonate='chrome', timeout=TIMEOUT,
                                  headers=headers)
        else:
            h = dict(MODE_HEADERS.get(mode, {}), **(headers or {}))
            r = _session.get(url, params=params, headers=h, timeout=TIMEOUT)
    finally:
        _last = time.time()
    r.raise_for_status()
    return r


def text_of(r):
    """Response body as UTF-8 text (requests sometimes guesses latin-1 for JSON)."""
    try:
        return r.content.decode('utf-8')
    except UnicodeDecodeError:
        return r.content.decode('latin-1')


def to_int(value):
    """'€ 4.950,-' -> 4950, '176.663 km' -> 176663, 3800.0 -> 3800, junk -> None."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    digits = re.sub(r'[^\d]', '', str(value).split(',')[0])
    return int(digits) if digits else None


def to_year(value):
    """'06-1986', '05/1986', '1986', 1986 -> 1986; else None."""
    m = re.search(r'\b(19[5-9]\d|20[0-2]\d)\b', str(value or ''))
    return int(m.group(1)) if m else None


def clean(s, limit=None):
    s = re.sub(r'\s+', ' ', str(s or '')).strip()
    return s[:limit] if limit else s


def listing(source, country, id, url, title, text='', price=None, year=None, mileage=None,
            fuel=None, location=None, image=None, attrs=None):
    price = to_int(price)
    mileage = to_int(mileage)
    return {
        'source': source, 'country': country, 'id': str(id), 'url': url,
        'title': clean(title, 200), 'text': clean(text, 600),
        'price': price if price and 100 <= price <= 500_000 else None,
        'year': to_year(year), 'mileage': mileage if mileage and mileage < 2_000_000 else None,
        'fuel': clean(fuel) or None, 'location': clean(location) or None,
        'image': image or None, 'attrs': attrs or {},
    }


def dedupe(items):
    seen, out = set(), []
    for it in items:
        if it['id'] not in seen:
            seen.add(it['id'])
            out.append(it)
    return out
