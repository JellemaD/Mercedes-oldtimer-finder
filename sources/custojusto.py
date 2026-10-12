"""
CustoJusto (PT) - general classifieds.

Searching inside the used-cars section (/portugal/veiculos/carros-usados/q/<terms>) keeps parts
out. Results are in <script id="__NEXT_DATA__"> -> props.pageProps.listItems[] with listID, title,
body, price, url (relative), locationNames and params {fuel, gearbox, regdate}. Mileage is only on
the detail page, so it stays empty. Titles end with the two-digit year ("... - 87"); regdate gives
the full year ('1980 ou anterior' -> 1980). Pagination: ?o=2, ?o=3 ... (40 per page).
"""

import json
import re
from urllib.parse import quote_plus

from sources.common import fetch, text_of, listing, dedupe

NAME = 'CustoJusto'
COUNTRY = 'PT'
RUNNER = 'github'

BASE = 'https://www.custojusto.pt'
SEARCH = BASE + '/portugal/veiculos/carros-usados/q/{}'
TERMS = ['mercedes w124', 'mercedes s124', 'mercedes c124', 'mercedes w201', 'mercedes 190',
         'mercedes 250d', 'mercedes 250 d', 'mercedes 300d', 'mercedes 300 d', 'mercedes 300td',
         'mercedes 300e', 'mercedes 260e', 'mercedes 230e']
MAX_PAGES = 2
CAR_CATEGORIES = re.compile(r'^20[2-9]\d$')  # 2021-2029 = car body types; 2121 = parts
NEXT_DATA = re.compile(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)


def _page(term, page):
    url = SEARCH.format(quote_plus(term)) + (f'?o={page}' if page > 1 else '')
    m = NEXT_DATA.search(text_of(fetch(url)))
    if not m:
        return []
    return json.loads(m.group(1))['props']['pageProps'].get('listItems') or []


def _item(it):
    if not CAR_CATEGORIES.match(str(it.get('category') or '')):
        return None
    params = it.get('params') or {}
    loc = it.get('locationNames') or {}
    url = it.get('url') or ''
    return listing(
        NAME, COUNTRY, f"cj_{it['listID']}", url if url.startswith('http') else BASE + url,
        it.get('title') or '',
        text=it.get('body') or '',
        price=it.get('price'),
        year=params.get('regdate'),
        fuel=params.get('fuel'),
        location=', '.join(s for s in (loc.get('county'), loc.get('district')) if s),
        image=it.get('imageFullURL'),
        attrs={'gearbox': params.get('gearbox'), 'body': it.get('categoryName'),
               'listTime': it.get('listTime')},
    )


def scrape():
    items, errors = [], 0
    for term in TERMS:
        for page in range(1, MAX_PAGES + 1):
            try:
                found = _page(term, page)
            except Exception as e:  # one failing search must not kill the source
                print(f'[{NAME}] {term} p{page}: {e}')
                errors += 1
                break
            for it in found:
                try:
                    x = _item(it)
                except Exception:
                    continue
                if x:
                    items.append(x)
            if len(found) < 40:
                break
    if errors == len(TERMS):
        raise RuntimeError(f'{NAME}: all searches failed')
    return dedupe(items)
