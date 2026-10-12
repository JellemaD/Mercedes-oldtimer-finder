# CLAUDE.md - Project Memory

## Project Info
- **Naam:** Mercedes Oldtimer Finder (repo `JellemaD/Mercedes-oldtimer-finder`, was `mercedes-diesel-finder`)
- **Site:** https://jellemad.github.io/Mercedes-oldtimer-finder/ (GitHub Pages, map `docs/`)
- **Profiel:** Mercedes W124 en W201 t/m bouwjaar 31-12-1987; diesel alleen 5/6-cilinder, benzine met
  LPG-score; landen NL, BE, DE, ES, PT, GR. Besluiten en uitkomsten per fase: `PLAN.md`.
- **Dagelijks:** `.github/workflows/scrape.yml`, 04:00 UTC. Negen bronnen op GitHub, car.gr op de
  laptop-runner `C:\actions-runner-oldtimer` (label `scrape`, start bij inloggen via snelkoppeling in
  Opstarten). Een bron met 0 resultaten laat de run mislukken (mail van GitHub), data blijft staan.

## Werken aan dit project
- Test classifier na elke wijziging: `python tests/test_classify.py` (moet ≥ 90%, nu 100%).
  Nieuwe fout gevonden? Eerst als geval in `tests/classify_cases.json`, dan `classify.py` aanpassen.
- Eén bron testen: `python scrape.py --only <module>`; site lokaal: `python -m http.server 8124 --directory docs`.
- Niet te vaak volledig scrapen vanaf de laptop: coches.net en Marktplaats werden na veel testruns
  op 12-10-2026 terughoudend.
- Regexes en Windows-paden met de Edit/Write-tool schrijven, niet via Bash-heredocs (backslashes
  worden daar stuurtekens).

## Archief
De oude Flask-app (poort 5000), SQLite-database, scheduler en PythonAnywhere-bestanden staan in
`99 - Archive` (lokaal, niet in git). De oude deploy-instructies (Python-processen stoppen,
`__pycache__` wissen) gelden niet meer: er draait geen server.

Lessons learned uit de Flask-periode: [LESSONS_LEARNED.md](LESSONS_LEARNED.md).
