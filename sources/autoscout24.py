"""
AutoScout24 (NL, BE, DE, ES) via the __NEXT_DATA__ JSON on the search pages.

One module for four country sites. scrape() runs all four; scrape_country(code) runs one.
Search: Mercedes-Benz, first registration 1982-1987, newest first, narrowed to the model ids
where W124 and W201 are filed (see MODEL_IDS). That cuts DE from ~550 to ~210 results without
losing W124/W201 cars. Each page holds 20 listings; numberOfPages tells when to stop.
"""

import json
import re

from sources.common import dedupe, fetch, listing, text_of

NAME = 'AutoScout24'
COUNTRY = 'multi'
RUNNER = 'github'

SITES = {
    'NL': 'https://www.autoscout24.nl',
    'BE': 'https://www.autoscout24.be/nl',
    'DE': 'https://www.autoscout24.de',
    'ES': 'https://www.autoscout24.es',
}
MAX_PAGES = 12
MAKE_ID = 47  # Mercedes-Benz
# AutoScout24 model ids (taxonomy.models['47']) where sellers file W124/W201 cars.
MODEL_IDS = {
    1846: '190', 1847: '200', 1848: '230', 1850: '250', 1851: '260', 1853: '300',
    1862: 'E 200', 15029: 'E 230', 15695: 'E 250', 15955: 'E 260', 15543: 'E 300',
    16492: 'CE 200', 20241: 'CE 230', 15715: 'CE 300', 77652: 'Baureihe 124',
    20930: 'Overig/Sonstige',
}
NEXT_DATA = re.compile(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)


def _search_url(base, page):
    mmmv = ','.join(f'{MAKE_ID}|{mid}||' for mid in MODEL_IDS)
    return (f'{base}/lst/mercedes-benz?fregfrom=1982&fregto=1987&sort=age&desc=1'
            f'&atype=C&mmmv={mmmv}&page={page}')


def _page_props(html):
    m = NEXT_DATA.search(html)
    if not m:
        raise ValueError('no __NEXT_DATA__')
    return json.loads(m.group(1))['props']['pageProps']


def _item(raw, code, base):
    v = raw.get('vehicle') or {}
    tr = raw.get('tracking') or {}
    model, version = v.get('model') or '', v.get('modelVersionInput') or ''
    squash = lambda s: re.sub(r'[\s-]', '', s.lower())
    if model and squash(version).startswith(squash(model)):
        model = ''  # '190' + '190D 2.5' -> '190D 2.5' (else classify sees a bare '190')
    title = ' '.join(x for x in (v.get('make'), model, version) if x)
    if not title:
        return None
    url = raw.get('url') or ''
    origin = re.match(r'https://[^/]+', base).group(0)
    url = url if url.startswith('http') else origin + url
    price = (raw.get('price') or {}).get('priceRaw') or tr.get('price')
    loc = raw.get('location') or {}
    location = ' '.join(x for x in (loc.get('zip'), loc.get('city')) if x)
    images = raw.get('images') or []
    details = ' · '.join(d.get('data', '') for d in raw.get('vehicleDetails') or [] if d.get('data'))
    return listing(
        NAME, code, f"as24_{code.lower()}_{raw['id']}", url, title,
        text=details, price=price, year=tr.get('firstRegistration'),
        mileage=tr.get('mileage') or v.get('mileageInKm'), fuel=v.get('fuel'),
        location=location, image=images[0] if images else None,
        attrs={'model': v.get('model'), 'modelId': v.get('modelId'),
               'firstRegistration': tr.get('firstRegistration'),
               'displacement': v.get('engineDisplacementInCCM')})


def scrape_country(code):
    base = SITES[code]
    out, pages = [], 1
    page = 1
    while page <= min(pages, MAX_PAGES):
        pp = _page_props(text_of(fetch(_search_url(base, page))))
        pages = pp.get('numberOfPages') or 1
        raws = pp.get('listings') or []
        if not raws:
            break
        for raw in raws:
            try:
                it = _item(raw, code, base)
                if it:
                    out.append(it)
            except Exception:
                continue
        page += 1
    return dedupe(out)


def scrape():
    items, errors = [], []
    for code in SITES:
        try:
            items += scrape_country(code)
        except Exception as e:
            errors.append(f'{code}: {e}')
    if errors and not items:
        raise RuntimeError('AutoScout24 failed: ' + '; '.join(errors))
    return dedupe(items)
