#!/usr/bin/env python3
"""
Add a part to onderdelen.json from a free-text wish, e.g. "linker achterlicht met reflector".

Used by the Action 'onderdelen.yml' when an issue titled "Onderdeel: <tekst>" is opened from
docs/onderdelen.html (the box at the bottom). No AI: search terms come from woordenboek.json
(NL -> DE). Words that are not in the dictionary give a Dutch-only search and the label
"zoektermen nakijken"; add the word to woordenboek.json and fix the part by hand.

Usage:
    python voeg_toe.py "linker achterlicht met reflector" [--issue 12] [--toelichting "..."] [--dry]
"""

import argparse
import json
import os
import re
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ONDERDELEN = os.path.join(HERE, 'onderdelen.json')
WOORDENBOEK = os.path.join(HERE, 'woordenboek.json')

LINKS = r'links|linker|linkse|linkerkant|bestuurder\w*|fahrerseite|fahrer'
RECHTS = r'rechts|rechter|rechtse|rechterkant|bijrijder\w*|beifahrer\w*'
VOOR = r'voor|voorste|voorkant|vorn|vorne|front'
ACHTER = r'achter|achterste|achterkant|hinten|heck'
STOP = {'met', 'de', 'het', 'een', 'van', 'en', 'of', 'voor', 'achter', 'mijn', 'nodig', 'ik', 'heb',
        'w124', 'mercedes', 'benz', '250d', '250', 'd', 'nieuw', 'nieuwe', 'gebruikt', 'graag', 'zoek',
        'op', 'aan', 'bij', 'in', 'onderdeel'}


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def flex(word):
    """Regex for a word that tolerates ü/ue/u, ö/oe/o, ä/ae/a, ß/ss and spaces/hyphens."""
    out = []
    for ch in word:
        out.append({'ü': '(?:ü|ue|u)', 'ö': '(?:ö|oe|o)', 'ä': '(?:ä|ae|a)', 'ß': '(?:ß|ss)',
                    ' ': r'[\s-]?', '-': r'[\s-]?'}.get(ch, re.escape(ch)))
    rx = ''.join(out)
    return r'\b' + rx if len(word) <= 5 else rx   # short words only at a word start ('bak' not in 'kofferbak')


def find_entries(text, boek):
    """Dictionary entries named in the text, longest word first, no overlaps; in text order."""
    cands = []
    for e in boek:
        for w in e['nl'] + e['de']:
            for m in re.finditer(r'\b' + re.escape(w) + r'\w*', text):
                cands.append((len(w), m.start(), m.end(), e, m.group()))
    cands.sort(key=lambda c: (-c[0], c[1]))   # longest dictionary word wins: 'spiegelglas' before 'spiegel'
    taken, found = [], []
    for _, s, t, e, woord in cands:
        if any(s < b and a < t for a, b in taken) or any(e is f[1] for f in found):
            continue
        taken.append((s, t))
        found.append((s, e, woord))
    return [(e, w) for _, e, w in sorted(found, key=lambda f: f[0])]


def only_other_side(mine, other):
    """'niet'-regex: listing names the other side and not mine."""
    return rf'(?s)^(?!.*\b(?:{mine})\b).*\b(?:{other})\b'


def slug(s):
    s = s.lower().translate(str.maketrans('üöäéèë', 'uoaeee'))
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:50] or 'onderdeel'


def maak_onderdeel(tekst, boek, bestaande_ids, issue=None, toelichting=''):
    tekst = re.sub(r'^\s*onderdeel\s*:\s*', '', tekst.strip(), flags=re.I).strip()
    low = tekst.lower()
    words = set(re.findall(r'\w+', low))

    kant_nl = kant_de = ''
    niet = []
    if re.search(rf'\b(?:{LINKS})\b', low):
        kant, kant_nl, kant_de = 'links (bestuurderskant)', 'links', 'links'
        niet.append(only_other_side(LINKS, RECHTS))
    elif re.search(rf'\b(?:{RECHTS})\b', low):
        kant, kant_nl, kant_de = 'rechts (bijrijderskant)', 'rechts', 'rechts'
        niet.append(only_other_side(RECHTS, LINKS))
    else:
        kant = 'niet opgegeven'
    entries = find_entries(low, boek)
    # 'achterdeur', 'voorbumper': position hidden in the word itself (but 'achterlicht' is just the name)
    if entries:
        hw, h0 = entries[0][1], entries[0][0]['nl'][0]
        for pre in ('voor', 'achter'):
            if hw.startswith(pre) and not h0.startswith(pre):
                words.add(pre)
    pos_nl = pos_de = ''
    if words & {'voor', 'voorste', 'voorkant'}:
        pos_nl, pos_de = 'voor', 'vorne'
        niet.append(only_other_side(VOOR, ACHTER))
    elif words & {'achter', 'achterste', 'achterkant'}:
        pos_nl, pos_de = 'achter', 'hinten'
        niet.append(only_other_side(ACHTER, VOOR))

    entries = [e for e, _ in entries]
    if entries:
        hoofd = entries[0]
        nl0, de0 = hoofd['nl'][0], hoofd['de'][0]
        detail_nl = ' '.join(x for x in (pos_nl, kant_nl) if x)
        detail_de = ' '.join(x for x in (pos_de, kant_de) if x)
        zoek = {'nl': [f'w124 {nl0} {detail_nl}'.strip(), f'w124 {nl0}'],
                'de': [f'w124 {de0} {detail_de}'.strip(), f'w124 {de0}']}
        zoek = {k: list(dict.fromkeys(v)) for k, v in zoek.items()}
        match = ['(?:' + '|'.join(flex(w) for w in dict.fromkeys(hoofd['nl'] + hoofd['de'])) + ')']
        niet += hoofd.get('niet', [])
        naam = f'{tekst[:1].upper()}{tekst[1:]} ({de0[:1].upper()}{de0[1:]})'
        nakijken = False
    else:
        inhoud = [w for w in re.findall(r'\w+', low) if w not in STOP and len(w) > 2
                  and not re.fullmatch(rf'(?:{LINKS}|{RECHTS})', w)]
        if not inhoud:
            raise ValueError(f'Geen onderdeel herkend in "{tekst}"')
        zoek = {'nl': [f'w124 {" ".join(inhoud)} {kant_nl}'.strip()], 'de': []}
        match = ['(?s)^' + ''.join(rf'(?=.*{re.escape(w)})' for w in inhoud)]
        naam = f'{tekst[:1].upper()}{tekst[1:]}'
        nakijken = True

    oid, n = slug(tekst), 2
    base = oid
    while oid in bestaande_ids:
        oid, n = f'{base}-{n}', n + 1

    waarom = f'Toegevoegd via de onderdelenpagina op {date.today().strftime("%d-%m-%Y")}'
    waarom += f' (issue #{issue}).' if issue else '.'
    # issue body from the page: "Toelichting (mag leeg):\n<tekst>\n\n---\nVia de onderdelenpagina."
    toelichting = re.split(r'^---', toelichting or '', maxsplit=1, flags=re.M)[0]
    toelichting = ' '.join(l.strip() for l in toelichting.splitlines()
                           if l.strip() and not l.lower().startswith('toelichting'))
    if toelichting:
        waarom += ' ' + toelichting[:300]
    if nakijken:
        waarom += ' Woord niet in het woordenboek: zoekt alleen op Marktplaats, zoektermen nakijken.'
    if len(entries) > 1:
        waarom += ' Ook genoemd: ' + ', '.join(e['nl'][0] for e in entries[1:]) + ' (niet apart gezocht).'

    deel = {'id': oid, 'naam': naam, 'kant': kant, 'nummer': '', 'waarom': waarom, 'prio': 2,
            'status': 'zoeken', 'zoek': zoek, 'match': match, 'niet': niet, 'foto': '',
            'toegevoegd': date.today().isoformat(), 'bron': 'pagina'}
    if nakijken:
        deel['nakijken'] = True
    if issue:
        deel['issue'] = int(issue)
    return deel


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser()
    ap.add_argument('tekst')
    ap.add_argument('--issue')
    ap.add_argument('--toelichting', default='')
    ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()

    conf = load(ONDERDELEN)
    boek = load(WOORDENBOEK)['onderdelen']
    deel = maak_onderdeel(a.tekst, boek, {p['id'] for p in conf['onderdelen']}, a.issue, a.toelichting)
    print(json.dumps(deel, ensure_ascii=False, indent=1))
    if a.dry:
        return 0
    conf['onderdelen'].append(deel)
    tmp = ONDERDELEN + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(conf, f, ensure_ascii=False, indent=2)
        f.write('\n')
    os.replace(tmp, ONDERDELEN)
    # one line for the issue comment (read by the workflow)
    out = os.environ.get('GITHUB_OUTPUT')
    if out:
        with open(out, 'a', encoding='utf-8') as f:
            f.write(f"id={deel['id']}\nnaam={deel['naam']}\nnakijken={'1' if deel.get('nakijken') else ''}\n"
                    f"de={' | '.join(deel['zoek']['de'])}\nnl={' | '.join(deel['zoek']['nl'])}\n")
    return 0


if __name__ == '__main__':
    sys.exit(main())
