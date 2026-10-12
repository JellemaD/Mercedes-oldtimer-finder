"""
Cost of driving the car home yourself: distance from the seller to HOME x consumption x fuel price.

- Location -> coordinates via OpenStreetMap Nominatim (max 1 request/s, cached per location string in
  docs/data/geo.json, so each place is looked up once).
- Road distance = straight line x ROAD_FACTOR (rough; islands also need a ferry, not included).
- Consumption per model on the motorway (litres/100 km, indicative for an 80s car); a petrol car that
  already runs on LPG drives home on LPG (1.2 x the petrol litres).
- Fuel prices: EU averages, week of 5 Oct 2026 (EU Oil Bulletin via fuel-prices.eu); LPG estimated.
  Tolls (France, Italy, Spain) and the trip to the car are not included.

update(listings) adds trip_km and trip_cost (euro) to every active listing with a known location.
"""

import json
import math
import os
import re
import time

import requests

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, 'docs', 'data', 'geo.json')
HOME = (52.1736, 5.2917)  # Soest
ROAD_FACTOR = 1.25
FUEL_PRICE = {'diesel': 2.10, 'benzine': 1.95, 'lpg': 0.95}  # euro per litre
LPG_FACTOR = 1.2
MAX_LOOKUPS = int(os.environ.get('GEO_MAX_LOOKUPS', '600'))  # per run (Nominatim: 1 per second)
USER_AGENT = 'Mercedes-oldtimer-finder (https://github.com/JellemaD/Mercedes-oldtimer-finder)'
COUNTRY_NAME = {'NL': 'nl', 'BE': 'be', 'DE': 'de', 'ES': 'es', 'PT': 'pt', 'GR': 'gr', 'FR': 'fr', 'IT': 'it'}

# litres/100 km on the motorway, by model label from classify.py (first match wins)
CONSUMPTION = [
    ('190D', 7.5), ('250', 8.0), ('300D', 9.0), ('300TD', 9.0),
    ('190E 2.6', 10.5), ('190E 2.3-16', 10.5), ('190E 2.3', 9.5), ('190', 9.0),
    ('200', 10.0), ('230', 10.5), ('260', 11.5), ('300', 12.0),
]


def _load():
    try:
        with open(CACHE, encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return {}


def _save(cache):
    tmp = CACHE + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=0, sort_keys=True)
    os.replace(tmp, CACHE)


def _lookup(country, location):
    """Coordinates for a location string, or None. Postcode first (exact), else free text."""
    cc = COUNTRY_NAME.get(country, '')
    params = {'format': 'json', 'limit': 1, 'countrycodes': cc}
    m = re.search(r'\b(\d{4,5})\b', location)
    if m:
        params['postalcode'] = m.group(1)
    else:
        params['q'] = location
    r = requests.get('https://nominatim.openstreetmap.org/search', params=params, timeout=20,
                     headers={'User-Agent': USER_AGENT})
    r.raise_for_status()
    hits = r.json()
    if not hits and m:  # postcode unknown to OSM: try the text after it
        time.sleep(1.1)
        params.pop('postalcode')
        params['q'] = location
        hits = requests.get('https://nominatim.openstreetmap.org/search', params=params, timeout=20,
                            headers={'User-Agent': USER_AGENT}).json()
    return [float(hits[0]['lat']), float(hits[0]['lon'])] if hits else None


def _km(a, b):
    lat1, lon1, lat2, lon2 = map(math.radians, (*a, *b))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h)) * ROAD_FACTOR


def consumption(it):
    """(litres per 100 km, fuel) for the drive home."""
    model = it.get('model') or ''
    l100 = next((v for k, v in CONSUMPTION if model.startswith(k)), 10.0)
    if it.get('fuel') == 'diesel':
        return l100, 'diesel'
    if it.get('has_lpg'):
        return round(l100 * LPG_FACTOR, 1), 'lpg'
    return l100, 'benzine'


def update(listings):
    cache = _load()
    lookups = failed = 0
    for it in listings:
        if not it.get('active') or not it.get('location'):
            continue
        key = f"{it['country']}|{it['location']}"
        if key not in cache and lookups < MAX_LOOKUPS:
            lookups += 1
            try:
                cache[key] = _lookup(it['country'], it['location'])
            except Exception:
                failed += 1
            time.sleep(1.1)
        pos = cache.get(key)
        if pos:
            km = _km(pos, HOME)
            l100, fuel = consumption(it)
            it['trip_km'] = round(km)
            it['trip_fuel'] = fuel
            it['trip_cost'] = round(km / 100 * l100 * FUEL_PRICE[fuel])
        else:
            it['trip_km'] = it['trip_cost'] = it['trip_fuel'] = None
    if lookups:
        _save(cache)
        print(f'ritkosten: {lookups} nieuwe plaatsen opgezocht ({failed} mislukt)')
    return listings
