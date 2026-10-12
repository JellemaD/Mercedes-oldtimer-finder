"""
Classify a marketplace listing against the search profile (see PLAN.md).

Profile: Mercedes W124 and W201, built up to and including 1987.
- Diesel: 5 or 6 cylinders only (W124 250D/TD, 300D/TD, 300TD Turbo; W201 190D 2.5).
- Petrol: anything that converts well to LPG, scored 1-3 stars
  (M103 6-cyl: 300E/260E/190E 2.6 = 3; M102 2.3 = 2; M102 2.0 = 1; 190E 2.3-16 = 0).
- Build year decides (up to 31-12-1987). Model names are only rejected for variants that did not
  exist yet in 1987 (220E/280E/320E/500E, E-naming, 300E-24, 250D Turbo, 190D 2.5 Turbo, 2.5-16).

classify(title, text, attrs) -> dict with 'match' plus model details and a 'reason'.
"""

import re

MAX_YEAR = 1987
MIN_YEAR = {'W124': 1984, 'W201': 1982}

# Not a car: scale models, wanted ads, spare parts (title words, several languages)
MODEL_CAR = re.compile(r'hot\s?wheels|norev|maisto|minichamps|schuco|modelauto|miniatur|\b1:(?:18|24|43|64|87)\b')
WANTED = re.compile(r'\b(?:gezocht|gesucht|suche|busco|procuro|ζητείται|wanted)\b')
PARTS = re.compile(
    r'onderde(?:el|len)|deurvanger|deurvastzetter|slotcilinder|contactslot|spiegel|motorkap|kachelpaneel'
    r'|gordel|schakelpook|stappenmotor|stabilisator|sierlijst|subframe|rubbers?\b|\bdeur\b|bumper|koplamp'
    r'|achterlicht|velgen|uitlaat|embleem|grille?\b|hardtop|reparatieset|hoes\b|matten\b|dashboard'
    r'|ersatzteil|\bteile\b|ausschlachten|scheinwerfer|rückleuchte|stoßstange|motorhaube|felgen|\btür\b'
    r'|\bmando\b|\bfunda\b|\bfaro\b|\bfoco\b|\bcopas\b|\bpiloto\b|silencioso|amorte[cs]edor|amortiguador'
    r'|carcasa|espejo|retrovisor|term[oó]metro|potenci[oó]metro|\bbomba\b|\bfarol\b|[oó]tica|\bpisca'
    r'|suporte|dep[oó]sito|pistola|alternador|motor (?:de )?arranque|fechadura|puxador|interruptor'
    r'|resguardo|para-?choques|centralina|volante motor|caixa de velocidades|trav[õo]es|recambio|pe[çc]as?\b'
    r'|ανταλλακτικ|φανάρι|καθρέπτ|πόρτα'
    r'|draagarm|\bstuur\b|motorsteun|schokdemper|relais|\becu\b|motor ?computer|bobine|koppelingsplaat|carter|armleuning'
    r'|dorpel|raammechanisme|ruiten|wielrand|rembekrachtiger|lager\b|hardyschijf|fuseekogel|stuurstang'
    r'|spoorstang|demper|dakdrager|interior|interieur|shroud|radiateur|radiator|ventiel|remschijf|remblok'
    r'|bekleding|spatbord|discos|freno|cenicero|alimentaci[oó]n|chapeleira|complete story|\bboek\b|\bbuch\b')
# A part fits several cars; a car listing names one chassis. "voor/für/para W124" = part.
FITS_FOR = re.compile(r'\b(?:voor|für|fuer|para|for|pour|passend)\s+(?:de\s+|o\s+)?(?:mercedes|w\s?124|w\s?201|190|om\s?60)')
# Modern Mercedes classes ("C 300 e", "GLA 200", "A 250") and modern technology words
MODERN = re.compile(r'\b(?:a|b|c|cl|cla|cls|clk|g|gl|gla|glb|glc|gle|gls|ml|m|r|sl|slk|slc|v|x|eq[a-z])'
                    r'(?:[\s-]?(?:klasse|class|classe|clase))?\s?-?\s?\d{3}\b'
                    r'|\bcdi\b|bluetec|blueefficiency|\bcgi\b|kompressor|hybrid|g-?tronic|amg line')
OTHER_CHASSIS = re.compile(r'\b[wrc]\s?(?:1[0-2]\d|11[0-5]|126|140|202|208|210|21[0-9]|22\d|638)\b')
W124_CODE = re.compile(r'\b[wscav]\s?124\b|\b124\s?w\b|\b124\.\d{3}\b')
W201_CODE = re.compile(r'\bw\s?201\b|\b201\.\d{3}\b')

LPG = re.compile(r'\blpg\b|autogas|gas-?anlage|\bglp\b|\bgpl\b|υγρα[έε]ριο|\bprins\b|\bbrc\b|landi\s?renzo|\bvialle\b')
DIESEL_WORD = re.compile(r'diesel|disel|πετρ[έε]λαιο|gas[oó]leo')
PETROL_WORD = re.compile(r'benzin|gasolina|βενζ[ίι]νη|petrol')

YEAR_RANGE = re.compile(r'\(?\b(?:19|20)?\d\d\s?[-–]\s?(?:19|20)?\d\d\b\)?')
YEAR_DATE = re.compile(r'\b\d{1,2}[./-](?:\d{1,2}[./-])?(19[5-9]\d)\b')
YEAR_KEYWORD = re.compile(
    r'(?:bj\.?|bouwjaar|baujahr|ez|erstzulassung|jahr|ano|año|de|uit|from|matriculad[oa] en|zugelassen)'
    r'\s*:?\s*(19[5-9]\d)\b')
YEAR_PLAIN_TITLE = re.compile(r'\b(19[5-9]\d)\b')
YEAR_APOSTROPHE = re.compile(r"[’'´`]([5-9]\d)\b")
YEAR_PLAIN_TEXT = YEAR_PLAIN_TITLE

# Diesel: cylinders per base number. Petrol: (cylinders, LPG score); None = built after 1987 only.
W124_DIESEL = {'200': 4, '250': 5, '300': 6}
W124_PETROL = {'200': (4, 1), '230': (4, 2), '260': (6, 3), '300': (6, 3),
               '220': None, '280': None, '320': None, '400': None, '420': None, '500': None, '36': None}

W124_MODEL = re.compile(
    r'\b(200|220|230|250|260|280|300|320|400|420|500)\s?'
    r'(turbo\s?diesel|turbo\s?d|diesel|td|te|ce|cd|d|e|t)?\b(\s?turbo)?(-?\s?24\s?v?\b)?')
E_NAMING = re.compile(r'\be\s?(200|220|250|280|300|320|36|400|420|500)\s?(turbo\s?diesel|diesel|td|d|t|te)?\b(\s?turbo)?')
DISPLACEMENT_DIESEL = re.compile(r'\b(2\.5|2\.0|3\.0)\s?(td|d)\b')
W201_MODEL = re.compile(r'\b190\s?(e|d)?\b')
W201_SIZE = re.compile(r'\b(1\.8|2\.0|2\.2|2\.3|2\.5|2\.6)\b')
SIXTEEN_V = re.compile(r'2\.[35]\s?-?\s?16|16\s?v\b|cosworth|\bevo\b')


def _norm(s):
    s = (s or '').lower()
    s = re.sub(r'(\d),(\d)', r'\1.\2', s)            # 2,5 -> 2.5
    s = re.sub(r'mercedes[\s-]*benz|mercedes|benz', ' ', s)
    s = re.sub(r'\b200\s?-\s?500\b', ' ', s)          # Marktplaats category "200-500 (W124)"
    s = re.sub(r'turbo-d\b', 'turbo d', s)
    return re.sub(r'\s+', ' ', s).strip()


def find_year(title, text, attrs):
    for k in ('constructionYear', 'modelDate', 'year', 'firstRegistrationYear'):
        v = str((attrs or {}).get(k) or '')
        if re.fullmatch(r'(?:19|20)\d\d', v):  # site attribute: trust it, also for modern cars
            return int(v)
    t = YEAR_RANGE.sub(' ', title)
    for rx in (YEAR_DATE, YEAR_KEYWORD, YEAR_PLAIN_TITLE):
        m = rx.search(t)
        if m:
            return int(m.group(1))
    m = YEAR_APOSTROPHE.search(t)
    if m:
        return 1900 + int(m.group(1))
    x = YEAR_RANGE.sub(' ', text)
    for rx in (YEAR_DATE, YEAR_KEYWORD, YEAR_PLAIN_TEXT):
        m = rx.search(x)
        if m:
            return int(m.group(1))
    return None


def _fuel_hint(s, attrs):
    f = ' '.join(str((attrs or {}).get(k) or '') for k in ('fuel', 'fuelType')).lower()
    if DIESEL_WORD.search(f) or f == 'd':
        return 'diesel'
    if PETROL_WORD.search(f) or 'benz' in f:
        return 'benzine'
    if DIESEL_WORD.search(s):
        return 'diesel'
    if PETROL_WORD.search(s):
        return 'benzine'
    return None


def _w201(s, full, fuel_hint):
    """Return (model, fuel, cyl, score) or (None, reason)."""
    if re.search(r'190\s?sl', s):
        return None, 'andere serie (190 SL)'
    m = W201_MODEL.search(s)
    suffix = m.group(1) if m else None
    size_m = W201_SIZE.search(s)
    size = size_m.group(1) if size_m else None
    diesel = suffix == 'd' or re.search(r'\b2\.[025]\s?d\b', s) or fuel_hint == 'diesel'
    if diesel:
        if size == '2.5' or re.search(r'2\.5\s?d|5[\s-]?(?:cil|zyl|cyl)', full):
            if 'turbo' in s:
                return None, '190D 2.5 Turbo (na 1987)'
            return ('190D 2.5', 'diesel', 5, 0), None
        return None, 'diesel 4-cilinder'
    if SIXTEEN_V.search(s):
        if re.search(r'2\.5\s?-?\s?16|\bevo\b', s):
            return None, '190E 2.5-16 (na 1987)'
        return ('190E 2.3-16', 'benzine', 4, 0), None  # 16V Cosworth head: not advised for LPG
    if size == '2.6':
        return ('190E 2.6', 'benzine', 6, 3), None
    if size == '2.3':
        return ('190E 2.3', 'benzine', 4, 2), None
    return ('190E' if suffix == 'e' else '190', 'benzine', 4, 1), None


def _w124(s, fuel_hint):
    """Return (model, fuel, cyl, score, new_naming) or (None, reason)."""
    new_naming = False
    m = W124_MODEL.search(s)
    if m:
        num, suf, turbo, v24 = m.group(1), m.group(2) or '', m.group(3), m.group(4)
    else:
        e = E_NAMING.search(s)
        d = DISPLACEMENT_DIESEL.search(s)
        if e:
            num, suf, turbo, v24, new_naming = e.group(1), e.group(2) or '', e.group(3), None, True
        elif d:
            num, suf, turbo, v24 = {'2.5': '250', '2.0': '200', '3.0': '300'}[d.group(1)], d.group(2), None, None
        else:
            return None, 'model onbekend'
    suf = suf.replace(' ', '')
    if 'turbo' in suf:
        turbo, suf = True, 'd'
    if 'turbo' in s and num in ('250', '300') and not suf.startswith(('e', 'c')) and suf != 'te':
        turbo = True
    diesel = suf in ('d', 'td', 'diesel', 'cd', 'turbodiesel') or (not suf and (fuel_hint == 'diesel' or turbo or num == '250'))
    if diesel:
        cyl = W124_DIESEL.get(num)
        if cyl is None:
            return None, f'geen W124-diesel ({num})'
        if cyl == 4:
            return None, 'diesel 4-cilinder'
        if turbo and num == '250':
            return None, '250 Turbo (na 1987)'
        label = num + ('TD' if suf == 'td' else 'D') + (' Turbo' if turbo else '')
        return (label, 'diesel', cyl, 0, new_naming), None
    spec = W124_PETROL.get(num)
    if spec is None:
        return None, f'{num}E alleen na 1987'
    if v24:
        return None, '300E-24 (na 1987)'
    label = num + {'e': 'E', 'te': 'TE', 'ce': 'CE', 't': 'T'}.get(suf, '')
    if new_naming or (not suf and re.search(r'\be\s?' + num + r'\b', s)):  # "E 300" = 300E
        label = num + 'E'
    return (label, 'benzine', spec[0], spec[1], new_naming), None


def classify(title, text='', attrs=None, price=None):
    attrs = attrs or {}
    t_raw = (title or '').lower()
    t = _norm(title)
    x = _norm(text)
    full = f'{t} {x}'
    out = {'match': False, 'reason': '', 'series': None, 'model': None, 'fuel': None, 'cyl': None,
           'year': None, 'year_known': False, 'lpg_score': 0, 'has_lpg': False}

    if price is None:
        price = attrs.get('price')
    if MODEL_CAR.search(t_raw):
        out['reason'] = 'schaalmodel'
        return out
    if WANTED.search(t_raw):
        out['reason'] = 'zoekertje'
        return out
    chassis = set(re.findall(r'\b[wrcsav]\s?(1[0-2]\d|20[1-9]|21\d)\b', t_raw))
    if PARTS.search(t_raw) or FITS_FOR.search(t_raw) or len(chassis) >= 2:
        out['reason'] = 'onderdeel'
        return out
    if MODERN.search(t) and not W124_CODE.search(t):
        out['reason'] = 'modern model'
        return out
    try:
        if price is not None and float(price) < 500:
            out['reason'] = 'prijs < 500 (onderdeel?)'
            return out
    except (TypeError, ValueError):
        pass

    year = find_year(t_raw, (text or '').lower(), attrs)
    out['year'], out['year_known'] = year, year is not None

    # Series: chassis code in title wins, then 190, then W124 model numbers
    if W201_CODE.search(t) or (W201_MODEL.search(t) and not W124_CODE.search(t)):
        series = 'W201'
    elif W124_CODE.search(t) or W124_MODEL.search(t) or E_NAMING.search(t) or DISPLACEMENT_DIESEL.search(t):
        series = 'W124'
    elif OTHER_CHASSIS.search(t):
        out['reason'] = 'andere serie'
        return out
    elif W124_CODE.search(x):
        series = 'W124'
    else:
        out['reason'] = 'geen W124/W201'
        return out
    if OTHER_CHASSIS.search(t) and not (W124_CODE.search(t) or W201_CODE.search(t)):
        out['reason'] = 'andere serie'
        return out
    out['series'] = series

    fuel_hint = _fuel_hint(full, attrs)
    if series == 'W201':
        res, reason = _w201(t if W201_MODEL.search(t) else full, full, fuel_hint)
        if res is None:
            out['reason'] = reason
            return out
        model, fuel, cyl, score = res
        new_naming = False
    else:
        res, reason = _w124(t, fuel_hint)
        if res is None and reason == 'model onbekend':
            res, reason = _w124(x, fuel_hint)
        if res is None:
            out['reason'] = reason
            return out
        model, fuel, cyl, score, new_naming = res

    out.update(model=model, fuel=fuel, cyl=cyl, lpg_score=score, has_lpg=bool(LPG.search(full)))

    if year is not None:
        if year > MAX_YEAR:
            out['reason'] = f'bouwjaar {year}'
            return out
        if year < MIN_YEAR[series]:
            out['reason'] = f'bouwjaar {year} (W123/ouder)'
            return out
    elif new_naming:
        out['reason'] = 'E-benaming zonder bouwjaar (1993+)'
        return out

    out['match'] = True
    out['reason'] = 'ok' if year else 'ok, bouwjaar onbekend'
    return out
