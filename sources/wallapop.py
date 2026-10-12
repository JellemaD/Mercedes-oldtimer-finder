"""
Wallapop (ES) via the search API with app-like headers (fetch mode 'wallapop').

The cars category (category_id=100, singular; 'category_ids' is ignored) accepts brand and
year filters, so one keyword-less search returns every Mercedes-Benz from 1984-1987 in Spain
with structured year/km/fuel. Paged with meta.next_page.
"""

import json

from .common import dedupe, fetch, listing, text_of

NAME = 'Wallapop'
COUNTRY = 'ES'
RUNNER = 'github'

API = 'https://api.wallapop.com/api/v3/search'
PARAMS = {'category_id': 100, 'brand': 'Mercedes-Benz', 'min_year': 1984, 'max_year': 1987,
          'latitude': 40.4168, 'longitude': -3.7038, 'source': 'search_box', 'order_by': 'newest'}
MAX_PAGES = 8


def _safe(fn, *args):
    """Skip a single bad item instead of failing the source."""
    try:
        return fn(*args)
    except Exception:
        return None


def _to_listing(it):
    if not it.get('id') or not it.get('web_slug'):
        return None
    ta = it.get('type_attributes') or {}
    images = it.get('images') or []
    loc = it.get('location') or {}
    return listing(
        NAME, COUNTRY, 'wp_' + it['id'], 'https://es.wallapop.com/item/' + it['web_slug'],
        it.get('title'), text=it.get('description'),
        price=(it.get('price') or {}).get('amount'),
        year=ta.get('year'), mileage=ta.get('km'), fuel=ta.get('engine'),
        location=', '.join(x for x in (loc.get('city'), loc.get('region2')) if x) or None,
        image=((images[0].get('urls') or {}).get('medium')) if images else None,
        images=[(im.get('urls') or {}).get('medium') for im in images],
        attrs={k: ta[k] for k in ('model', 'version', 'gearbox', 'horsepower') if ta.get(k)},
    )


def scrape():
    out, token = [], None
    for _ in range(MAX_PAGES):
        params = {'next_page': token} if token else PARAMS
        d = json.loads(text_of(fetch(API, mode='wallapop', params=params)))
        items = ((d.get('data') or {}).get('section') or {}).get('payload', {}).get('items') or []
        out += [x for x in (_to_listing(i) for i in items) if x]
        token = (d.get('meta') or {}).get('next_page')
        if not token or not items:
            break
    return dedupe(out)
