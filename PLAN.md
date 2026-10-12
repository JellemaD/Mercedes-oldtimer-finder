# PLAN — Mercedes W124/W201 Finder als website

Vastgesteld met Durk op 12-10-2026.

## Doel

Elke ochtend een overzicht van te koop staande Mercedes W124 en W201 (bouwjaar t/m 1987) uit
NL, DE, BE, ES, PT en GR, als website op GitHub Pages. Geen server, geen PythonAnywhere.

## Zoekprofiel

| Groep | Modellen | Jaren | Cilinders |
|---|---|---|---|
| W124 diesel | 250D/TD, 300D/TD, 300TD Turbo | 1984–1987 | 5 / 6 |
| W201 diesel | 190D 2.5 | 1985–1987 | 5 |
| W124 benzine (LPG) | 300E/TE/CE, 260E, 230E/TE/CE, 200 | 1984–1987 | 6 / 4 |
| W201 benzine (LPG) | 190E 2.6, 190E 2.3, 190E 2.0, 190 | 1984–1987 | 6 / 4 |

Vervalt: W123, W210, W124 200D, 190D 2.0, 190E 2.3-16 (verzamelobject).

### LPG-score (benzine)

| Score | Modellen | Motor | Toelichting |
|---|---|---|---|
| ★★★ | 300E/TE/CE, 260E, 190E 2.6 | M103 6-cil | Ruim vermogen, LPG-verlies (5–10%) nauwelijks merkbaar; robuust, hydraulische klepstoters |
| ★★ | 230E/TE/CE, 190E 2.3 | M102 4-cil | Klassieke taxi op LPG; eenvoudig en duurzaam, verlies wel merkbaar |
| ★ | 200, 190, 190E 2.0 | M102 4-cil | Makkelijk om te bouwen, maar traag |

Badge **"rijdt al op LPG"**: herkend aan LPG, autogas, Gasanlage, GLP, GPL, υγραέριο of
installatiemerken (Prins, BRC, Landi Renzo, Vialle). Bij aankoop: keuring en tankdatum checken;
KE-Jetronic met venturi-installatie vraagt een terugslagklep.

## Architectuur

```
GitHub Actions (cron 06:00 NL)
  job A: GitHub-runner   → sites die datacenter-IP's toelaten
  job B: laptop-runner   → Marktplaats, Kleinanzeigen e.d. (label: scrape)
        ↓
  docs/data/listings.json (first_seen / last_seen)  → commit
GitHub Pages (/docs): index.html + app.js, filters in de browser
```

Draaikosten €0 (publieke repo). Geen AI in de dagelijkse run.

## Fasen

| Fase | Wat | Af als |
|---|---|---|
| 0 Opruimen | Oude bestanden naar `99 - Archive`, plan vastleggen | Schone `git status` ✅ |
| 1 Sites testen | Per site testen vanaf GitHub-runner en laptop. ES: autoscout24.es, coches.net, milanuncios, wallapop. PT: standvirtual, olx.pt, custojusto. GR: car.gr, xe.gr. Plus bestaande NL/DE/BE-bronnen. Max 2 pogingen per site. | Tabel: werkt GitHub / werkt laptop / wordt zoeklink |
| 2 Classifier | Eén `classify()` voor model, motor, brandstof, cilinders, jaar, LPG-score, "al LPG" | ≥90% goed op ±50 echte titels in 5 talen |
| 3 Scrapers | `scrape.py` → `docs/data/listings.json`; Flask, APScheduler, SQLite eruit; prijs/km-parser met grenzen (fix "int too large") | Lokale run levert geldige JSON |
| 4 Site | Filters: land, groep, brandstof, cilinders, LPG-score, al LPG, jaar, prijs, nieuw. Werkt op telefoon | Lokaal te openen en filteren |
| 5 Automatiseren | Workflow (cron + handmatig), jobs A/B, melding bij 0 resultaten per bron, Pages aan | Eerste automatische run online |
| 6 Afronden | CLAUDE.md-tabel, `Mijn websites.html`, README `mijn-websites` | Link werkt vanaf startpagina |

## Uitkomst fase 1 (12-10-2026)

Getest met `tools/site_test.py` (laptop) en workflow `site-test` (GitHub-runner).

| Land | Site | Laptop | GitHub | Techniek | Besluit |
|---|---|---|---|---|---|
| NL | Marktplaats | ✅ | ✅ | JSON-API `/lrp/api/search` | scrapen |
| NL | AutoTrack | ✅ | ✅ | `__NEXT_DATA__` | scrapen |
| NL | Gaspedaal | ✅ | ✅ (met curl_cffi) | curl_cffi | scrapen (aggregator, overlap) |
| NL/BE/DE/ES | AutoScout24 | ✅ | ✅ | `__NEXT_DATA__` | scrapen (één scraper, 4 landen) |
| BE | 2dehands | ✅ | ✅ | JSON-API (zelfde platform als Marktplaats) | scrapen |
| DE | Kleinanzeigen | ✅ | ✅ | HTML + ld+json | scrapen |
| DE | eBay.de | ❌ | ❌ | 3 technieken 403 | zoeklink |
| DE | mobile.de | ❌ | ❌ | Akamai | zoeklink |
| ES | coches.net | ✅ | ✅ | HTML + ld+json | scrapen |
| ES | Wallapop | ✅ | ✅ | JSON-API met app-headers | scrapen |
| ES | Milanuncios | ❌ | ❌ | captcha | zoeklink |
| PT | Standvirtual | ✅ | ✅ | `__NEXT_DATA__` | scrapen |
| PT | CustoJusto | ✅ | ✅ | `__NEXT_DATA__` | scrapen |
| PT | OLX.pt | ✅ | ✅ | curl_cffi | scrapen |
| GR | car.gr | ✅ | ❌ Cloudflare | navigatie-headers | scrapen via **laptop-runner** |
| GR | xe.gr | – | – | geen auto-rubriek meer | vervalt |

Geblokkeerde sites worden vaste zoeklinks op de site. Haiku-classificatie (±$0,50/maand)
alleen als fase 2 onder 90% blijft.
