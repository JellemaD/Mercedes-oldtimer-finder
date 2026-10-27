"""
Kleinanzeigen.de, category Autoteile & Reifen (c223), keyword search per part term.
Card parsing is shared with the car scraper (sources/kleinanzeigen.py: same HTML).
"""

from bs4 import BeautifulSoup

from sources.common import dedupe, fetch, text_of, to_int
from sources.kleinanzeigen import _item

NAME = 'Kleinanzeigen'
COUNTRY = 'DE'
BASE = 'https://www.kleinanzeigen.de'
MAX_PAGES = 2  # 25 ads per page, newest first; daily runs only need the top


def _url(term, page):
    seite = f'seite:{page}/' if page > 1 else ''
    return f'{BASE}/s-autoteile-reifen/{seite}{term.replace(" ", "-")}/k0c223'


def zoek(onderdelen):
    out, errors, terms = [], [], []
    for o in onderdelen:
        terms += o['zoek'].get('de', [])
    for term in dict.fromkeys(terms):
        try:
            for page in range(1, MAX_PAGES + 1):
                soup = BeautifulSoup(text_of(fetch(_url(term, page))), 'lxml')
                arts = soup.select('article[data-adid]')
                if not arts:
                    break
                for art in arts:
                    try:
                        it = _item(art)
                        if it:
                            # listing() drops prices under 100 (car rule); parts are cheaper
                            el = art.select_one('p.font-strong.text-title3, p.aditem-main--middle--price-shipping--price')
                            it['price'] = to_int(el.get_text(' ', strip=True)) if el else None
                            out.append(it)
                    except Exception:
                        continue
                if len(arts) < 25:
                    break
        except Exception as e:
            errors.append(f'{term}: {e}')
    if errors and not out:
        raise RuntimeError('Kleinanzeigen failed: ' + '; '.join(errors))
    return dedupe(out)
