# Onderdelenzoeker W124 250D 1986 (57-RVV-3)

Versie 0.2, 27-10-2026. Durk koos op 27-10-2026 optie B (scraper). Gebouwd, zie "Hoe het werkt".

## De auto (RDW)

| Veld | Waarde |
|---|---|
| Kenteken | 57-RVV-3 |
| Type | Mercedes-Benz 250 D, W124 sedan, Mopf 0 (vormopf) |
| Eerste toelating | 18-09-1986 |
| Motor | OM602, 5 cilinder, 2479 cc, 66 kW (90 pk) diesel |
| Kleur | groen; lakcode en beplankingcode nog opzoeken (typeplaatje motorruimte) |

Chassisnummer (WDB124125...) en lakcode nodig voor exacte onderdeelnummers (A-nummers) en de juiste
kleur beplanking (Mopf 0 kleuren o.a. 7700 altograu, 7738 satograu, 7166).

## Doel

Kapotte of ontbrekende onderdelen vervangen, bij voorkeur tweedehands (origineel Mercedes), tegen lage
prijs, zonder elke week zelf alle sites af te lopen.

## Hoe het werkt

- `onderdelen.json`: de lijst. Per onderdeel naam, kant, A-nummer, waarom, prio, status
  (zoeken / gevonden / besteld / gemonteerd / nieuw-kopen), zoektermen per site en match-regexen.
  **Dit is het enige bestand dat je bijwerkt** als er een deel bijkomt of af is.
- `zoek.py`: zoekt op vier bronnen (`bronnen/`), matcht advertenties op de regexen (titel en tekst
  moeten ook W124 noemen; coupe/cabrio/AMG/bodykit vallen af) en schrijft `../docs/data/onderdelen.json`.
  Treffers houden `first_seen`; verdwenen advertenties worden "weg" en na 30 dagen gewist.
- `../docs/onderdelen.html`: de pagina, per onderdeel de treffers op prijs, "nieuw" bij ≤ 7 dagen.
  Online: https://jellemad.github.io/Mercedes-oldtimer-finder/onderdelen.html
- `.github/workflows/onderdelen.yml`: dagelijks 04:30 UTC, na de auto-scrape; een bron met 0 resultaten
  geeft een "Run failed"-mail.
- Lokaal draaien: `python zoek.py` in deze map (of `--only marktplaats`).

| Bron | Wat | Stand 27-10-2026 |
|---|---|---|
| kleinanzeigen.de | categorie Autoteile & Reifen, zoektermen DE per onderdeel | werkt, 35 treffers |
| marktplaats.nl | categorie Auto-onderdelen, zoektermen NL per onderdeel | werkt, 1 treffer |
| mercedesforum.nl | subforum "Aanbod onderdelen en accessoires", laatste 150 topics | werkt, nog geen W124-treffer |
| w124-board.de | Marktplatz > Biete > Teile, laatste 60 topics | werkt, nog geen treffer |
| ebay.de | — | blokkeert scrapen (403); alleen via officiële API (backlog #11) |
| w124-freunde.com, mercedes-forum.com, onderdelenlijn.nl | — | 403 of login nodig; als zoeklink (backlog #14) |

## Werkwijze per onderdeel

1. Foto in `fotos/` (map per groep, bijv. `01 - Foto ontbrekende onderdelen buitenkant auto`).
2. Ik identificeer naam (NL/DE), positie en A-nummer; jij bevestigt kant en kleur.
3. Regel in `onderdelen.json`, status "zoeken".
4. Dagelijks zoeken; treffers op de pagina. Gekocht: status "besteld", gemonteerd: "gemonteerd".

## Onderdelen uit de foto's van 27-10-2026 (buitenkant)

| Onderdeel | Kant | A-nummer (uit advertenties, controleren) | Prio |
|---|---|---|---|
| Beplanking voorspatbord onder (Beplankung Kotflügel vorn) | nog bevestigen | L A1246901340, R A1246901440 | 1 |
| Beplanking achterscherm onder (Beplankung Seitenwand hinten, Kniestück) | nog bevestigen | L A1246901740, R A1246901840 | 1 |
| Dorpelbekleding (Schwellerverkleidung) | beide | L A1246902340, R A1246902440 | 2 |
| Afdekdop krikpunt (Stopfen Wagenheberaufnahme) | ≥ 1 | A1249970486 | 2 |
| Clips/spreidnieten beplanking | — | o.a. A0009884425 | 3, nieuw kopen |

Regel: slijtdelen (remmen, lagers, rubbers, filters) nieuw; plaatwerk, interieur, spiegels, lampen,
sierdelen, elektra tweedehands.

## Toets aan de drie meetlatten

| Meetlat | Oordeel |
|---|---|
| Knelpunt (TOC) | Knelpunt is weten wát je zoekt (kant, kleur, A-nummer), niet het zoeken. Zonder chassisnummer en kant blijft de lijst onzeker. Meting: delen van "zoeken" naar "gemonteerd". |
| Essentieel | Ja: auto rijdend en heel houden. Gelaten: eBay-API, meldingen (backlog). |
| Moeiteloos | Eén bestand bijwerken, de rest loopt vanzelf. "Af" per onderdeel = gemonteerd. |
