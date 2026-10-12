"""
Marktplaats (NL) via the JSON API behind the search page (/lrp/api/search).

Two queries per term, both in category Auto's (l1CategoryId=91):
- with the API's construction-year filter (<= 1987): all dated old cars;
- without it, newest first: picks up ads that have no construction year (the filter drops those).
tweedehands.py reuses search_lrp() for 2dehands.be (same platform).
"""

import json

from .common import TERMS_W124, TERMS_W201, dedupe, fetch, listing, text_of

NAME = 'Marktplaats'
COUNTRY = 'NL'
RUNNER = 'github'

BASE = 'https://www.marktplaats.nl'
CARS = 91
MAX_YEAR = 1987
TERMS = TERMS_W124 + TERMS_W201


def _attr(item, key):
    for a in item.get('attributes') or []:
        if a.get('key') == key:
            return a.get('value')
    return None


def _query(base, term, year_filter, offset=0):
    params = {'query': term, 'limit': 100, 'offset': offset, 'l1CategoryId': CARS}
    if year_filter:
        params['attributeRanges[]'] = f'constructionYear:null:{MAX_YEAR}'
    else:
        params.update(sortBy='SORT_INDEX', sortOrder='DECREASING')
    return json.loads(text_of(fetch(f'{base}/lrp/api/search', params=params)))


def _safe(fn, *args):
    """Skip a single bad item instead of failing the source."""
    try:
        return fn(*args)
    except Exception:
        return None


def _to_listing(item, base, source, country, prefix):
    url = item.get('vipUrl') or ''
    if not url or not item.get('itemId'):
        return None
    images = [('https:' + u) if u.startswith('//') else u for u in item.get('imageUrls') or []]
    image = images[0] if images else None
    cents = (item.get('priceInfo') or {}).get('priceCents')
    return listing(
        source, country, prefix + item['itemId'], base + url, item.get('title'),
        text=item.get('categorySpecificDescription') or item.get('description'),
        price=cents // 100 if cents else None,
        year=_attr(item, 'constructionYear'), mileage=_attr(item, 'mileage'), fuel=_attr(item, 'fuel'),
        location=(item.get('location') or {}).get('cityName'), image=image, images=images,
        attrs={'categoryId': item.get('categoryId'), 'priceType': (item.get('priceInfo') or {}).get('priceType')},
    )


def search_lrp(base, source, country, prefix, terms=TERMS, max_pages=3):
    """Search a Marktplaats-platform site (marktplaats.nl, 2dehands.be) for all terms."""
    out, errors = [], 0
    for term in terms:
        try:
            offset = 0
            for _ in range(max_pages):
                d = _query(base, term, True, offset)
                rows = d.get('listings') or []
                out += [x for x in (_to_listing(i, base, source, country, prefix) for i in rows) if x]
                offset += 100
                if offset >= (d.get('totalResultCount') or 0) or not rows:
                    break
            d = _query(base, term, False)
            undated = [i for i in d.get('listings') or [] if not _attr(i, 'constructionYear')]
            out += [x for x in (_to_listing(i, base, source, country, prefix) for i in undated) if x]
        except Exception as e:
            errors += 1
            print(f'{source}: term {term!r} failed: {e}')
    if errors == len(terms):
        raise RuntimeError(f'{source}: all searches failed')
    return dedupe(out)


def scrape():
    return search_lrp(BASE, NAME, COUNTRY, 'mp_')
