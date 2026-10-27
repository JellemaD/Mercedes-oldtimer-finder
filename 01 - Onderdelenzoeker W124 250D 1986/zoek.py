#!/usr/bin/env python3
"""
Parts finder for the W124 250D (57-RVV-3): search second-hand sites and forum marketplaces for
the parts in onderdelen.json and merge the hits into ../docs/data/onderdelen.json (read by
../docs/onderdelen.html).

Usage:
    python zoek.py                  # all sources
    python zoek.py --only marktplaats

Rules:
- A listing matches a part when title+text match one of the part's 'match' regexes AND mention
  the W124 family (not needed on W124-Board.de). Coupe/cabrio (C124/A124) ads are dropped.
- Hits keep first_seen; a hit not found again by a working source becomes inactive and is
  dropped after DROP_AFTER_DAYS. A failing source leaves its hits untouched.
- Parts with status 'nieuw-kopen', 'besteld' or 'gemonteerd' are not searched.
"""

import argparse
import importlib
import json
import os
import re
import sys
import time
import traceback
from datetime import date, datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)   # sources.common from the car scraper
sys.path.insert(0, HERE)   # bronnen package

ONDERDELEN = os.path.join(HERE, 'onderdelen.json')
OUT = os.path.join(ROOT, 'docs', 'data', 'onderdelen.json')
DROP_AFTER_DAYS = 30
BRONNEN = ['kleinanzeigen', 'marktplaats', 'mercedesforum', 'w124board']
W124_ONLY = {'w124board'}
ZOEKSTATUS = {'zoeken', 'gevonden'}

W124 = re.compile(r'\b(w\s?124|124er|250\s?d|300\s?d|200\s?d|300\s?e|260\s?e|230\s?e|200\s?e|'
                  r'e[\s-]?klasse|e[\s-]?class|mopf\s?0|vormopf|vor-mopf|s124|t-modell)\b', re.I)
NOT = re.compile(r'\b(c124|a124|coup[eé]|cabrio|cabriolet|w123|w201|w126|w202|w210|w140|190\s?[de]|w463|sprinter|'
                 r'amg|bodykit|body\s?kit|side\s?skirts?|sideskirts?)\b', re.I)
KEEP = ('id', 'source', 'country', 'url', 'title', 'price', 'location', 'image', 'attrs')


def load_json(path, default):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def match_parts(item, parts, w124_only):
    """Ids of the parts this listing fits."""
    blob = f"{item['title']} {item.get('text', '')}"
    if NOT.search(blob):
        return []
    if not w124_only and not W124.search(blob):
        return []
    hits = []
    for p in parts:
        if any(re.search(rx, blob, re.I) for rx in p.get('niet', [])):
            continue
        if any(re.search(rx, blob, re.I) for rx in p['match']):
            hits.append(p['id'])
    return hits


def run_source(modname, parts):
    t0 = time.time()
    status = {'module': modname, 'ok': False, 'found': 0, 'matched': 0, 'error': None}
    try:
        mod = importlib.import_module(f'bronnen.{modname}')
        status.update(name=mod.NAME, country=mod.COUNTRY)
        raw = mod.zoek(parts)
    except Exception as e:
        status['error'] = f'{type(e).__name__}: {e}'[:300]
        traceback.print_exc()
        status['secs'] = round(time.time() - t0)
        return status, []
    matched = []
    for item in raw:
        ids = match_parts(item, parts, modname in W124_ONLY)
        if ids:
            out = {k: item.get(k) for k in KEEP}
            out['text'] = (item.get('text') or '')[:300]
            out['onderdelen'] = ids
            out['source_module'] = modname
            matched.append(out)
    status.update(ok=len(raw) > 0, found=len(raw), matched=len(matched), secs=round(time.time() - t0))
    if not raw:
        status['error'] = 'geen resultaten (scraper kapot of geblokkeerd?)'
    return status, matched


def merge(existing, fresh, ok_sources, today):
    by_id = {it['id']: it for it in existing}
    seen = set()
    for it in fresh:
        seen.add(it['id'])
        old = by_id.get(it['id'])
        it['first_seen'] = old.get('first_seen', today) if old else today
        it['price_prev'] = old.get('price') if old and old.get('price') != it.get('price') else (old or {}).get('price_prev')
        it['last_seen'] = today
        it['active'] = True
        by_id[it['id']] = it
    out = []
    for it in by_id.values():
        if it['id'] not in seen and it.get('source_module') in ok_sources:
            it['active'] = False
        gone = (date.fromisoformat(today) - date.fromisoformat(it['last_seen'])).days
        if not it['active'] and gone > DROP_AFTER_DAYS:
            continue
        out.append(it)
    out.sort(key=lambda x: x['first_seen'], reverse=True)
    out.sort(key=lambda x: not x['active'])
    return out


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser()
    ap.add_argument('--only')
    args = ap.parse_args()

    conf = load_json(ONDERDELEN, None)
    if not conf:
        print('onderdelen.json ontbreekt of is ongeldig')
        return 1
    parts = [p for p in conf['onderdelen'] if p['status'] in ZOEKSTATUS and p['match']]
    today = date.today().isoformat()
    data = load_json(OUT, {})
    statuses = {s['module']: s for s in data.get('bronnen', [])}
    fresh, ok_sources, failed = [], set(), []
    for modname in ([args.only] if args.only else BRONNEN):
        print(f'== {modname}', flush=True)
        status, matched = run_source(modname, parts)
        status['last_run'] = datetime.now(timezone.utc).isoformat(timespec='seconds')
        if status['ok']:
            status['last_ok'] = status['last_run']
            ok_sources.add(modname)
        else:
            status['last_ok'] = statuses.get(modname, {}).get('last_ok')
            failed.append(modname)
        statuses[modname] = status
        fresh += matched
        print(f"   gevonden {status['found']}, passend {status['matched']}, {status['secs']}s "
              f"{status['error'] or ''}", flush=True)

    treffers = merge(data.get('treffers', []), fresh, ok_sources, today)
    order = {m: i for i, m in enumerate(BRONNEN)}
    save_json(OUT, {
        'updated': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'auto': conf['auto'],
        'onderdelen': [{k: v for k, v in p.items() if k not in ('zoek', 'match', 'niet')} for p in conf['onderdelen']],
        'treffers': treffers,
        'bronnen': sorted(statuses.values(), key=lambda s: order.get(s['module'], 99)),
    })
    active = sum(1 for t in treffers if t['active'])
    print(f'\nonderdelen.json: {len(treffers)} treffers ({active} actief)')
    for p in conf['onderdelen']:
        n = sum(1 for t in treffers if t['active'] and p['id'] in t['onderdelen'])
        print(f"   {p['id']}: {n}")
    if failed:
        print('BRONNEN ZONDER RESULTAAT: ' + ', '.join(failed))
    return 2 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
