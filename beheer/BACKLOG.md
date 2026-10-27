# Backlog — Mercedes Oldtimer Finder

Eén lijst, in volgorde van belang. Bovenaan staat wat nu het meeste verschil maakt.
Af = naar "Gedaan" onderaan met datum en versie. Maximaal 3 items tegelijk "bezig".

## Nu

| # | Wat | Waarom | Af als |
|---|---|---|---|
| 1 | Roestcheck v2 narekenen op 10 auto's uit de top 15 (eigen ogen vs. AI) | Na de 250D-fout: weten of de AI nu wél roest ziet voordat we op de score vertrouwen | ≥ 9 van 10 oordelen kloppen; fouten als testgeval vastgelegd (zie #4) |
| 2 | Eerste geplande run (13-10, 04:00 UTC) controleren: beide jobs, mail bij fout | Tot nu toe alleen handmatig gestart | Run groen of fout begrepen en opgelost |

## Straks

| # | Wat | Waarom |
|---|---|---|
| 3 | `detail_images()` ook voor bronnen met weinig foto's in het zoekresultaat: Marktplaats/2dehands, car.gr, Standvirtual, CustoJusto | Nu krijgen alleen Kleinanzeigen (advertentiepagina) en de bronnen met fotolijst (AutoScout24, Wallapop, OLX, coches.net) alle foto's |
| 4 | Kleine eval-set voor de roestcheck: auto's met bekend oordeel (o.a. de 250D Kleinanzeigen 3535481069 = zware roest dorpel + wielkast) en na elke promptwijziging opnieuw draaien | Zodat een verbetering niet ongemerkt iets anders breekt (zoals `tests/test_classify.py` voor de classifier) |
| 5 | coches.net particuliere advertenties "200 diesel" zonder cc/pk: cilinders van de advertentiepagina halen | Nu afgewezen als 4-cil, kunnen 250D/300D zijn |
| 6 | Zoekertjes ("Mercedes w124 carrinha 250 ou 300", "gesucht") beter herkennen | Paar ervan glippen door de classifier |
| 7 | Marktplaats volgen: gaf op 12-10 middag vanaf de laptop alleen dealeradvertenties; vanaf GitHub wel normaal | Als het terugkomt op GitHub: scraper aanpassen |
| 8 | Subito.it (particuliere markt Italië) testen; lukt het niet: zoeklink, net als Leboncoin/La Centrale | AutoScout24.it gaf maar 9 passende auto's in het zuiden |
| 9 | Besluit: Nederland, België en Duitsland (strooizout) houden of laten vallen? | Nu gehouden; de roestcheck beoordeelt die auto's. Durk wil "geen roest" |
| 10 | Tolschattingen verfijnen met echte routes (bijv. per traject i.p.v. per land) als ze in de praktijk te ver afwijken | Nu vaste bedragen per land |
| 11 | Onderdelenzoeker: eBay.de via de officiële eBay Browse API (gratis developer-key, secret in GitHub) | Scrapen geeft 403; eBay.de heeft veel NOS- en gebruikte W124-delen |
| 12 | Onderdelenzoeker: kant (links/rechts) en lakcode/beplankingcode van 57-RVV-3 vastleggen in `onderdelen.json`, A-nummers controleren met chassisnummer | Nu "nog bevestigen"; zonder kant en kleur koop je het verkeerde deel |
| 13 | Onderdelenzoeker: mail of melding bij een nieuwe treffer voor prio-1-delen | Nu alleen de pagina; zeldzame delen zijn snel weg |
| 14 | Onderdelenzoeker: onderdelenlijn.nl-aanvraag (403 bij scrapen, handmatig invullen) en Facebook-groepen als zoeklinks op de pagina | Eén aanvraag bereikt alle NL sloperijen |

## Ooit / misschien

- Lokale map `04 - MB W124 Diesel zoeken` hernoemen naar de nieuwe naam (pad in CLAUDE.md mee aanpassen).
- Standvirtual en CustoJusto (samen ±4 auto's): schrappen zodra ze breken, niet repareren.
- Roestcheck naar Haiku 5.5 als Opus te duur wordt (eerst #4, dan vergelijken).

## Gedaan

| Datum | Versie | Wat |
|---|---|---|
| 27-10-2026 | 2.4 | Onderdelenzoeker voor de eigen 250D: 4 bronnen, dagelijkse Action, pagina onderdelen.html |
| 12-10-2026 | 2.3 | Tol en routekeuze (snelweg/binnendoor), label LPG-geschikt |
| 12-10-2026 | 2.2 | Droge regio's, Zuid-Frankrijk en Zuid-Italië, rit naar huis in de prijs |
| 12-10-2026 | 2.1 | Kleinanzeigen-foto's in beide opmaken |
| 12-10-2026 | 2.0 | Roestcheck op alle advertentiefoto's, dorpelfoto aanwijzen, wielkasten apart, W123-controle door AI |
| 12-10-2026 | 1.4 | Top 15 op eindscore altijd gecheckt |
| 12-10-2026 | 1.3 | Roest op foto's 40% van de score |
| 12-10-2026 | 1.2 | Online (GitHub Pages) en dagelijks automatisch |
| 12-10-2026 | 1.1 | Website met score |
| 12-10-2026 | 1.0 | Nieuw profiel, 10 bronnen, classifier |
