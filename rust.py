"""
Rust check on the listing photos with Claude (vision).

Per listing the model gets up to MAX_IMAGES photos and reports:
    sills  0-3 or None  rust on the sills (dorpels), jacking points, lower door edges; None = not visible
    other  0-3          rust anywhere else (wheel arches, wings, boot lid, around windows)
    note   short Dutch remark shown on the site
Levels: 0 none, 1 a little (bubbles, small spots), 2 clear rust, 3 heavy (holes, large areas).

Results are cached in docs/data/rust.json per listing id (and its photo urls), so every car is
checked once. Without ANTHROPIC_API_KEY nothing is checked and the score treats rust as unknown.
The best TOP (15) cars on final score stay checked: check, rescore, repeat until the whole top 15
has a result (a rusty car drops out, the next moves up), at most MAX_CHECKS (30) model calls per run.
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
TOP = int(os.environ.get('RUST_TOP', '15'))  # the best TOP cars on final score stay rust-checked
MAX_CHECKS = int(os.environ.get('RUST_MAX_CHECKS', '30'))  # hard cap on model calls per run
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


def _attach(listings, cache):
    for it in listings:
        c = cache.get(it['id'])
        it['rust'] = {k: c[k] for k in ('sills', 'other', 'note', 'photos')} if c and not c.get('unusable') else None


def _todo(listings, cache, skip):
    """Cars in the current top TOP (final score) without a rust result for their current photos."""
    top = sorted((it for it in listings if it.get('active') and not it.get('dup_of')),
                 key=lambda it: it.get('score') or 0, reverse=True)[:TOP]
    out = []
    for it in top:
        urls, key = _photos_key(it)
        if urls and it['id'] not in skip and cache.get(it['id'], {}).get('key') != key:
            out.append((it, urls, key))
    return out


def update(listings, rescore):
    """Keep the top TOP on final score rust-checked: check the unchecked ones, rescore, repeat
    (a rusty car drops out, the next one moves up and gets checked), at most MAX_CHECKS per run.
    rescore(listings) recomputes the scores (score.score_all). Returns the rescored listings."""
    cache = load_cache()
    active_ids = {it['id'] for it in listings}
    for k in [k for k in cache if k not in active_ids]:  # cars that dropped out of the list
        del cache[k]
    _attach(listings, cache)
    rescore(listings)

    if not os.environ.get('ANTHROPIC_API_KEY'):
        waiting = len(_todo(listings, cache, set()))
        if waiting:
            print(f"roestcheck: overgeslagen (geen ANTHROPIC_API_KEY), {waiting} auto's in de top {TOP} wachten")
    else:
        import anthropic
        client = anthropic.Anthropic()
        checks = errors = 0
        skip = set()  # failed this run: don't retry in the loop
        while checks < MAX_CHECKS and errors < 5:
            todo = _todo(listings, cache, skip)
            if not todo:
                break
            for it, urls, key in todo[:MAX_CHECKS - checks]:
                checks += 1
                try:
                    res = check(client, urls)
                except Exception as e:
                    errors += 1
                    skip.add(it['id'])
                    print(f'   roestcheck fout ({it["id"]}): {type(e).__name__}: {str(e)[:200]}', file=sys.stderr)
                    if errors >= 5:
                        print('   roestcheck gestopt na 5 fouten', file=sys.stderr)
                        break
                    continue
                entry = dict(res, key=key) if res else {'key': key, 'unusable': True}  # no usable photo
                cache[it['id']] = dict(entry, model=MODEL, date=date.today().isoformat())
            _attach(listings, cache)
            rescore(listings)
        left = len(_todo(listings, cache, skip))
        cost = (USAGE['input'] * PRICE[0] + USAGE['output'] * PRICE[1]) / 1e6
        print(f'roestcheck: {checks} checks ({errors} fouten), top {TOP} '
              f'{"volledig gecheckt" if not left else f"nog {left} open"}; {USAGE["input"]} input- en '
              f'{USAGE["output"]} output-tokens, ca. ${cost:.2f} ({MODEL})')
    save_cache(cache)
    return listings
