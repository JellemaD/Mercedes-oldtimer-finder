"""
OLX.pt (PT) - general classifieds, cars section. Needs curl_cffi (plain requests gets 403).

The page has window.__PRERENDERED_STATE__ = "<json string>" -> listing.listing with totalPages and
ads[]: id, title, description (HTML), url, price.regularPrice.value, location, photos and
params[] (year, quilometros, combustivel, modelo, engine_capacity ...).

Searches: all Mercedes with year <= 1987 (site filter), plus free-text model searches inside
Mercedes cars (no year filter: some ads have no year, the classifier decides).
"""

import html
import json
import re

from sources.common import fetch, text_of, listing, dedupe

NAME = 'OLX.pt'
COUNTRY = 'PT'
RUNNER = 'github'

BASE = 'https://www.olx.pt/carros-motos-e-barcos/carros/mercedes-benz/'
SEARCHES = [
    (BASE + '?search%5Bfilter_float_year%3Ato%5D=1987', 3),
    (BASE + 'q-w124/', 3),
    (BASE + 'q-s124/', 1),
    (BASE + 'q-w201/', 2),
    (BASE + 'q-190d/', 2),
    (BASE + 'q-190e/', 2),
    (BASE + 'q-250d/', 2),
    (BASE + 'q-300d/', 2),
    (BASE + 'q-300td/', 1),
    (BASE + 'q-300e/', 1),
    (BASE + 'q-260e/', 1),
    (BASE + 'q-230e/', 1),
]
STATE = re.compile(r'window\.__PRERENDERED_STATE__\s*=\s*("(?:[^"\\]|\\.)*")')


def _page(url):
    """Return (ads, total_pages) for one result page."""
    m = STATE.search(text_of(fetch(url, mode='cffi')))
    if not m:
        return [], 0
    data = json.loads(json.loads(m.group(1)))
    lst = (data.get('listing') or {}).get('listing') or {}
    return lst.get('ads') or [], lst.get('totalPages') or 0


def _item(ad):
    p = {x.get('key'): x.get('value') for x in ad.get('params') or []}
    desc = html.unescape(re.sub(r'<[^>]+>', ' ', ad.get('description') or ''))
    fuel = p.get('combustivel')
    extra = []
    if p.get('engine_capacity'):
        extra.append(f"{p['engine_capacity']} cm3")
    if fuel == 'gpl':
        extra.append('GPL')  # lets the classifier set the "already on LPG" badge
    loc = ad.get('location') or {}
    photos = ad.get('photos') or []
    return listing(
        NAME, COUNTRY, f"olx_{ad['id']}", ad['url'], ad.get('title') or '',
        text=' '.join(extra + [desc]),
        price=((ad.get('price') or {}).get('regularPrice') or {}).get('value'),
        year=p.get('year'),
        mileage=p.get('quilometros'),
        fuel=fuel,
        location=', '.join(s for s in (loc.get('cityName'), loc.get('regionName')) if s),
        image=photos[0] if photos else None, images=photos,
        attrs={'modelo': p.get('modelo'), 'engine_capacity': p.get('engine_capacity'),
               'origin': p.get('origin')},
    )


def scrape():
    items, errors = [], 0
    for base, max_pages in SEARCHES:
        for page in range(1, max_pages + 1):
            url = base if page == 1 else base + ('&' if '?' in base else '?') + f'page={page}'
            try:
                ads, total = _page(url)
            except Exception as e:  # one failing search must not kill the source
                print(f'[{NAME}] {url}: {e}')
                errors += 1
                break
            for ad in ads:
                try:
                    items.append(_item(ad))
                except Exception:
                    continue
            if page >= total:
                break
    if errors == len(SEARCHES):
        raise RuntimeError(f'{NAME}: all searches failed')
    return dedupe(items)
