# Mercedes-Benz W124 Diesel — 250D (OM602) & 300D (OM603), bouwjaar 1985–1987

**Compleet trainingshandboek: van beginner tot zelfverzekerde koper & opknapper.**
Geschatte studietijd: 2 uur. Oorspronkelijk samengesteld februari 2026 (Claude-chat
"W124 dieselmotor basisbeginselen leren", geleverd als `W124_Diesel_Training_Handboek.docx`).
Op 01-11-2026 uit die chat overgenomen naar dit project, zodat de cursus bij de auto (57-RVV-3) staat.

> **Correcties 01-11-2026** (gecontroleerd tegen de fabrieks-datenblätter, ADAC en Wikipedia DE; zie het
> gesprek van 01-11-2026 over verbruik en overbrengingen). De oorspronkelijke tekst hieronder is
> ongewijzigd gelaten, dus lees deze punten erbij:
> - **250D had de 5-bak standaard** (niet de 4-bak). 4-bak standaard gold voor de 200D en 200.
> - **Eindoverbrengingen (tabel 5.4) kloppen niet.** Juist: 250D handbak 3,42 of 3,64; **250D automaat 3,07**
>   (ca. 3.150 toeren bij 120 km/h); 300D handbak 3,46; 300D automaat 2,88.
> - Automaat 722.4 (W4A 020) zit op 4- en 5-cilinders, 722.3 (W4A 040) op 6-cilinders: klopt.
>   Alle automaten 4 trappen, 4e = 1:1.
> - **Brandstoffilter**: de OM601/602/603 ontlucht zichzelf bij starten; geen handpomp nodig.
>   Volledige procedure, nummers (A6010901652, voorfilter A0024772701) en koppel (25 Nm): zie gesprek 01-11-2026.
> - **Brandstof**: gewone EN 590 diesel; HVO100 kan (retourslangen controleren); geen B100.
> - Verbruik fabriek 250D automaat: 5,9 / 7,7 / 8,8 l/100 km (90 / 120 / stad), mix 7,5.

---

## Inhoud

1. Kennismaking met de W124 (20 min)
2. De dieselmotor – hoe werkt het? (30 min)
3. Brandstofsysteem & inspuiting (15 min)
4. Koelsysteem & smeersysteem (15 min)
5. Aandrijflijn – van motor naar wiel (15 min)
6. Uitlaat, afwatering & overige systemen (10 min)
7. Kopen & beoordelen – praktijkgids (20 min)
8. Onderhoud & veelvoorkomende problemen (15 min)
9. Aanbevolen YouTube-video's en bronnen
10. Samenvatting & businessmodel opknappers

---

## Module 1: Kennismaking met de W124 (20 min)

### 1.1 Wat is de W124?

De Mercedes-Benz W124 is de interne chassiscode voor de middenklasse Mercedes die werd geproduceerd van 1984 tot 1997. Het is de directe opvolger van de legendarische W123 en wordt door veel kenners beschouwd als de best gebouwde Mercedes ooit. De "W" staat voor "Wagen" (Duits voor auto) en "124" is het interne projectnummer.

De W124 werd gepresenteerd op de Autosalon van Sevilla op 5 november 1984. De serieproductie begon in januari 1985 met zeven modellen. Er zijn meer dan 2,5 miljoen exemplaren geproduceerd over de gehele productieperiode.

**Carrosserievarianten:**

| Code | Type | Productie |
|---|---|---|
| W124 | Sedan (Limousine) | 1984–1995 |
| S124 | Estate (T-model) | 1985–1996 |
| C124 | Coupé | 1987–1996 |
| A124 | Cabriolet | 1991–1997 |
| V124 | Limousine (lang) | 1990–1995 |

### 1.2 De dieselmodellen 1985–1987

Voor jouw focus op pre-1986 (en tot 1987) zijn er twee relevante dieselmodellen:

| Eigenschap | 250D | 300D |
|---|---|---|
| Motor | OM602.911 | OM603.912 |
| Configuratie | 5-cilinder lijnmotor | 6-cilinder lijnmotor |
| Cilinderinhoud | 2.497 cc | 2.996 cc |
| Vermogen | 90 pk (66 kW) bij 4600 tpm | 109 pk (80 kW) bij 4600 tpm |
| Koppel | 155 Nm bij 2800 tpm | 185–191 Nm bij 2800–3050 tpm |
| Compressieverhouding | 22,0 : 1 | 22,0 : 1 |
| Cilinderboring | 87 mm | 87 mm |
| Zuigerslag | 84 mm | 84 mm |
| Gewicht auto | ca. 1.370 kg | ca. 1.440 kg |
| Topsnelheid | ca. 175 km/h | ca. 190 km/h |
| 0–100 km/h | ca. 15 sec | ca. 13,7 sec |
| Aandrijving | Achterwielaandrijving (RWD) | Achterwielaandrijving (RWD) |

Let op: de 250D (OM602) is de populairdere motor voor doorverkoop vanwege de legendarische betrouwbaarheid. Sommige OM602-motoren hebben meer dan 1.000.000 km gelopen. De OM603 (300D) is zeldzamer en gevoeliger voor cilinderkopproblemen, maar biedt meer vermogen en souplesse door de 6e cilinder.

---

## Module 2: De dieselmotor – hoe werkt het? (30 min)

### 2.1 Basisprincipe van een dieselmotor

Een dieselmotor werkt fundamenteel anders dan een benzinemotor. Het grote verschil zit in de ontsteking:

- **Benzinemotor:** een bougie maakt een vonk die het brandstof-luchtmengsel ontsteekt.
- **Dieselmotor:** lucht wordt zó sterk samengeperst (compressieverhouding 22:1) dat de temperatuur stijgt tot ca. 700–900 °C. Dieselbrandstof wordt dan in deze hete lucht gespoten en ontsteekt spontaan.

**De vier takten van de W124 diesel:**

1. **Inlaattakt:** de zuiger gaat naar beneden, het inlaatventiel opent, schone lucht (géén brandstof!) wordt aangezogen.
2. **Compressietakt:** beide ventielen dicht. De zuiger perst de lucht samen tot 1/22e van het oorspronkelijke volume. De temperatuur stijgt enorm.
3. **Arbeidstakt (verbranding):** de Bosch injectiepomp spuit via de verstuiver (injector) fijne dieselnevel in de voorkamer (prechamber). De brandstof ontsteekt direct door de hitte. De explosie duwt de zuiger naar beneden → dit levert vermogen.
4. **Uitlaattakt:** het uitlaatventiel opent, de zuiger duwt de verbrandingsgassen naar buiten via het uitlaatspruitstuk.

### 2.2 Het voorkamersysteem (indirecte injectie)

Cruciaal om te begrijpen: de OM602 en OM603 zijn INDIRECTE injectie-motoren. Dit betekent dat de diesel niet direct in de cilinder wordt gespoten, maar eerst in een kleine voorkamer (prechamber) die in de cilinderkop zit.

- De voorkamer creëert een wervelende verbranding die zachter en stiller is dan directe injectie.
- Nadeel: iets minder efficiënt dan directe injectie (meer brandstofverbruik).
- Voordeel: veel soepeler motorloop, minder trillingen, langere levensduur.

### 2.3 Motorblok & cilinderkop

**Motorblok (onderblok):**

- Materiaal: gietijzer – extreem sterk en duurzaam.
- Bevat de cilinders waarin de zuigers op en neer bewegen.
- OM602: 5 cilinders op een rij (lijn-5) – uniek geluid, lichte trilling.
- OM603: 6 cilinders op een rij (lijn-6) – inherent gebalanceerd, fluisterstil.

**Cilinderkop (bovenkant motor):**

- Materiaal: aluminium – lichter, betere warmteafvoer, maar kwetsbaarder bij oververhitting.
- Bevat de ventielen (2 per cilinder: 1 inlaat, 1 uitlaat), de voorkamers en de nokkenas.
- SOHC-ontwerp: Single Overhead Camshaft – één bovenliggende nokkenas.
- Hydraulische klepstellers: automatische klepspeling, géén handmatige afstelling nodig.

> **WAARSCHUWING OM603:** de vroege cilinderkoppen (mal #14) van de OM603 zijn berucht om scheuren bij oververhitting. Dit is het grootste risico bij de 300D 1985–1987. Controleer altijd of de kop al vervangen is door een latere mal (#17 of #22). Dit is een dealbreaker bij aankoop!

### 2.4 Kleppentrein & distributieketting

De nokkenas en de injectiepomp worden aangedreven door een duplex distributieketting (dubbele rollenketting) vanaf de krukas. Dit is geen distributieriem! Een ketting gaat veel langer mee, maar moet wel onderhouden worden.

- Ketting levensduur: ca. 200.000–250.000 km (bij goed onderhoud).
- Een aparte enkelrijige ketting drijft de oliepomp aan.
- Als de ketting breekt, kan dit de cilinderkop ernstig beschadigen.
- Luister bij aankoop naar rammelgeluiden bij koude start – teken van versleten ketting of geleiders.

---

## Module 3: Brandstofsysteem & inspuiting (15 min)

### 3.1 Het brandstofsysteem stap voor stap

Het pad van diesel van tank tot verbranding:

1. **Brandstoftank** → zit onder de auto, achter.
2. **Voorfilter / waterafscheider** → vangt water en grof vuil op. Water in diesel is de vijand!
3. **Opvoerpomp (liftpomp)** → zit op de zijkant van de injectiepomp, pompt diesel uit de tank naar de injectiepomp.
4. **Brandstoffilter** → fijn filterelement dat vuil tegenhoudt. Vervangen elke 15.000–20.000 km.
5. **Bosch PES lijn-injectiepomp** → het hart van het systeem. Mechanisch aangestuurd, creëert de hoge druk (ca. 120–170 bar) die nodig is om diesel in de voorkamers te spuiten.
6. **Injectieleidingen (stalen buisjes)** → transporteren hogedruk-diesel naar elke injector.
7. **Verstuivers (injectors)** → spuiten een fijne nevel van diesel in de voorkamer van elke cilinder.

**Ontstekingsvolgorde:**

- OM602 (5-cilinder): 1 – 2 – 4 – 5 – 3
- OM603 (6-cilinder): 1 – 5 – 3 – 6 – 2 – 4

### 3.2 Gloeibougies (voorgloeisysteem)

Omdat een dieselmotor geen bougie heeft, zijn er gloeibougies nodig voor de koude start. Deze zitten in de voorkamers en gloeien roodheet om de eerste verbranding mogelijk te maken.

Draai het contactsleuteltje naar positie 2: het gloeibougie-lampje (spiraal-symbool) gaat branden. Wacht tot het lampje uitgaat (ca. 5–15 seconden afhankelijk van temperatuur), dan starten. Bij temperaturen boven 20 °C is voorgloeien nauwelijks nodig.

Bij aankoop: als de motor moeilijk koud start, controleer de gloeibougies en het gloeibougie-relais.

---

## Module 4: Koelsysteem & smeersysteem (15 min)

### 4.1 Het koelsysteem

Het koelsysteem is CRUCIAAL bij de W124 diesel, vooral bij de OM603 die gevoelig is voor oververhitting.

| Component | Functie |
|---|---|
| Radiateur (koeler) | Groot koperen/aluminium element aan de voorkant. Koelt de koelvloeistof via luchtstroom. |
| Waterpomp | Aangedreven door de multiriem, pompt koelvloeistof rond. |
| Thermostaat | Regelt de temperatuur: houdt koelvloeistof in motorblok tot ca. 80 °C, opent dan circuit naar radiateur. |
| Viscokoppeling (fan clutch) | Mechanische ventilator op de waterpomp. Draait harder als de motor warmer wordt. |
| Expansievat | Transparant reservoir voor koelvloeistofniveau-controle. Zit rechts in motorruimte. |
| Koelslangen | Rubber verbindingen tussen motor, radiateur en verwarming. Verouderen en worden bros. |
| Temperatuursensor | Stuurt het dashboard-instrument aan. |

**Koelvloeistof specificaties:** gebruik altijd Mercedes-goedgekeurde koelvloeistof (blauw, op basis van monoethyleenglycol). Meng 50/50 met gedemineraliseerd water. Goedkope of oude antivries kan leiden tot een doorgeblazen koppakking!

Normale bedrijfstemperatuur: 80 °C – 100 °C. Als de temperatuur boven de 100 °C komt, DIRECT stoppen en oorzaak zoeken. Mogelijk defecte thermostaat, viscokoppeling, of lekkende slang.

Vervangingsinterval: koelvloeistof elke 2 jaar verversen. Slangen en thermostaat elke 4–5 jaar controleren.

### 4.2 Het smeersysteem (motorolie)

De oliepomp wordt aangedreven door een aparte enkelrijige ketting vanaf de krukas. Olie wordt onder druk door het motorblok, de krukas, de nokkenas en de hydraulische klepstellers gepompt.

**Aanbevolen motorolie:** 15W-40 minerale dieselolie (bijv. Shell Rotella T4 of Liqui Moly Diesel High Tech). Voor het Nederlandse klimaat is 10W-40 ook geschikt voor betere koude start.

Olie-interval: elke 5.000–7.500 km of jaarlijks, wat het eerst komt. Bij de OM602/603 is regelmatige olieverversing het allerbelangrijkste onderhoud.

Oliedruk: controleer bij aankoop of het olielampje direct uitgaat na starten. Knipperen of branden bij stationair = NIET KOPEN.

---

## Module 5: Aandrijflijn – van motor naar wiel (15 min)

### 5.1 Overzicht aandrijflijn

De W124 diesel is altijd achterwielaandrijving (RWD). Het vermogen loopt van de motor naar achteren als volgt:

**Motor → Koppeling/Automaat → Cardanas → Differentieel → Aandrijfassen → Achterwielen**

### 5.2 De versnellingsbak

| Type | Details |
|---|---|
| 4-bak handgeschakeld | Standaard op de 250D. Stevige Mercedes-bak. *(Correctie: 250D had de 5-bak standaard, zie boven.)* |
| 5-bak handgeschakeld | Optioneel op 250D, standaard op 300D. Extra overdrive-versnelling voor snelweg. |
| 4-traps automaat (722.4) | W4A 020 automaat. Betrouwbaar maar geen overdrive. Op de 250D. |
| 4-traps automaat (722.3) | W4A 040, sterkere versie. Op de 300D. |

Bij aankoop: controleer of de automaat vloeiend schakelt zonder schoppen of slippen. Schakelproblemen = dure reparatie. De automatische versnellingsbak gebruikt ATF (Automatic Transmission Fluid) – rode olie. Check kleur en niveau.

### 5.3 De cardanas (propeller shaft)

De cardanas verbindt de versnellingsbak met het differentieel achterin. Let op deze onderdelen:

- **Flexschijf (Hardyscheibe / flex disc):** rubber verbinding tussen cardanas en differentieel. Veroudert en scheurt. Controleer op scheuren en speling!
- **Center bearing (tussenlager):** ondersteunt de tweedelige cardanas. Bij trillingen op snelheid vaak de boosdoener.

### 5.4 Het differentieel (achteras)

Het differentieel verdeelt het vermogen over de twee achterwielen en zorgt ervoor dat het buitenste wiel sneller kan draaien in bochten.

| Model | Overbrengingsverhouding (origineel) | Gecontroleerd 01-11-2026 | Type |
|---|---|---|---|
| 250D handgeschakeld | 3,64 : 1 | 3,42 of 3,64 | 185 mm open differentieel |
| 250D automaat | 3,46 : 1 | **3,07** | 185 mm open differentieel |
| 300D handgeschakeld | 3,46 : 1 | 3,46 | 185 mm open differentieel |
| 300D automaat | 3,07 : 1 | 2,88 | 185 mm open differentieel |

Differentieelolie: hypoid versnellingsbakolie (SAE 90). Vervangen elke 60.000 km of bij aankoop als historie onbekend.

---

## Module 6: Uitlaat, afwatering & overige systemen (10 min)

### 6.1 Het uitlaatsysteem

- **Uitlaatspruitstuk (manifold):** gietijzeren verzamelstuk dat aan de cilinderkop zit. Alle uitlaatgassen komen hier samen.
- **Flexibel stuk (flexpipe):** absorbeert trillingen van de motor. Scheurt vaak door ouderdom.
- **Middendemper:** eerste geluidsdemping.
- **Einddemper:** tweede geluidsdemping, zit helemaal achterin.
- **Katalysator:** vanaf september 1986 standaard op de W124.

Controleer bij aankoop: roestaantasting, lekkende verbindingen (luister naar blazend geluid), hangende uitlaat door versleten rubbers.

### 6.2 Afwatering (drainage) van de carrosserie

De W124 heeft diverse drainagepunten die verstopt kunnen raken. Verstopte afvoeren leiden tot waterlekkage in het interieur en roest:

- **Zonnedak-afvoeren:** vier afvoerslangen (als zonnedak aanwezig). Verstopt = water in hemelbekleding en voetruimte.
- **Deurafvoeren:** onderkant van elke deur heeft drainagegaten. Prik ze open met een dunne draad.
- **Kofferbak-afvoer:** controleer op vocht in de reservewielkuip.
- **Scuttle panel (cowl):** het paneel onder de voorruit. Bladeren en vuil verstoppen de afvoer naar de stuurbekrachtigingsruimte.
- **Wielkasten:** controleer op ophopend vuil dat vocht vasthoudt en roest veroorzaakt.

### 6.3 Vacuümsysteem

De W124 diesel gebruikt een uitgebreid vacuümsysteem voor diverse functies: centrale vergrendeling, motorstop (afsluitklep op injectiepomp), klimaatregeling, en cruisecontrol. De vacuümpomp zit op de motor en wordt mechanisch aangedreven.

Bekend probleem: de vacuümpomp kan intern kapotgaan en olie lekken. Check bij aankoop of de centrale vergrendeling en deuren goed functioneren – dit zijn vaak de eerste tekenen van vacuümproblemen.

---

## Module 7: Kopen & beoordelen – praktijkgids (20 min)

### 7.1 Aankoopchecklist pre-1986 W124 diesel

Gebruik deze checklist bij elke bezichtiging in Duitsland of Spanje:

**A. Motor & mechanisch**

- [ ] Koude start: start de motor soepel? Hoeveel voorgloei-tijd? Blauwe rook bij koude start is normaal, zwarte rook = injectieprobleem.
- [ ] Stationair: draait de motor egaal? Geen tikken, kloppen of overdreven trillingen?
- [ ] Olielampje: gaat direct uit na starten?
- [ ] Temperatuurmeter: blijft tussen 80 °C en 100 °C tijdens proefrit?
- [ ] Distributieketting: luister naar rammelgeluiden bij koude start.
- [ ] OM603: vraag naar cilinderkop-historie (mal #14 = risico, #17/#22 = goed).
- [ ] Oliepeilstok: controleer niveau en kleur. Melkachtig = water in olie (koppakkinglek!).
- [ ] Koelvloeistof: check niveau en kleur. Olieachtig residu = koppakkinglek.

**B. Aandrijflijn**

- [ ] Versnellingsbak: schakelt soepel in alle versnellingen? Geen knarsen of hakken?
- [ ] Automaat: schakelt vloeiend op en af? Geen slippen of harde schokken?
- [ ] Trillingen op snelheid: center bearing of flexschijf versleten?

**C. Carrosserie & roest**

- [ ] Wielkasten (alle vier): bubbelroest of doorroesting?
- [ ] Krikpunten (jack points): roest of doorgerot?
- [ ] Dorpels: druk met je duim – voelt het stevig?
- [ ] Veerpoten voor: roest aan de onderkant?
- [ ] Onderrand deuren: open alle deuren, kijk naar onderkant.
- [ ] Kofferbak reservewielkuip: droog? Geen roest?

**D. Interieur & elektriciteit**

- [ ] Alle ramen op en neer (elektrisch)?
- [ ] Centrale vergrendeling functioneert (vacuümsysteem)?
- [ ] Dashboard: alle lampjes werken, geen waarschuwingslampjes aan?
- [ ] Bekleding: MB-Tex (vinyl met smalle verticale plooien) vs. leer (vlakke panelen)?

### 7.2 Prijsindicatie & marktverschillen

**Duitsland:** groot aanbod, strenge TÜV-keuring zorgt voor betere basiskwaliteit. Let op "TÜV bis" datum – dit is de APK-vervaldatum. Geen TÜV = extra kosten.

**Spanje:** vaak roestvrij door droog klimaat, MAAR: verwaarlozing van mechaniek is gebruikelijk. Interieur kan verbleekt zijn door zon. Check altijd de motor extra goed.

Let op bij import naar Nederland: BPM, invoerrechten, RDW-keuring. Een pre-1986 auto kan als oldtimer (25+ jaar oud) voordelen bieden qua wegenbelasting.

---

## Module 8: Onderhoud & veelvoorkomende problemen (15 min)

### 8.1 Onderhoudsschema

| Interval | Werkzaamheid |
|---|---|
| Elke 5.000–7.500 km | Motorolie + filter vervangen |
| Elke 15.000–20.000 km | Brandstoffilter vervangen |
| Elke 15.000 km | Luchtfilter inspecteren (vervangen indien nodig) |
| Elke 2 jaar | Koelvloeistof verversen |
| Elke 30.000 km | Remvloeistof vervangen |
| Elke 60.000 km | Versnellingsbakolie / differentieelolie controleren/vervangen |
| Elke 60.000 km | Multiriem (V-belt) controleren/vervangen |
| Elke 100.000 km | Distributieketting en geleiders inspecteren |
| Elke 200.000–250.000 km | Distributieketting vernieuwen |
| Jaarlijks | Alle drainagepunten controleren en schoonmaken |
| Jaarlijks | Flexschijf en motorsteunen controleren |

### 8.2 Top 10 veelvoorkomende problemen

| Probleem | Motor/model | Kostenindicatie |
|---|---|---|
| Gescheurde cilinderkop | OM603 (mal #14) | € 800–€ 1.500 |
| Versleten distributieketting/geleiders | Beide | € 500–€ 1.000 |
| Defecte vacuümpomp | Beide | € 200–€ 400 |
| Viscokoppeling defect (oververhitting) | Beide | € 100–€ 250 |
| Koppakkinglekkage | Beide | € 400–€ 800 |
| Versleten motorsteunen (trillingen) | OM602 vooral | € 150–€ 300 |
| Lekkende injectieleidingen | Beide | € 100–€ 200 |
| Roest in wielkasten/krikpunten | Carrosserie | € 300–€ 2.000+ |
| Hydraulische klepstellers (tikgeluid) | Beide | € 200–€ 500 |
| Versleten flexschijf cardanas | Aandrijflijn | € 50–€ 150 |

---

## Module 9: Aanbevolen YouTube-video's en bronnen

### 9.1 Video's (links uit het vervolgbericht in de chat)

1. **Diesel motor uitleg (animatie)**
   - https://www.youtube.com/watch?v=Lrr-vGfOGHQ — "How Diesel Engines Work - Part 1 (Four Stroke Combustion Cycle)"
   - Zoek: `How diesel engine works animation`
2. **MercedesSource / Kent Bergsma** — dé specialist voor OM601/602/603, 400+ video's
   - https://www.youtube.com/@MercedesSource
   - Zoek: `MercedesSource diesel 601 602 603`
3. **W124 koopgidsen**
   - Zoek: `Mercedes W124 buying guide what to look for` (Hervé Collette)
   - Zoek: `Mercedes W124 buyers guide inspection`
   - Zoek: `Classics World Mercedes W124 buying guide`
4. **AUTODOC reparatie-tutorials** — stap voor stap W124-onderhoud
   - https://www.youtube.com/@AUTODOC
   - Zoek: `AUTODOC Mercedes W124`
5. **Koude start / motorgeluid als referentie**
   - Zoek: `Mercedes W124 250D cold start OM602`, `Mercedes W124 300D cold start OM603`, `Mercedes OM602 engine sound`
6. **Specifieke klussen**
   - `Mercedes W124 cooling system repair`, `Mercedes OM602 timing chain replacement`,
     `Mercedes W124 diesel fuel filter change`, `Mercedes W124 glow plug replacement OM602`
7. **MBturbo.com** — how-to's over differentielen, bakken, motorswaps.

### 9.2 Online bronnen

- w124performance.com – complete service manuals (PDF) voor OM602/OM603
- mbmanuals.com – downloadbare werkplaatshandboeken per motor
- benzworld.org/forums – groot W124-forum
- peachparts.com – uitstekend forum voor technische vragen
- mbturbo.com – differentieelverhoudingen, how-to's, dieselprojecten
- Boek: "Jetzt helfe ich mir selbst" Nr. 123 – W124 200D/250D/300D reparatiehandboek (Duits, zeer compleet)
- Uit dit project (01-11-2026): fabriekshandboek-scans 0780/0781 (brandstoffilter), W124 Complete Guide
  (sites.google.com/view/mercedesbenzw124), ADAC-autokatalog, W124-Board.de, MercedesForum.nl

---

## Module 10: Samenvatting & businessmodel opknappers

### 10.1 Quick reference card

| Onderwerp | OM602 (250D) | OM603 (300D) |
|---|---|---|
| Cilinders | 5 in lijn | 6 in lijn |
| Inhoud | 2.497 cc | 2.996 cc |
| Vermogen | 90 pk | 109 pk |
| Betrouwbaarheid | Legendarisch (1M+ km) | Goed, maar kop-risico |
| Distributie | Duplex ketting | Duplex ketting |
| Injectie | Bosch PES lijn, IDI | Bosch PES lijn, IDI |
| Koeling | Water, viscokoppeling | Water, viscokoppeling |
| Olie | 15W-40 diesel | 15W-40 diesel |
| Aandrijving | RWD, 185 mm diff | RWD, 185 mm diff |
| Zwakke plek | Motorsteunen, trillingen | Cilinderkop mal #14 |

### 10.2 Businessmodel: opknappen & doorverkopen

- **Inkoop Duitsland:** mobile.de, autoscout24.de. Filter op "TÜV neu" voor recente keuring. Budget: € 1.500–€ 4.000 voor goede basis.
- **Inkoop Spanje:** milanuncios.com, coches.com. Zoek "Mercedes 250D" of "300D W124". Budget: € 1.000–€ 3.000. Let op: ITV-keuring (Spaanse APK).
- **Focus op de 250D (OM602):** beste motor voor doorverkoop. Vraag is hoog, motorproblemen zeldzaam, "million mile engine" verkoopt zichzelf.
- **Opknap-prioriteiten:** 1) roest verhelpen, 2) koelsysteem vernieuwen, 3) filters en olie verversen, 4) remmen controleren, 5) interieur opfrissen. Met € 500–€ 1.500 aan onderdelen kun je een goede basisauto verkoopklaar maken.
- **Verkoop Nederland:** Marktplaats.nl, Facebook W124-groepen. Pre-1986 modellen zijn 40+ jaar oud en kwalificeren als oldtimer met voordelen bij wegenbelasting. Verkoopprijs goede 250D: € 4.000–€ 8.000 afhankelijk van staat.

---

*Einde training – succes met je W124! Vragen? Neem de modules opnieuw door of zoek de aanbevolen video's op.*
