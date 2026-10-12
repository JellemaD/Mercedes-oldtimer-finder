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
| 10 | Rit naar huis: tol (FR/IT/ES) en veerboot (Sardinië, Sicilië, Griekenland) toevoegen | Nu alleen brandstof |

## Ooit / misschien

- Lokale map `04 - MB W124 Diesel zoeken` hernoemen naar de nieuwe naam (pad in CLAUDE.md mee aanpassen).
- Standvirtual en CustoJusto (samen ±4 auto's): schrappen zodra ze breken, niet repareren.
- Roestcheck naar Haiku 5.5 als Opus te duur wordt (eerst #4, dan vergelijken).

## Gedaan

| Datum | Versie | Wat |
|---|---|---|
| 12-10-2026 | 2.2 | Droge regio's, Zuid-Frankrijk en Zuid-Italië, rit naar huis in de prijs |
| 12-10-2026 | 2.1 | Kleinanzeigen-foto's in beide opmaken |
| 12-10-2026 | 2.0 | Roestcheck op alle advertentiefoto's, dorpelfoto aanwijzen, wielkasten apart, W123-controle door AI |
| 12-10-2026 | 1.4 | Top 15 op eindscore altijd gecheckt |
| 12-10-2026 | 1.3 | Roest op foto's 40% van de score |
| 12-10-2026 | 1.2 | Online (GitHub Pages) en dagelijks automatisch |
| 12-10-2026 | 1.1 | Website met score |
| 12-10-2026 | 1.0 | Nieuw profiel, 10 bronnen, classifier |
