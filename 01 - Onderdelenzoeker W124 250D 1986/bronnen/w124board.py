"""
W124-Board.de, Marktplatz > Biete > Teile (board f188): the latest threads. Everything there is
W124, so zoek.py skips the W124 check for this source. Thread URLs: /teile-f188/<slug>-t<id>/p1.html
"""

import re

from bs4 import BeautifulSoup

from sources.common import dedupe, fetch, listing, text_of

NAME = 'W124-Board.de'
COUNTRY = 'DE'
BASE = 'https://www.w124-board.de'
BOARD = 'teile-f188'
PAGES = 3
THREAD = re.compile(r'/teile-f188/[^/?]+-t(\d+)/')


def zoek(onderdelen):
    out = []
    for page in range(1, PAGES + 1):
        soup = BeautifulSoup(text_of(fetch(f'{BASE}/{BOARD}/p{page}.html')), 'lxml')
        found = 0
        for div in soup.select('div.topic'):
            a = div.select_one('a[href]')
            m = THREAD.search(a['href']) if a else None
            if not m or not a.get_text(strip=True):
                continue
            url = re.sub(r'\?s=[0-9a-f]+', '', a['href'])
            out.append(listing(NAME, COUNTRY, f'wb_{m.group(1)}', url, a.get_text(' ', strip=True),
                               text=div.get_text(' ', strip=True)))
            found += 1
        if not found:
            break
    if not out:
        raise RuntimeError('W124-Board.de: no threads found')
    return dedupe(out)
