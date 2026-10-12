#!/usr/bin/env python3
"""
Phase 1 spike: which marketplaces can we read, and from where?

Requests one W124 search page per site with browser-like headers and records
status, size, bot-protection signs and whether listing data is present.
Run on the laptop and on a GitHub runner, then compare.

Usage: python tools/site_test.py [label]   -> prints table, writes site_test_<label>.json
"""

import json
import re
import sys
import time

import requests

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36')

SITES = [
    # (country, name, url)
    ('NL', 'Marktplaats (web)', 'https://www.marktplaats.nl/q/mercedes+w124/'),
    ('NL', 'Marktplaats (api)', 'https://www.marktplaats.nl/lrp/api/search?query=mercedes%20w124&limit=30'),
    ('NL', 'Gaspedaal', 'https://www.gaspedaal.nl/zoeken?q=mercedes+w124'),
    ('NL', 'AutoTrack', 'https://www.autotrack.nl/aanbod/mercedes-benz?q=w124'),
    ('NL', 'AutoScout24.nl', 'https://www.autoscout24.nl/lst/mercedes-benz?fregto=1987&sort=age&desc=1'),
    ('BE', '2dehands (api)', 'https://www.2dehands.be/lrp/api/search?query=mercedes%20w124&limit=30'),
    ('BE', 'AutoScout24.be', 'https://www.autoscout24.be/nl/lst/mercedes-benz?fregto=1987&sort=age&desc=1'),
    ('DE', 'AutoScout24.de', 'https://www.autoscout24.de/lst/mercedes-benz?fregto=1987&sort=age&desc=1'),
    ('DE', 'Kleinanzeigen', 'https://www.kleinanzeigen.de/s-autos/mercedes-w124/k0c216'),
    ('DE', 'eBay.de', 'https://www.ebay.de/sch/9801/i.html?_nkw=mercedes+w124'),
    ('DE', 'Mobile.de', 'https://suchen.mobile.de/fahrzeuge/search.html?ms=17200%3B%3B%3B&maxFirstRegistrationDate=1987-12-31&isSearchRequest=true'),
    ('ES', 'AutoScout24.es', 'https://www.autoscout24.es/lst/mercedes-benz?fregto=1987&sort=age&desc=1'),
    ('ES', 'coches.net', 'https://www.coches.net/mercedes-benz/segunda-mano/?MaxYear=1987'),
    ('ES', 'Milanuncios', 'https://www.milanuncios.com/coches-de-segunda-mano/?s=mercedes%20w124'),
    ('ES', 'Wallapop (api)', 'https://api.wallapop.com/api/v3/search?keywords=mercedes%20w124&category_id=100&latitude=40.4168&longitude=-3.7038'),
    ('PT', 'Standvirtual', 'https://www.standvirtual.com/carros/mercedes-benz?search%5Bfilter_float_first_registration_year%3Ato%5D=1987'),
    ('PT', 'OLX.pt', 'https://www.olx.pt/carros-motos-e-barcos/carros/mercedes-benz/q-w124/'),
    ('PT', 'CustoJusto', 'https://www.custojusto.pt/portugal/q/mercedes+w124'),
    ('GR', 'car.gr', 'https://www.car.gr/classifieds/cars/?q=mercedes+w124'),
    ('GR', 'xe.gr', 'https://www.xe.gr/autos/results?query=mercedes%20w124'),
]

# Round 2: blocked sites retried with another technique
# (mode: nav = browser navigation headers, wallapop = app headers, cffi = Chrome TLS impersonation)
SITES_ROUND2 = [
    ('NL', 'Gaspedaal [cffi]', 'https://www.gaspedaal.nl/zoeken?q=mercedes+w124', 'cffi'),
    ('ES', 'Wallapop [api2]', 'https://api.wallapop.com/api/v3/search?keywords=mercedes%20w124&category_ids=100&latitude=40.4168&longitude=-3.7038&source=search_box', 'wallapop'),
    ('PT', 'OLX.pt [cffi]', 'https://www.olx.pt/carros-motos-e-barcos/carros/mercedes-benz/q-w124/', 'cffi'),
    ('GR', 'car.gr [nav]', 'https://www.car.gr/classifieds/cars/?q=mercedes%20w124', 'nav'),
    ('GR', 'car.gr [cffi]', 'https://www.car.gr/classifieds/cars/?q=mercedes%20w124', 'cffi'),
]

EXTRA_HEADERS = {
    'nav': {'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'none',
            'Upgrade-Insecure-Requests': '1', 'Accept-Language': 'el-GR,el;q=0.9,en;q=0.8'},
    'wallapop': {'Accept': 'application/json', 'X-DeviceOS': '0',
                 'Origin': 'https://es.wallapop.com', 'Referer': 'https://es.wallapop.com/'},
}


class ModeSession:
    """Wraps requests.Session; switches technique per mode."""

    def __init__(self, session, mode):
        self.session, self.mode = session, mode

    def get(self, url, **kw):
        if self.mode == 'cffi':
            from curl_cffi import requests as cffi_requests
            return cffi_requests.get(url, impersonate='chrome', timeout=kw.get('timeout', 25))
        return self.session.get(url, headers=EXTRA_HEADERS.get(self.mode, {}), **kw)


BLOCK_SIGNS = {
    'cloudflare': ['cf-chl', 'just a moment', 'challenge-platform', 'cf_chl_opt'],
    'datadome': ['datadome', 'captcha-delivery.com'],
    'akamai': ['access denied', 'reference #'],
    'perimeterx': ['px-captcha', '_pxhd', 'perimeterx'],
    'captcha': ['g-recaptcha', 'hcaptcha', 'captcha'],
}

DATA_SIGNS = {
    'next_data': '__NEXT_DATA__',
    'ld_json': 'application/ld+json',
    'json_api': None,  # filled in when the body parses as JSON
}


def check(country, name, url, session):
    row = {'country': country, 'site': name, 'url': url}
    t0 = time.time()
    try:
        r = session.get(url, timeout=25, allow_redirects=True)
        body = r.text
        low = body.lower()
        row.update(status=r.status_code, kb=round(len(body) / 1024),
                   secs=round(time.time() - t0, 1), final_url=r.url)
        m = re.search(r'<title[^>]*>(.*?)</title>', body, re.I | re.S)
        row['title'] = (m.group(1).strip()[:70] if m else '')
        row['blocked_by'] = [k for k, signs in BLOCK_SIGNS.items()
                             if any(s in low for s in signs)]
        row['data'] = [k for k, s in DATA_SIGNS.items() if s and s in body]
        try:
            json.loads(body)
            row['data'].append('json_api')
        except ValueError:
            pass
        row['hits_w124'] = len(re.findall(r'w\s?124|\b(?:2[036]0|300)\s?e\b|\b(?:250|300)\s?t?d\b', low))
        row['hits_mercedes'] = low.count('mercedes')
    except Exception as e:
        row.update(status='ERR', error=str(e)[:120], secs=round(time.time() - t0, 1))
    return row


def verdict(row):
    if row.get('status') != 200:
        return 'NEE'
    if row['hits_mercedes'] >= 5 and (row['hits_w124'] > 0 or row['data']):
        return 'JA' if not row['blocked_by'] or row['kb'] > 150 else 'TWIJFEL'
    return 'TWIJFEL' if row['kb'] > 50 else 'NEE'


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else 'local'
    s = requests.Session()
    s.headers.update({
        'User-Agent': UA,
        'Accept': 'text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8',
        'Accept-Language': 'nl-NL,nl;q=0.9,en;q=0.8,de;q=0.7,es;q=0.6,pt;q=0.5',
    })
    rows = []
    if len(sys.argv) > 2 and sys.argv[2] == 'round2':
        sites = [(c, n, u, ModeSession(s, m)) for c, n, u, m in SITES_ROUND2]
        label += '_round2'
    else:
        sites = [(c, n, u, s) for c, n, u in SITES]
    for country, name, url, session in sites:
        row = check(country, name, url, session)
        row['verdict'] = verdict(row)
        rows.append(row)
        print(f"{row['verdict']:8} {country} {name:20} status={row.get('status')} "
              f"kb={row.get('kb', '-')} w124={row.get('hits_w124', '-')} "
              f"mb={row.get('hits_mercedes', '-')} data={row.get('data', '')} "
              f"block={row.get('blocked_by', '')} {row.get('error', '')}", flush=True)
        time.sleep(1.5)
    with open(f'site_test_{label}.json', 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
