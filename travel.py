"""
Cost of driving the car home yourself: distance from the seller to HOME x consumption x fuel price.

- Location -> coordinates via OpenStreetMap Nominatim (max 1 request/s, cached per location string in
  docs/data/geo.json, so each place is looked up once).
- Road distance = straight line x ROAD_FACTOR (rough; islands also need a ferry, not included).
- Consumption per model on the motorway (litres/100 km, indicative for an 80s car); a petrol car that
  already runs on LPG drives home on LPG (1.2 x the petrol litres).
- Fuel prices: EU averages, week of 5 Oct 2026 (EU Oil Bulletin via fuel-prices.eu); LPG estimated.
- Two routes: 'toll' (fastest motorway, with tolls/vignettes: France ~0.095 euro/km, Italy ~0.075
  euro/km + Swiss vignette CHF 40, flat estimates for Spain, Portugal, the Balkans) and 'free'
  (binnendoor: ~15% more km, slower, no tolls). Ferries from Sicily/Sardinia count on both.
  The trip to the car itself is not included.

update(listings) adds trip = {fuel, l100, toll: {...}, free: {...}} and trip_cost (cheapest route,
used by the score) to every active listing with a known location.
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

# Tolls 2026 (estimates; see the docstring): France ~0.095 euro/km (class 1), Italy ~0.075 euro/km,
# Swiss vignette CHF 40 (~43 euro, annual only), flat amounts for Spain, Portugal and the Balkans.
TOLL_PER_KM = {'FR': 0.095, 'IT': 0.075}
TOLL_FLAT = {'ES': 15, 'PT': 20, 'GR': 90}
VIGNETTE_CH = 43
KM_FRANCE_TRANSIT = 1000      # Spanish border -> Belgian border on the autoroute
KM_HOME_FROM_FR_NORTH = 330   # Belgian border (Lille) -> Soest, toll-free
ITALY_EXIT = (45.83, 9.03)    # Chiasso, towards the Gotthard
FERRY = {'sicily': 40, 'sardinia': 200}
DETOUR_TOLL_FREE = 1.15       # toll-free roads: ~15% more km
SPEED = {'motorway': 95, 'binnendoor': 65}  # average km/h incl. stops
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


def _ferry(country, pos):
    """Unavoidable ferry from the islands (both routes)."""
    lat, lon = pos
    if country == 'IT' and lat < 38.4 and lon > 12.3:
        return FERRY['sicily']
    if country == 'IT' and lon < 10.0 and lat < 41.4:
        return FERRY['sardinia']
    return 0


def _toll(country, pos, km):
    """Estimated tolls and vignettes on the fastest motorway route to HOME."""
    if country == 'FR':
        return TOLL_PER_KM['FR'] * max(0, km - KM_HOME_FROM_FR_NORTH)
    if country in ('ES', 'PT'):
        extra = TOLL_FLAT['ES'] + (TOLL_FLAT['PT'] if country == 'PT' else 0)
        return TOLL_PER_KM['FR'] * KM_FRANCE_TRANSIT + extra
    if country == 'IT':
        return TOLL_PER_KM['IT'] * _km(pos, ITALY_EXIT) + VIGNETTE_CH
    if country == 'GR':
        return TOLL_FLAT['GR']
    return 0


def _routes(it, pos):
    """Both ways home: fastest (motorway, tolls) and 'binnendoor' (toll-free, longer and slower)."""
    km = _km(pos, HOME)
    l100, fuel = consumption(it)
    ferry = _ferry(it['country'], pos)
    has_toll = _toll(it['country'], pos, km) > 0
    km_free = km * (DETOUR_TOLL_FREE if has_toll else 1.0)

    def route(dist, toll, speed):
        fuel_cost = dist / 100 * l100 * FUEL_PRICE[fuel]
        return {'km': round(dist), 'fuel_cost': round(fuel_cost), 'toll': round(toll + ferry),
                'cost': round(fuel_cost + toll + ferry), 'hours': round(dist / speed, 1)}

    return {'fuel': fuel, 'l100': l100,
            'toll': route(km, _toll(it['country'], pos, km), SPEED['motorway']),
            'free': route(km_free, 0, SPEED['motorway'] if not has_toll else SPEED['binnendoor'])}


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
        it['trip'] = _routes(it, pos) if pos else None
        # trip_cost = cheapest route, used by the score; the site lets you pick the route
        it['trip_cost'] = min(it['trip']['toll']['cost'], it['trip']['free']['cost']) if pos else None
        for old in ('trip_km', 'trip_fuel'):
            it.pop(old, None)
    if lookups:
        _save(cache)
        print(f'ritkosten: {lookups} nieuwe plaatsen opgezocht ({failed} mislukt)')
    return listings
