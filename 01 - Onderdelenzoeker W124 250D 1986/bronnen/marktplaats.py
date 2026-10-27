"""
Marktplaats.nl, category Auto-onderdelen (l1CategoryId=2600), JSON search API per part term.
Item parsing is shared with the car scraper (sources/marktplaats.py).
"""

import json

from sources.common import dedupe, fetch, text_of
from sources.marktplaats import _to_listing

NAME = 'Marktplaats'
COUNTRY = 'NL'
BASE = 'https://www.marktplaats.nl'
ONDERDELEN = 2600


def zoek(onderdelen):
    out, errors, terms = [], [], []
    for o in onderdelen:
        terms += o['zoek'].get('nl', [])
    for term in dict.fromkeys(terms):
        try:
            params = {'query': term, 'limit': 100, 'offset': 0, 'l1CategoryId': ONDERDELEN,
                      'sortBy': 'SORT_INDEX', 'sortOrder': 'DECREASING'}
            d = json.loads(text_of(fetch(f'{BASE}/lrp/api/search', params=params)))
            for i in d.get('listings') or []:
                try:
                    it = _to_listing(i, BASE, NAME, COUNTRY, 'mp_')
                    if it:
                        # listing() drops prices under 100 (car rule); parts are cheaper
                        cents = (i.get('priceInfo') or {}).get('priceCents')
                        it['price'] = cents // 100 if cents else None
                        out.append(it)
                except Exception:
                    continue
        except Exception as e:
            errors.append(f'{term}: {e}')
    if errors and not out:
        raise RuntimeError('Marktplaats failed: ' + '; '.join(errors))
    return dedupe(out)
