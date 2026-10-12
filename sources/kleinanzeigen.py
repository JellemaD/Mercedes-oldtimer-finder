"""
Kleinanzeigen.de, category Autos (c216), plain HTML search pages.

The URL filters work: first registration (autos.ez_i:from,to), brand (autos.marke_s) and model
(autos.model_s, several comma-separated). All Mercedes 1982-1987 is ~1500 ads (too many), so:
- W124 model names, EZ 1984-1987 (W124 started late 1984; skips most W123s)
- model 190, EZ 1982-1987
- keyword w124 / w201 / 190 within "Weitere Mercedes Benz" (misfiled cars)
25 ads per page; the "1 - 25 von N" header tells when to stop.
Cards: <article data-adid data-href>, h3 title, snippet, price, tags 'EZ 05/1986' and 'km'.
"""

import json
import re
from html import unescape as html_unescape

from bs4 import BeautifulSoup

from sources.common import dedupe, fetch, listing, text_of

NAME = 'Kleinanzeigen'
COUNTRY = 'DE'
RUNNER = 'github'

BASE = 'https://www.kleinanzeigen.de'
PER_PAGE = 25
MAX_PAGES = 15
BRAND = '+autos.marke_s:mercedes_benz'
W124_MODELS = '200,230,250,260,300,e_klasse,e_200,e_230,e_260,e_300,ce_230,ce_300'
# (keyword or None, ez_from, models)
QUERIES = [
    (None, 1984, W124_MODELS),
    (None, 1982, '190'),
    ('w124', 1984, 'andere'),
    ('w201', 1982, 'andere'),
    ('190', 1982, 'andere'),
]
COUNT = re.compile(r'\d+\s*-\s*\d+\s+von\s+([\d.]+)')


def _url(keyword, ez_from, models, page):
    seite = f'seite:{page}/' if page > 1 else ''
    kw = f'{keyword}/k0' if keyword else ''
    filters = f'c216+autos.ez_i:{ez_from}%2C1987{BRAND}+autos.model_s:{models.replace(",", "%2C")}'
    return f'{BASE}/s-autos/mercedes_benz/{seite}{kw}{filters}'


def _total(soup):
    m = COUNT.search(soup.get_text(' ', strip=True))
    return int(m.group(1).replace('.', '')) if m else None


def _item(art):
    adid = art.get('data-adid')
    href = art.get('data-href') or ''
    a = art.select_one('h3 a') or art.select_one('h2 a')
    if not adid or not a:
        return None
    title = a.get_text(' ', strip=True)
    url = BASE + href if href.startswith('/') else (href or BASE + a.get('href', ''))
    snippet = art.select_one('h3 + p, h2 + p')
    text = snippet.get_text(' ', strip=True) if snippet else ''
    price_el = art.select_one('p.font-strong.text-title3, p.aditem-main--middle--price-shipping--price')
    price = price_el.get_text(' ', strip=True) if price_el else None
    tags = [t.get_text(' ', strip=True) for t in art.select('span[data-dhl-promotion], .simpletag')]
    year = mileage = None
    for t in tags:
        if re.match(r'EZ\s', t):
            year = t
        elif t.endswith('km'):
            mileage = t
    loc_svg = art.select_one('svg[data-title="locationOutline"]')
    location = loc_svg.find_next('span').get_text(' ', strip=True) if loc_svg else None
    image = None
    ld = art.select_one('script[type="application/ld+json"]')
    if ld:
        try:
            image = json.loads(ld.string or '{}').get('contentUrl')
        except ValueError:
            pass
    return listing(NAME, COUNTRY, f'ka_{adid}', url, title,
                   text=' · '.join([text] + tags), price=price, year=year, mileage=mileage,
                   location=location, image=image, attrs={'tags': tags})


def _query(keyword, ez_from, models):
    out, pages, page = [], 1, 1
    while page <= min(pages, MAX_PAGES):
        soup = BeautifulSoup(text_of(fetch(_url(keyword, ez_from, models, page))), 'lxml')
        total = _total(soup)
        if total is not None:
            pages = -(-total // PER_PAGE)
        arts = soup.select('article[data-adid]')
        if not arts:
            break
        for art in arts:
            try:
                it = _item(art)
                if it:
                    out.append(it)
            except Exception:
                continue
        page += 1
    return out


def detail_images(url):
    """All gallery photos (960 px) from the ad page; used by the rust check when the search
    result photos don't show the sills."""
    # Kleinanzeigen serves two page layouts at random:
    # - app layout (~3 MB): the ad's photos are the first "imageList" in the embedded data;
    # - classic layout (~250 kB): each gallery photo is referenced 5+ times, other ads' photos 1-3 times.
    page = html_unescape(text_of(fetch(url)))
    pattern = r'prod-ads/images/([0-9a-f]{2}/[0-9a-f-]{36})'
    start = page.find('"imageList"')
    if start >= 0:
        gallery = list(dict.fromkeys(re.findall(pattern, page[start:page.find('}]]]', start) + 4])))
    else:
        paths = re.findall(pattern, page)
        gallery = [p for p in dict.fromkeys(paths) if paths.count(p) >= 4]
    return [f'https://img.kleinanzeigen.de/api/v1/prod-ads/images/{p}?rule=$_59.JPG' for p in gallery]


def scrape():
    items, errors = [], []
    for q in QUERIES:
        try:
            items += _query(*q)
        except Exception as e:
            errors.append(f'{q}: {e}')
    if errors and not items:
        raise RuntimeError('Kleinanzeigen failed: ' + '; '.join(errors))
    return dedupe(items)
