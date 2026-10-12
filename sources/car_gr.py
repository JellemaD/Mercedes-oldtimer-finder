"""
car.gr (GR): Mercedes-Benz cars with first registration 1982-1987.

Cloudflare blocks datacenter IPs, so this runs on the laptop runner with browser navigation
headers (fetch mode 'nav'). The search page is a Nuxt app: the results are in the
<script id="__NUXT_DATA__"> payload (devalue format: a flat list where values point to other
indexes), under pinia.classifiedsSearch.rows (24 per page, pagination.total).

Filters (from the page's own facets): category=15001 (cars), make=32186 (Mercedes-Benz),
registration-from=>1982, registration-to=<1987, page via pg=N. That is ~70 cars = 3 requests,
which covers every keyword search, so no search terms are needed.
Be gentle: ~4 s between requests, on 403 wait a minute and retry once.
"""

import json
import re
import time

import requests

from .common import fetch, text_of, listing, dedupe, to_int

NAME = 'car.gr'
COUNTRY = 'GR'
RUNNER = 'laptop'

BASE = 'https://www.car.gr'
SEARCH = BASE + '/classifieds/cars/'
PARAMS = {'category': 15001, 'make': 32186, 'registration-from': '>1982', 'registration-to': '<1987'}
HEADERS = {'Accept-Language': 'el-GR,el;q=0.9,en;q=0.8'}
EXTRA_DELAY = 2.5          # on top of common.DELAY (1.5 s) -> ~4 s between requests
RETRY_WAIT = 60
MAX_PAGES = 8

NUXT = re.compile(r'<script[^>]*id="__NUXT_DATA__"[^>]*>(.*?)</script>', re.S)


def _get(params):
    time.sleep(EXTRA_DELAY)
    try:
        return fetch(SEARCH, mode='nav', headers=HEADERS, params=params)
    except requests.HTTPError as e:
        if e.response is None or e.response.status_code != 403:
            raise
        time.sleep(RETRY_WAIT)
        return fetch(SEARCH, mode='nav', headers=HEADERS, params=params)


def _unflatten(arr):
    """Nuxt/devalue payload -> plain Python. ['Reactive', i] etc. are wrappers around index i."""
    memo = {}

    def get(i):
        if not isinstance(i, int) or i < 0 or i >= len(arr):
            return None
        if i in memo:
            return memo[i]
        v = arr[i]
        if isinstance(v, list):
            if v and isinstance(v[0], str):
                kind = v[0]
                if kind == 'Set':
                    r = [get(x) for x in v[1:]]
                elif kind == 'Date' or len(v) < 2 or kind.startswith('Empty'):
                    r = v[1] if kind == 'Date' and len(v) > 1 else None
                else:
                    r = get(v[1])
            else:
                r = []
                memo[i] = r
                r.extend(get(x) for x in v)
                return r
        elif isinstance(v, dict):
            r = {}
            memo[i] = r
            for k, x in v.items():
                r[k] = get(x)
            return r
        else:
            r = v
        memo[i] = r
        return r

    return get(0)


def _search(html):
    m = NUXT.search(html)
    if not m:
        raise ValueError('car.gr: __NUXT_DATA__ not found (Cloudflare page?)')
    data = _unflatten(json.loads(m.group(1)))
    return (data.get('pinia') or {}).get('classifiedsSearch') or {}


def _engine(cc, fuel):
    """'2.500 cc' + 'Πετρέλαιο' -> '2.5 diesel' (classify reads litres, e.g. 190D 2.5 vs 2.0)."""
    cc = to_int(cc)
    if not cc or not 800 <= cc <= 7000:
        return ''
    litres = f'{cc / 1000:.1f}'
    return f'{litres} diesel' if 'πετρ' in (fuel or '').lower() else f'{litres} l'


def _item(r):
    feats = {f.get('key'): f.get('value') for f in r.get('keyFeatures') or [] if isinstance(f, dict)}
    parts = r.get('titleParts') or {}
    text = ' · '.join(p for p in (r.get('descriptiveTitle'), _engine(feats.get('engine_size'), feats.get('fuel_type'))) if p)
    url = r.get('seoUrl') or f"/classifieds/cars/view/{r['id']}"
    return listing(NAME, COUNTRY, f"cargr_{r['id']}", BASE + url if url.startswith('/') else url,
                   r.get('title') or r.get('modelStub'), text=text,
                   price=r.get('price'), year=r.get('registration') or parts.get('year'),
                   mileage=r.get('mileage') or feats.get('mileage'), fuel=feats.get('fuel_type'),
                   location=r.get('addressLong'), image=r.get('thumb'),
                   attrs={'model': parts.get('model'), 'variant': parts.get('variant'),
                          'engine_size': feats.get('engine_size'), 'hp': feats.get('engine_power'),
                          'seller': (r.get('seller') or {}).get('type')})


def scrape():
    items, page, pages = [], 1, 1
    while page <= min(pages, MAX_PAGES):
        params = dict(PARAMS, pg=page) if page > 1 else PARAMS
        search = _search(text_of(_get(params)))
        pag = search.get('pagination') or {}
        total, per = pag.get('total') or 0, pag.get('perPage') or 24
        pages = max(1, -(-total // per))
        for r in search.get('rows') or []:
            try:
                items.append(_item(r))
            except (KeyError, TypeError, ValueError, AttributeError):
                continue
        if pag.get('isLastPage'):
            break
        page += 1
    return dedupe(items)
