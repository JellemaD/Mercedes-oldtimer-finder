# Mercedes Oldtimer Finder

Dagelijks overzicht van te koop staande Mercedes **W124 en W201 (190) t/m bouwjaar 1987**:
diesels met 5 of 6 cilinders (250D, 300D, 300D Turbo, 190D 2.5) en benzinemotoren die goed op LPG
kunnen (300E, 260E, 190E 2.6, 230E, 200), uit NL, BE, DE, ES, PT en GR.

**Site:** https://jellemad.github.io/Mercedes-oldtimer-finder/

## Hoe het werkt

| Onderdeel | Bestand |
|---|---|
| Bronnen (één module per site) | `sources/` — contract in `sources/common.py` |
| Past de advertentie in het profiel? | `classify.py` — test: `python tests/test_classify.py` |
| Score 0-100 | `score.py` |
| Scrapen, samenvoegen, status | `scrape.py` → `docs/data/listings.json`, `docs/data/status.json` |
| Website | `docs/index.html` (GitHub Pages, map `/docs`) |
| Dagelijks draaien | `.github/workflows/scrape.yml` — 06:00 (winter 05:00) |

Negen bronnen draaien op GitHub; car.gr alleen op de laptop-runner (`C:\actions-runner-oldtimer`,
label `scrape`, start bij inloggen) omdat Cloudflare de IP's van GitHub blokkeert. Geeft een bron 0
resultaten, dan blijven zijn advertenties staan en mislukt de run, zodat GitHub een mail stuurt.

```bash
pip install -r requirements.txt
python scrape.py                 # alle bronnen
python scrape.py --only wallapop # één bron
python -m http.server 8124 --directory docs
```

Besluiten en uitkomsten per fase: [PLAN.md](PLAN.md). Versies: [beheer/VERSIES.md](beheer/VERSIES.md). Wat nog open staat: [beheer/BACKLOG.md](beheer/BACKLOG.md).
