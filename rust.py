"""
Rust check on the listing photos with Claude (vision).

Per listing the model gets up to FIRST_IMAGES photos and reports:
    sills    0-3 or None  rust on the sills (dorpels), jacking points, lower door edges; None = not visible
                          (the model must name the photo that shows them, else None)
    arches   0-3          rust on/around the wheel arches
    other    0-3          rust anywhere else (wings, door edges, boot lid, around windows)
    chassis  W124 / W201 / W123 / ander / onzeker   which car the photos show
    note     short Dutch remark shown on the site
Levels: 0 none, 1 a little (bubbles, small spots), 2 clear rust, 3 heavy (holes, large areas).

All photos of the ad are sent (up to MAX_PHOTOS); when the search result has few, the ad page is
read via the source's detail_images(). The AI saying W123/ander removes the car from the site
(score.py sets ai_reject).

Results are cached in docs/data/rust.json per listing id (and its photo urls), so every car is
checked once. Without ANTHROPIC_API_KEY nothing is checked and the score treats rust as unknown.
The best TOP (15) cars on final score stay checked: check, rescore, repeat until the whole top 15
has a result (a rusty car drops out, the next moves up), at most MAX_CHECKS (30) model calls per run.
"""

import base64
import hashlib
import importlib
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
FIRST_IMAGES = 4  # photos that identify a listing's photo set (cache key)
MAX_PHOTOS = 16   # photos sent per car; fewer in the search result -> ad page via detail_images()
MAX_SIDE = 800    # px; photos are scaled down before sending (fewer tokens, rust still visible)
VERSION = 3       # bump to re-check every car (v2: all ad photos, sills photo named; v3: Kleinanzeigen both layouts)
CHASSIS = ['W124', 'W201', 'W123', 'ander', 'onzeker']

PROMPT = """Dit zijn foto's (genummerd 1, 2, 3 ... in volgorde) uit een advertentie voor een Mercedes
W124 of W201 (190) uit de jaren 80. Een koper wil weten of er roest is. Bekijk ELKE foto apart.
- sills_photo: het nummer van de foto waarop de dorpels (onder de deuren, inclusief de onderkant van
  de deuren en de krikpunten) van dichtbij of halfdichtbij duidelijk te zien zijn; 0 als geen enkele
  foto dat laat zien. Een vooraanzicht, achteraanzicht of een zijaanzicht van grote afstand telt NIET:
  daarop kun je roest op de dorpels niet beoordelen. Zeg nooit dat de dorpels schoon zijn als je ze
  niet echt ziet.
- sills: roest op de dorpels, de onderkant van de deuren en de krikpunten; -1 als sills_photo 0 is.
- arches: roest op of rond de wielkasten (wielranden van de spatborden, voor en achter), op welke foto
  dan ook.
- other: roest op de rest van de carrosserie (spatborden buiten de wielkast, deurranden, kofferklep,
  rond de ruiten, onderkant van de bumpers), op welke foto dan ook.
  Niveaus: 0 = geen roest te zien, 1 = een beetje (blaasjes, kleine plekjes), 2 = duidelijke roest,
  3 = veel roest (gaten, grote plekken, doorgeroest). Twijfel tussen twee niveaus: kies het hoogste.
  Roest bij de onderkant van een deur boven de dorpel telt als dorpelroest.
- chassis: welke auto staat op de foto's? W124 (E-klasse 1984-1995), W201 (190), W123 (voorganger
  van de W124, met verchroomde staande koplampen en hoekiger lijnen), ander (ander model) of onzeker.
note: één korte Nederlandse zin (max 15 woorden) over wat je ziet, of waarom je het niet kunt zien."""

SCHEMA = {
    'type': 'object',
    'properties': {
        'sills_photo': {'type': 'integer'},  # 1-based photo number showing the sills, 0 = none
        'sills': {'type': 'integer', 'enum': [-1, 0, 1, 2, 3]},  # -1 = not visible
        'arches': {'type': 'integer', 'enum': [0, 1, 2, 3]},
        'other': {'type': 'integer', 'enum': [0, 1, 2, 3]},
        'chassis': {'type': 'string', 'enum': CHASSIS},
        'note': {'type': 'string'},
    },
    'required': ['sills_photo', 'sills', 'arches', 'other', 'chassis', 'note'],
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


def _photos(it):
    return it.get('images') or ([it['image']] if it.get('image') else [])


def _key(it):
    return hashlib.sha1('|'.join(_photos(it)[:FIRST_IMAGES]).encode()).hexdigest()[:12]


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
    """Ask the model about one set of photos. Returns dict or None (no usable photo / refusal)."""
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
    if out['sills'] < 0 or not 1 <= out.get('sills_photo', 0) <= len(blocks):
        out['sills'] = None  # no photo actually shows the sills: never count them as clean
    out['photos'] = len(blocks)
    return out


def _all_photos(it):
    """All photos of the ad, up to MAX_PHOTOS. Search results often carry only 1-4 (Kleinanzeigen: 1,
    a front view): then the ad page is read via the source's detail_images()."""
    photos = _photos(it)[:MAX_PHOTOS]
    if len(photos) >= 6:
        return photos
    try:
        mod = importlib.import_module(f"sources.{it.get('source_module')}")
        more = getattr(mod, 'detail_images', lambda url: [])(it['url'])
    except Exception as e:
        print(f'   advertentiefoto\'s ({it["id"]}): {type(e).__name__}: {str(e)[:150]}', file=sys.stderr)
        more = []
    bases = {u.split('?')[0] for u in photos}
    return (photos + [u for u in more if u.split('?')[0] not in bases])[:MAX_PHOTOS]


def _valid(entry, key):
    return entry and entry.get('key') == key and entry.get('v') == VERSION


def _attach(listings, cache):
    for it in listings:
        c = cache.get(it['id'])
        it['rust'] = ({k: c.get(k) for k in ('sills', 'arches', 'other', 'chassis', 'note', 'photos')}
                      if c and not c.get('unusable') else None)


def _todo(listings, cache, skip):
    """Cars in the current top TOP (final score) without a current rust result."""
    top = sorted((it for it in listings if it.get('active') and not it.get('dup_of')),
                 key=lambda it: it.get('score') or 0, reverse=True)[:TOP]
    return [it for it in top if _photos(it) and it['id'] not in skip and not _valid(cache.get(it['id']), _key(it))]


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
        checks = errors = photos = 0
        skip = set()  # failed this run: don't retry in the loop
        while checks < MAX_CHECKS and errors < 5:
            todo = _todo(listings, cache, skip)
            if not todo:
                break
            for it in todo:
                if checks >= MAX_CHECKS or errors >= 5:
                    break
                try:
                    checks += 1
                    res = check(client, _all_photos(it))
                    photos += res['photos'] if res else 0
                except Exception as e:
                    errors += 1
                    skip.add(it['id'])
                    print(f'   roestcheck fout ({it["id"]}): {type(e).__name__}: {str(e)[:200]}', file=sys.stderr)
                    continue
                entry = dict(res, key=_key(it), v=VERSION) if res else {'key': _key(it), 'v': VERSION, 'unusable': True}
                cache[it['id']] = dict(entry, model=MODEL, date=date.today().isoformat())
            _attach(listings, cache)
            rescore(listings)
        left = len(_todo(listings, cache, skip))
        cost = (USAGE['input'] * PRICE[0] + USAGE['output'] * PRICE[1]) / 1e6
        print(f'roestcheck: {checks} auto\'s, {photos} foto\'s ({errors} fouten), top {TOP} '
              f'{"volledig gecheckt" if not left else f"nog {left} open"}; {USAGE["input"]} input- en '
              f'{USAGE["output"]} output-tokens, ca. ${cost:.2f} ({MODEL})')
    save_cache(cache)
    return listings
