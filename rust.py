"""
Rust check on the listing photos with Claude (vision).

Per listing the model gets up to MAX_IMAGES photos and reports:
    sills  0-3 or None  rust on the sills (dorpels), jacking points, lower door edges; None = not visible
    other  0-3          rust anywhere else (wheel arches, wings, boot lid, around windows)
    note   short Dutch remark shown on the site
Levels: 0 none, 1 a little (bubbles, small spots), 2 clear rust, 3 heavy (holes, large areas).

Results are cached in docs/data/rust.json per listing id (and its photo urls), so every car is
checked once. Without ANTHROPIC_API_KEY nothing is checked and the score treats rust as unknown.
Only the best TOP (25) cars by score-without-rust are checked; each day only newcomers to that top.
"""

import base64
import hashlib
import io
import json
import os
import re
import sys
from datetime import date

import requests

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, 'docs', 'data', 'rust.json')
MODEL = os.environ.get('RUST_MODEL', 'claude-opus-5-5')
TOP = int(os.environ.get('RUST_TOP', '25'))  # only the best TOP cars get a rust check
PRICE = {'claude-opus-5-5': (4.0, 20.0), 'claude-sonnet-5-5': (2.0, 10.0),
         'claude-haiku-5-5': (0.10, 0.50)}.get(MODEL, (4.0, 20.0))  # $ per million tokens in/out
USAGE = {'input': 0, 'output': 0}
MAX_IMAGES = 4
MAX_SIDE = 1024  # px; photos are scaled down before sending (fewer tokens, under the size limit)

PROMPT = """Dit zijn foto's uit een advertentie voor een Mercedes W124 of W201 (190) uit de jaren 80.
Beoordeel alleen roest, zo nauwkeurig mogelijk:
- sills: roest op de dorpels (onder de deuren), de krikpunten en de onderkant van de deuren.
  Gebruik -1 als de dorpels op geen enkele foto goed genoeg te zien zijn om te beoordelen.
- other: roest op de rest van de carrosserie (wielkasten, spatborden, kofferklep, rond de ruiten,
  onderkant van de bumpers).
Niveaus: 0 = geen roest te zien, 1 = een beetje (blaasjes, kleine plekjes), 2 = duidelijke roest,
3 = veel roest (gaten, grote plekken). Twijfel tussen twee niveaus: kies het hoogste.
note: één korte Nederlandse zin (max 15 woorden) over wat je ziet, of waarom je het niet kunt zien."""

SCHEMA = {
    'type': 'object',
    'properties': {
        'sills': {'type': 'integer', 'enum': [-1, 0, 1, 2, 3]},  # -1 = not visible
        'other': {'type': 'integer', 'enum': [0, 1, 2, 3]},
        'note': {'type': 'string'},
    },
    'required': ['sills', 'other', 'note'],
    'additionalProperties': False,
}


def load_cache():
    try:
        with open(CACHE, encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return {}


def save_cache(cache):
    tmp = CACHE + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=1)
    os.replace(tmp, CACHE)


def _photos_key(it):
    urls = (it.get('images') or ([it['image']] if it.get('image') else []))[:MAX_IMAGES]
    return urls, hashlib.sha1('|'.join(urls).encode()).hexdigest()[:12]


def larger(url):
    """Search results often carry thumbnails (147 px); rust needs a bigger version where one exists."""
    url = url.replace('rule=ecg_mp_eps$_82', 'rule=ecg_mp_eps$_85')        # Marktplaats, 2dehands
    url = re.sub(r'/\d+x\d+\.webp$', '/1280x960.webp', url)                # AutoScout24
    url = re.sub(r'(static\.car\.gr/\d+_\d+)_n\.jpg$', r'\1_b.jpg', url)    # car.gr
    return url


def _image_block(url):
    """Download (bigger version), scale down and base64-encode one photo; None if it fails."""
    from PIL import Image
    try:
        r = requests.get(larger(url), timeout=20, headers={'User-Agent': 'Mozilla/5.0'})
        r.raise_for_status()
        im = Image.open(io.BytesIO(r.content)).convert('RGB')
        im.thumbnail((MAX_SIDE, MAX_SIDE))
        buf = io.BytesIO()
        im.save(buf, 'JPEG', quality=85)
    except Exception:
        return None
    return {'type': 'image', 'source': {'type': 'base64', 'media_type': 'image/jpeg',
                                        'data': base64.standard_b64encode(buf.getvalue()).decode()}}


def check(client, urls):
    """Ask the model about one listing. Returns dict or None (no usable photo / refusal / error)."""
    blocks = [b for b in (_image_block(u) for u in urls) if b]
    if not blocks:
        return None
    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        output_config={'effort': 'low', 'format': {'type': 'json_schema', 'schema': SCHEMA}},
        messages=[{'role': 'user', 'content': blocks + [{'type': 'text', 'text': PROMPT}]}],
    )
    USAGE['input'] += response.usage.input_tokens
    USAGE['output'] += response.usage.output_tokens
    if response.stop_reason == 'refusal':
        return None
    text = next((b.text for b in response.content if b.type == 'text'), '')
    out = json.loads(text)
    if out['sills'] < 0:
        out['sills'] = None
    out['photos'] = len(blocks)
    return out


def _rank(it):
    """Score without the rust part, so checking rust doesn't shuffle who is in the top."""
    return sum(v for k, v in (it.get('punten') or {}).items() if k != 'roest')


def update(listings):
    """Check the TOP best cars that have no rust result yet (if an API key is set), then attach
    cached results to all listings."""
    cache = load_cache()
    top = sorted((it for it in listings if it.get('active') and not it.get('dup_of')), key=_rank, reverse=True)[:TOP]
    todo = []
    for it in top:
        urls, key = _photos_key(it)
        if urls and cache.get(it['id'], {}).get('key') != key:
            todo.append((it, urls, key))

    if todo and os.environ.get('ANTHROPIC_API_KEY'):
        import anthropic
        client = anthropic.Anthropic()
        done = errors = 0
        for it, urls, key in todo:
            try:
                res = check(client, urls)
            except Exception as e:
                errors += 1
                if errors <= 3:
                    print(f'   roestcheck fout ({it["id"]}): {type(e).__name__}: {str(e)[:200]}', file=sys.stderr)
                if errors >= 10:
                    print('   roestcheck gestopt na 10 fouten', file=sys.stderr)
                    break
                continue
            if res is not None:
                cache[it['id']] = dict(res, key=key, model=MODEL, date=date.today().isoformat())
                done += 1
        cost = (USAGE['input'] * PRICE[0] + USAGE['output'] * PRICE[1]) / 1e6
        print(f'roestcheck: {done} van de top {TOP} beoordeeld ({errors} fouten), {USAGE["input"]} input- en '
              f'{USAGE["output"]} output-tokens, ca. ${cost:.2f} ({MODEL})')
    elif todo:
        print(f'roestcheck: overgeslagen (geen ANTHROPIC_API_KEY), {len(todo)} auto\'s wachten')

    active_ids = {it['id'] for it in listings}
    for k in [k for k in cache if k not in active_ids]:  # cars that dropped out of the list
        del cache[k]
    save_cache(cache)
    for it in listings:
        c = cache.get(it['id'])
        it['rust'] = {k: c[k] for k in ('sills', 'other', 'note', 'photos')} if c else None
    return listings
