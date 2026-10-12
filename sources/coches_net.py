"""
coches.net (ES): Mercedes-Benz used cars, registration year 1982-1987.

Plain requests get a soft block page ("Ups!"); curl_cffi (Chrome impersonation) works.
The search page embeds all results as window.__INITIAL_PROPS__ = JSON.parse("...") with
initialResults.items (title, year, km, price, fuelType, hp, location). The year filter
(MinYear/MaxYear) and make filter in the URL cut it down to ~50 cars, so no search terms are
needed: we just walk the pages (pg=N, ~30 per page).
"""

import json
import re
import unicodedata

from .common import fetch, text_of, listing, dedupe

NAME = 'coches.net'
COUNTRY = 'ES'
RUNNER = 'github'

BASE = 'https://www.coches.net'
SEARCH = BASE + '/mercedes-benz/segunda-mano/'
PARAMS = {'MinYear': 1982, 'MaxYear': 1987}
MAX_PAGES = 10

PROPS = re.compile(r'window\.__INITIAL_PROPS__\s*=\s*JSON\.parse\((".*?")\);?\s*(?:window|</script)', re.S)


def _props(html):
    m = PROPS.search(html)
    if not m:
        raise ValueError('coches.net: __INITIAL_PROPS__ not found')
    return json.loads(json.loads(m.group(1)))


def _title(it):
    """'MERCEDES-BENZ 260 300SEL' -> 'MERCEDES-BENZ 300SEL': the model field ('260', '300', '200')
    is a coches.net bucket that mixes series (W123/W124/W126/R107), the version says what it is."""
    title = it.get('title') or f"{it.get('make', '')} {it.get('model', '')}"
    make, model = it.get('make') or '', str(it.get('model') or '')
    head = f'{make} {model} '
    if model and title.upper().startswith(head.upper()) and title[len(head):].strip():
        return f'{make} {title[len(head):].strip()}'
    return title


def _plain(s):
    """'Diésel' -> 'Diesel' (classify matches 'diesel' without accent)."""
    return ''.join(c for c in unicodedata.normalize('NFKD', s or '') if not unicodedata.combining(c))


def _item(it):
    loc = it.get('location') or {}
    province = loc.get('mainProvince')
    city = loc.get('cityLiteral')
    hp = it.get('hp')
    fuel = _plain(it.get('fuelType'))
    text = ' · '.join(str(p) for p in (fuel, f'{hp} CV' if hp else None, it.get('year'),
                                        f"{it['km']} km" if it.get('km') else None, city, province) if p)
    url = it.get('url') or ''
    return listing(NAME, COUNTRY, f"cn_{it['id']}", BASE + url if url.startswith('/') else url,
                   _title(it), text=text,
                   price=it.get('price'), year=it.get('year'), mileage=it.get('km'),
                   fuel=fuel, location=province, image=it.get('img'), images=it.get('photos'),
                   attrs={'hp': hp, 'model': it.get('model'), 'city': city,
                          'professional': it.get('isProfessional')})


def scrape():
    items, page, pages = [], 1, 1
    while page <= min(pages, MAX_PAGES):
        props = _props(text_of(fetch(SEARCH, mode='cffi', params=dict(PARAMS, pg=page))))
        res = props.get('initialResults') or {}
        pages = res.get('totalPages') or 1
        for it in res.get('items') or []:
            try:
                items.append(_item(it))
            except (KeyError, TypeError, ValueError):
                continue
        page += 1
    return dedupe(items)
