"""
MercedesForum.nl, subforum "Aanbod onderdelen en accessoires" (phpBB, f=49): the latest threads.
No search per part; zoek.py matches thread titles against the parts. Threads have no price field.
"""

import re

from bs4 import BeautifulSoup

from sources.common import dedupe, fetch, listing, text_of

NAME = 'MercedesForum.nl'
COUNTRY = 'NL'
BASE = 'https://www.mercedesforum.nl/forum/'
FORUM = 49
PAGES = 3  # 50 threads per page


def _strip_sid(href):
    return re.sub(r'[?&]sid=[0-9a-f]+', '', href)


def zoek(onderdelen):
    out = []
    for page in range(PAGES):
        url = f'{BASE}viewforum.php?f={FORUM}&start={page * 50}'
        soup = BeautifulSoup(text_of(fetch(url)), 'lxml')
        rows = soup.select('li.row')
        if not rows:
            break
        for row in rows:
            a = row.select_one('a.topictitle')
            if not a:
                continue
            m = re.search(r't=(\d+)', a.get('href', ''))
            if not m:
                continue
            href = _strip_sid(a['href']).lstrip('./')
            date_el = row.select_one('time')
            out.append(listing(NAME, COUNTRY, f'mf_{m.group(1)}', BASE + href, a.get_text(' ', strip=True),
                               text=row.get_text(' ', strip=True),
                               attrs={'datum': date_el.get('datetime') if date_el else None}))
    if not out:
        raise RuntimeError('MercedesForum.nl: no threads found')
    return dedupe(out)
