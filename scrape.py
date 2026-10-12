#!/usr/bin/env python3
"""
Run the source scrapers, keep listings that fit the profile (classify.py) and merge them into
docs/data/listings.json, which the website reads.

Usage:
    python scrape.py                    # all sources
    python scrape.py --runner github    # only sources that work from GitHub runners
    python scrape.py --runner laptop    # only sources that need the laptop (car.gr)
    python scrape.py --only wallapop    # one source module

Merge rules:
- A listing keeps its first_seen date; last_seen is updated every time it is found again.
- If a source ran fine but a listing was not found again, it is marked inactive (sold/removed)
  and dropped DROP_AFTER_DAYS later.
- If a source failed or returned nothing, its listings are left untouched (scraper broken,
  not the cars gone). docs/data/status.json shows per source what happened.
- Each run only touches its own sources, so the GitHub job and the laptop job can both write.
"""

import argparse
import importlib
import json
import os
import sys
import time
import traceback
from datetime import date, datetime, timezone

from classify import classify
import rust
from score import condition_signals, score_all

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, 'docs', 'data')
LISTINGS = os.path.join(DATA, 'listings.json')
STATUS = os.path.join(DATA, 'status.json')
DROP_AFTER_DAYS = 30

# Module names in sources/ (order = order on the site)
SOURCES = ['marktplaats', 'tweedehands', 'autoscout24', 'kleinanzeigen', 'coches_net', 'wallapop',
           'standvirtual', 'custojusto', 'olx_pt', 'car_gr']

KEEP_FIELDS = ('id', 'source', 'country', 'url', 'title', 'price', 'year', 'mileage', 'location', 'image',
               'images')
CLASS_FIELDS = ('series', 'model', 'fuel', 'cyl', 'lpg_score', 'has_lpg', 'year_known', 'maybe_w123')


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


def run_source(modname):
    """Scrape one source module. Returns (status dict, matched listings)."""
    t0 = time.time()
    status = {'module': modname, 'ok': False, 'found': 0, 'matched': 0, 'error': None}
    try:
        mod = importlib.import_module(f'sources.{modname}')
        status.update(name=mod.NAME, country=mod.COUNTRY, runner=mod.RUNNER)
        raw = mod.scrape()
    except Exception as e:
        status['error'] = f'{type(e).__name__}: {e}'[:300]
        traceback.print_exc()
        status['secs'] = round(time.time() - t0)
        return status, []
    matched = []
    for item in raw:
        attrs = dict(item.get('attrs') or {}, constructionYear=item.get('year'), fuel=item.get('fuel'))
        c = classify(item['title'], item.get('text', ''), attrs, price=item.get('price'))
        if c['match']:
            out = {k: item.get(k) for k in KEEP_FIELDS}
            out.update({k: c[k] for k in CLASS_FIELDS})
            out['year'] = c['year']
            out['signals_good'], out['signals_bad'] = condition_signals(f"{item['title']} {item.get('text', '')}")
            matched.append(out)
    status.update(ok=len(raw) > 0, found=len(raw), matched=len(matched), secs=round(time.time() - t0))
    if not raw:
        status['error'] = 'geen resultaten (scraper kapot of geblokkeerd?)'
    return status, matched


def merge(existing, fresh, ok_sources, today):
    """existing: list from listings.json; fresh: matched listings of this run."""
    by_id = {it['id']: it for it in existing}
    seen_now = set()
    for it in fresh:
        seen_now.add(it['id'])
        old = by_id.get(it['id'])
        if old:
            if old.get('price') and it.get('price') and old['price'] != it['price']:
                it['price_prev'] = old['price']
            else:
                it['price_prev'] = old.get('price_prev')
            it['first_seen'] = old.get('first_seen', today)
        else:
            it['first_seen'] = today
            it['price_prev'] = None
        it['last_seen'] = today
        it['active'] = True
        by_id[it['id']] = it
    out = []
    for it in by_id.values():
        if it['id'] not in seen_now and it.get('source_module') in ok_sources:
            it['active'] = False
        days_gone = (date.fromisoformat(today) - date.fromisoformat(it['last_seen'])).days
        if not it['active'] and days_gone > DROP_AFTER_DAYS:
            continue
        out.append(it)
    out.sort(key=lambda x: x['first_seen'], reverse=True)
    out.sort(key=lambda x: not x['active'])  # stable: active first, newest first
    mark_duplicates(out)
    return out


def mark_duplicates(items):
    """Same car on two sites (Standvirtual + OLX, or AutoScout24 .nl + .de): same model, year, price.
    The oldest listing stays; the others get dup_of and are listed under 'also_on'."""
    first = {}
    for it in sorted(items, key=lambda x: x['first_seen']):
        it['dup_of'], it['also_on'] = None, []
        if not (it['active'] and it.get('model') and it.get('year') and it.get('price')):
            continue
        key = (it['model'], it['year'], it['price'])
        if key in first and (first[key]['source'], first[key]['country']) != (it['source'], it['country']):
            it['dup_of'] = first[key]['id']
            first[key]['also_on'].append({'source': it['source'], 'url': it['url']})
        else:
            first.setdefault(key, it)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser()
    ap.add_argument('--runner', choices=['github', 'laptop', 'all'], default='all')
    ap.add_argument('--only')
    args = ap.parse_args()

    today = date.today().isoformat()
    statuses = {s['module']: s for s in load_json(STATUS, {}).get('sources', [])}
    fresh, ok_sources, failed = [], set(), []
    for modname in ([args.only] if args.only else SOURCES):
        try:
            runner = importlib.import_module(f'sources.{modname}').RUNNER
        except ModuleNotFoundError:
            print(f'-- {modname}: module ontbreekt, overgeslagen')
            continue
        if args.runner != 'all' and runner != args.runner:
            continue
        print(f'== {modname}', flush=True)
        status, matched = run_source(modname)
        status['last_run'] = datetime.now(timezone.utc).isoformat(timespec='seconds')
        if status['ok']:
            status['last_ok'] = status['last_run']
            ok_sources.add(modname)
        else:
            status['last_ok'] = statuses.get(modname, {}).get('last_ok')
            failed.append(modname)
        statuses[modname] = status
        for it in matched:
            it['source_module'] = modname
        fresh += matched
        print(f"   gevonden {status['found']}, passend {status['matched']}, "
              f"{status['secs']}s {status['error'] or ''}", flush=True)

    listings = score_all(merge(load_json(LISTINGS, []), fresh, ok_sources, today))
    listings = score_all(rust.update(listings))  # first score picks which cars get the photo check first
    save_json(LISTINGS, listings)
    order = {m: i for i, m in enumerate(SOURCES)}
    save_json(STATUS, {'updated': datetime.now(timezone.utc).isoformat(timespec='seconds'),
                       'sources': sorted(statuses.values(), key=lambda s: order.get(s['module'], 99))})
    active = sum(1 for it in listings if it['active'])
    print(f'\nlistings.json: {len(listings)} advertenties ({active} actief)')
    if failed:
        print('BRONNEN ZONDER RESULTAAT: ' + ', '.join(failed))
    return 2 if failed else 0  # data is saved either way; exit code 2 lets the workflow warn


if __name__ == '__main__':
    sys.exit(main())
