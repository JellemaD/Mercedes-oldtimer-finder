"""
Score 0-100 per listing, with the breakdown shown on the website.

    roest           40  photo check (rust.py): starts at 10; rust elsewhere -2/-4/-6, wheel arches
                        -3/-5/-8, sills -5/-8/-10 (count extra heavy), sills not visible -3;
                        not checked = 6. AI says W123/other model: score 0, hidden (ai_reject)
    motor           18  diesel 250D/300D = 10, 190D 2.5 = 9; petrol by LPG score (3=10, 2=8, 1=6, 0=3)
    staat           12  starts at 5; good words in the ad +1.5 each, bad words -2.5 each
    kilometerstand  12  diesel: 0 km = 10, 500,000 km = 0; petrol: 0 km = 10, 350,000 km = 0
    prijs            9  price against the median of the same model in today's list
    bouwjaar         6  1987 = 10 ... 1982 = 5
    al op LPG       +3  petrol car that already has an LPG installation
(Rust was added at 40%; the other parts kept their mutual proportions, scaled to 60%.)

condition_signals() needs the ad text, so scrape.py calls it per listing; score_all() needs the
whole list (median prices), so scrape.py calls it after the merge.
"""

import re
from statistics import median

WEIGHTS = {'roest': 4.0, 'motor': 1.8, 'staat': 1.2, 'km': 1.2, 'prijs': 0.9, 'bouwjaar': 0.6}
LPG_BONUS = 3
UNKNOWN = 4.0  # points (of 10) for a missing km, price or year: a bit below average
RUST_OTHER = {0: 0, 1: 2, 2: 4, 3: 6}
RUST_ARCHES = {0: 0, 1: 3, 2: 5, 3: 8}
RUST_SILLS = {0: 0, 1: 5, 2: 8, 3: 10}  # sills count extra heavy
SILLS_UNSEEN = 3
RUST_UNCHECKED = 6.0  # below "nothing seen" (7), above "a little rust on the sills" (5)

GOOD = {
    'roestvrij': r'roestvrij|rostfrei|ohne rost|kein rost|sin [oó]xido|sem ferrugem|χωρ[ίι]ς σκουρι',
    'H-kenteken': r'\bh-?(?:kennzeichen|zulassung|gutachten|kz)\b|wertgutachten|oldtimergutachten',
    'onderhoudshistorie': r'scheckheft|onderhoudsboek|onderhoudshistorie|historial de mantenimiento'
                          r'|libro de (?:mantenimiento|revisiones)|livro de revis|βιβλ[ίι]ο σ[έε]ρβις',
    'keuring geldig': r't[üu]v neu|t[üu]v bis|hu neu|hu bis|apk (?:tot|t/m|nieuw)|itv (?:en vigor|pasada|reciente)'
                      r'|inspe[cç][aã]o (?:em dia|v[aá]lida)|κτεο',
    'weinig eigenaren': r'\b1\.? ?hand\b|erste hand|aus erster hand|eerste eigenaar|1e eigenaar|[uú]nico (?:due[ñn]o|propietario)'
                        r'|primeiro dono|πρ[ώω]το χ[έε]ρι',
    'garage/droog gestald': r'garagenwagen|garagenfahrzeug|altijd binnen|binnen gestald|trocken untergestellt|siempre en garaje',
    'NAP/km-bewijs': r'\bnap\b|nachweisbar|km-?nachweis',
}
BAD = {
    'roest': r'\brost(?:stellen|schaden|loch|l[öo]cher|blasen|ansatz)|durchgerostet|\broest(?:plek|vorming|schade)'
             r'|doorgeroest|\b[oó]xido en|ferrugem (?:na|no)|σκουρι[άα] σε',
    'motor/bak defect': r'motorschaden|motorschade|getriebeschaden|versnellingsbak defect|kopfdichtung defekt'
                        r'|\bdefekt\b|\bdefect\b|kapot|averiad|avariad|χαλασμ[έε]ν',
    'rijdt niet': r'springt nicht an|f[äa]hrt nicht|start niet|loopt niet|no arranca|n[ãa]o (?:anda|pega)|δεν παν',
    'opknapper/sloop': r'bastler|opknapper|restauratie(?:project|object)|restaurationsobjekt|projektaufgabe'
                       r'|ersatzteilspender|teileträger|para (?:pe[çc]as|piezas)|sloop|scheunenfund|barn ?find',
    'geen keuring': r'ohne t[üu]v|kein t[üu]v|t[üu]v abgelaufen|zonder apk|geen apk|sin itv|itv caducada|sem inspe',
    'schade/ongeval': r'unfall(?!frei)|unfallwagen|schadeauto|met schade|aanrijding|siniestrad|acidentad',
    'export/handelaar': r'\bexport\b|h[äa]ndler ?(?:export|preis)|nur f[üu]r h[äa]ndler',
}
_GOOD = {k: re.compile(v) for k, v in GOOD.items()}
_BAD = {k: re.compile(v) for k, v in BAD.items()}

YEAR_POINTS = {1987: 10, 1986: 9, 1985: 8, 1984: 7, 1983: 6, 1982: 5}


def condition_signals(text):
    """(good, bad): lists of signal names found in title + description."""
    t = (text or '').lower()
    return [k for k, rx in _GOOD.items() if rx.search(t)], [k for k, rx in _BAD.items() if rx.search(t)]


def _rust(it):
    r = it.get('rust')
    if not r:
        return RUST_UNCHECKED
    sills = SILLS_UNSEEN if r.get('sills') is None else RUST_SILLS[r['sills']]
    return max(0.0, 10.0 - RUST_OTHER[r.get('other') or 0] - RUST_ARCHES[r.get('arches') or 0] - sills)


def _motor(it):
    if it['fuel'] == 'diesel':
        return 9.0 if it['model'].startswith('190') else 10.0
    return {3: 10.0, 2: 8.0, 1: 6.0}.get(it.get('lpg_score') or 0, 3.0)


def _km(it):
    km = it.get('mileage')
    if not km or km < 1000:  # missing, or given in thousands/miles: don't guess
        return UNKNOWN
    return max(0.0, 10.0 - km / (50000 if it['fuel'] == 'diesel' else 35000))


def _price(it, medians):
    p, m = it.get('price'), medians.get(_group(it))
    if not p or not m:
        return UNKNOWN
    return max(0.0, min(10.0, 10.0 - (p / m - 0.6) * 10))  # 60% of median = 10, 160% = 0


def _group(it):
    model = re.sub(r'(?<=\d)(?:TE|CE|TD|E|T|D)\b', '', it.get('model') or '')  # 230TE ~ 230E ~ 230
    return model or it.get('series'), it.get('fuel')


def _medians(items):
    groups = {}
    for it in items:
        if it.get('price') and it.get('active', True) and not it.get('dup_of'):
            groups.setdefault(_group(it), []).append(it['price'])
    return {g: median(v) for g, v in groups.items() if len(v) >= 4}


def score_all(items):
    """Adds score, punten (breakdown) and let_op to every listing."""
    medians = _medians(items)
    for it in items:
        good, bad = it.get('signals_good') or [], it.get('signals_bad') or []
        parts = {
            'roest': _rust(it),
            'motor': _motor(it),
            'staat': max(0.0, min(10.0, 5 + 1.5 * len(good) - 2.5 * len(bad))),
            'km': _km(it),
            'prijs': _price(it, medians),
            'bouwjaar': YEAR_POINTS.get(it.get('year'), UNKNOWN),
        }
        punten = {k: round(WEIGHTS[k] * v, 1) for k, v in parts.items()}
        if it['fuel'] == 'benzine' and it.get('has_lpg'):
            punten['al op LPG'] = LPG_BONUS
        it['punten'] = punten
        it['score'] = round(min(100.0, sum(punten.values())), 1)
        it['ai_reject'] = (it.get('rust') or {}).get('chassis') in ('W123', 'ander')
        if it['ai_reject']:
            it['score'] = 0.0

        let_op = []
        r = it.get('rust') or {}
        if (r.get('sills') or 0) >= 1:
            let_op.append(['', 'Beetje roest op dorpels', 'Roest op dorpels', 'Veel roest op dorpels'][r['sills']])
        if (r.get('other') or 0) >= 2:
            let_op.append('Roest zichtbaar op foto')
        if (r.get('arches') or 0) >= 1:
            let_op.append(['', 'Beetje roest wielkasten', 'Roest wielkasten', 'Veel roest wielkasten'][r['arches']])
        if it.get('maybe_w123'):
            let_op.append('Mogelijk W123: check chassisnummer (WDB124… = W124)')
        if not it.get('year_known'):
            let_op.append('Bouwjaar onbekend')
        if (it.get('mileage') or 0) > 300000:
            let_op.append('Hoge kilometerstand')
        if it.get('model') == '190E 2.3-16':
            let_op.append('16V Cosworth: niet geschikt voor LPG')
        if it['fuel'] == 'benzine' and it.get('has_lpg'):
            let_op.append('LPG-installatie: keuring en tankdatum checken')
        if '4' in (it.get('title') or '').lower() and 'matic' in (it.get('title') or '').lower():
            let_op.append('4MATIC: duur in onderhoud')
        let_op += [f'Advertentie noemt: {b}' for b in bad]
        it['let_op'] = let_op
    return items
