# Versies — Mercedes Oldtimer Finder

Nieuwste bovenaan. Per versie: wat veranderde voor de gebruiker, en de belangrijkste commits.
Bij elke inhoudelijke wijziging een nieuwe regel bovenaan; oude versies niet aanpassen.

| Versie | Datum | Wat | Commits |
|---|---|---|---|
| **2.2** | 12-10-2026 | **Alleen droge regio's zonder strooizout** (`regions.py`): natte/koude regio's in Spanje, Portugal en Griekenland vallen weg; **Zuid-Frankrijk** (Middellandse Zee-departementen) en **Zuid-Italië + eilanden** erbij via AutoScout24. **Rit naar huis** (`travel.py`): afstand naar Soest × verbruik per model × literprijs diesel/benzine/LPG, telt mee in het prijsdeel van de score en staat bij elke auto. | volgt |
| 2.1 | 12-10-2026 | Kleinanzeigen-advertentiefoto's in beide pagina-opmaken (de site wisselt willekeurig); in 2.0 kregen 11 van de 12 Kleinanzeigen-auto's nog maar 1 foto. Top 15 opnieuw beoordeeld. | 2d77f1c |
| 2.0 | 12-10-2026 | Roestcheck kijkt naar **alle foto's van de advertentie** (tot 16; bij weinig foto's in het zoekresultaat via de advertentiepagina). De AI moet de foto aanwijzen waarop de dorpels te zien zijn, anders telt het als "niet te zien". **Wielkasten** apart beoordeeld (tussen "elders" en dorpels in). AI controleert of het echt een W124/W201 is; W123 of ander model verdwijnt van de lijst. Aanleiding: 250D (#2) kreeg 40/40 terwijl de advertentie zware roest bij deur, dorpel en wielkast toont. | ed2e7d0 |
| 1.4 | 12-10-2026 | Roestcheck houdt de **top 15 op eindscore** gecheckt (checken, herberekenen, herhalen; max 30 per run). Workflow-optie "alleen roestcheck". | 95bc5da, 51c7863 |
| 1.3 | 12-10-2026 | **Roest op foto's telt 40%** van de score, dorpels extra zwaar; overige onderdelen naar rato naar 60%. Claude Opus 5.5 beoordeelt de foto's. | b3080e0, ad31d21 |
| 1.2 | 12-10-2026 | **Online en automatisch**: repo hernoemd naar Mercedes-oldtimer-finder, GitHub Pages, dagelijkse run 04:00 UTC, car.gr via laptop-runner, mail bij een bron met 0 resultaten. | a6965f1 t/m b18b157 |
| 1.1 | 12-10-2026 | **Website** (`docs/`) met top 10, filters, zoeklinks en **score 0-100** (motor, staat, km, prijs, bouwjaar, LPG). | 90b6c0e |
| 1.0 | 12-10-2026 | **Nieuw zoekprofiel en nieuwe opzet**: W124 + W201 t/m 1987, diesel 5/6-cil, benzine met LPG-score; 10 bronnen in 6 landen (NL, BE, DE, ES, PT, GR); classifier met testset; Flask/SQLite/PythonAnywhere gearchiveerd. | d74057c t/m 4bd3a9d |
| 0.x | jan 2026 | Mercedes Diesel Finder: Flask + SQLite, lokaal (poort 5000) en PythonAnywhere; W123/W124/W201 diesel 1979–1986, vooral NL/DE. | 1c8b45f t/m 7d06f3c |
