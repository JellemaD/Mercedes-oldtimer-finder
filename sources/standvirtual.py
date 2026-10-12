"""
Standvirtual (PT) - car marketplace of the OLX group.

The search page is a Next.js app; the results sit in <script id="__NEXT_DATA__"> as an urql
(GraphQL) cache: props.pageProps.urqlState -> {key: {'data': '<json string>'}} -> one of those has
advertSearch.edges[].node with title, url, price.amount.units, location and parameters[]
(first_registration_year, mileage, fuel_type, version, engine_capacity ...).

Searches: all Mercedes registered up to 1987, plus the model pages W124 and W201 (all years,
because the site's year filter is the first registration in PT, which for imports can be later
than the build year; the classifier decides).
"""

import json
import re

from sources.common import fetch, text_of, listing, dedupe

NAME = 'Standvirtual'
COUNTRY = 'PT'
RUNNER = 'github'

BASE = 'https://www.standvirtual.com/carros/mercedes-benz'
SEARCHES = [
    BASE + '?search%5Bfilter_float_first_registration_year%3Ato%5D=1987',
    BASE + '/w124',
    BASE + '/w201',
]
MAX_PAGES = 5
NEXT_DATA = re.compile(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)


def _search(url):
    """Return the advertSearch dict of one result page (None if not found)."""
    m = NEXT_DATA.search(text_of(fetch(url)))
    if not m:
        return None
    state = json.loads(m.group(1))['props']['pageProps'].get('urqlState') or {}
    for entry in state.values():
        try:
            data = json.loads(entry.get('data') or '{}')
        except (TypeError, ValueError):
            continue
        if isinstance(data, dict) and data.get('advertSearch'):
            return data['advertSearch']
    return None


def _item(node):
    p = {x.get('key'): x for x in node.get('parameters') or []}

    def val(k, display=False):
        x = p.get(k) or {}
        return x.get('displayValue' if display else 'value')

    loc = node.get('location') or {}
    city = (loc.get('city') or {}).get('name')
    region = (loc.get('region') or {}).get('name')
    thumb = node.get('thumbnail') or {}
    cc = val('engine_capacity')
    text = ' '.join(s for s in (node.get('shortDescription'), val('version'),
                                f'{cc} cm3' if cc else '', val('engine_power', True)) if s)
    return listing(
        NAME, COUNTRY, f"sv_{node['id']}", node['url'], node.get('title') or '',
        text=text,
        price=((node.get('price') or {}).get('amount') or {}).get('units'),
        year=val('first_registration_year'),
        mileage=val('mileage'),
        fuel=val('fuel_type', True),
        location=', '.join(s for s in (city, region) if s),
        image=thumb.get('x2') or thumb.get('x1'),
        attrs={'version': val('version'), 'model': val('model', True), 'engine_capacity': cc,
               'origin': val('origin', True)},
    )


def scrape():
    items, errors = [], 0
    for base in SEARCHES:
        for page in range(1, MAX_PAGES + 1):
            url = base if page == 1 else base + ('&' if '?' in base else '?') + f'page={page}'
            try:
                s = _search(url)
            except Exception as e:  # one failing search must not kill the source
                print(f'[{NAME}] {url}: {e}')
                errors += 1
                break
            edges = (s or {}).get('edges') or []
            for e in edges:
                try:
                    items.append(_item(e['node']))
                except Exception:
                    continue
            info = (s or {}).get('pageInfo') or {}
            if not edges or (info.get('currentOffset') or 0) + len(edges) >= (s.get('totalCount') or 0):
                break
    if errors == len(SEARCHES):
        raise RuntimeError(f'{NAME}: all searches failed')
    return dedupe(items)
