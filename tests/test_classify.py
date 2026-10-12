"""
Accuracy check for classify.py against labelled real listings (tests/classify_cases.json).

Run: python tests/test_classify.py    -> prints failures and the score; exits 1 below 90%.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from classify import classify  # noqa: E402

TARGET = 0.90
FIELDS = ('model', 'fuel', 'cyl', 'lpg_score', 'has_lpg')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    path = os.path.join(os.path.dirname(__file__), 'classify_cases.json')
    with open(path, encoding='utf-8') as f:
        cases = json.load(f)
    ok = 0
    for c in cases:
        got = classify(c['title'], c['text'], c['attrs'])
        exp = c['expect']
        wrong = [] if got['match'] == exp['match'] else ['match']
        if exp['match'] and got['match']:
            wrong += [k for k in FIELDS if k in exp and got[k] != exp[k]]
        if wrong:
            print(f"FOUT {c['id']:8} {c['title'][:60]!r}")
            print(f"     verwacht {exp}")
            print(f"     kreeg    { {k: got[k] for k in ('match', 'reason', 'model', 'fuel', 'cyl', 'year', 'lpg_score', 'has_lpg')} }")
        else:
            ok += 1
    score = ok / len(cases)
    print(f'\n{ok}/{len(cases)} goed = {score:.0%} (doel {TARGET:.0%})')
    sys.exit(0 if score >= TARGET else 1)


if __name__ == '__main__':
    main()
