# LESSONS LEARNED - Mercedes W123/W124 Diesel Finder

## 1. DEPLOYMENT & SERVER MANAGEMENT

### Python Cache Problemen
- **Probleem:** Python cache `.pyc` files in `__pycache__` blijven oude code uitvoeren
- **Oplossing:** Altijd `__pycache__` verwijderen bij deployment
- **Lesson:** Cache clearing moet onderdeel zijn van deployment routine

### Meerdere Python Processen
- **Probleem:** Meerdere Python processen draaien op dezelfde poort (5000)
- **Gevolg:** Browser connect naar oude versie, wijzigingen niet zichtbaar
- **Oplossing:**
  - Gebruik `netstat -ano | findstr ":5000"` om alle processen te checken
  - Kill alle processen op PID: `taskkill /F /PID <pid1> /PID <pid2>`
  - `taskkill /F /IM python.exe` werkt niet altijd betrouwbaar
- **Lesson:** Altijd verifiëren dat er maar 1 proces draait op de poort

### Browser Caching
- **Probleem:** Browser toont oude versie ondanks server restart
- **Oplossing:** Gebruik Incognito mode of Ctrl+Shift+R (hard refresh)
- **Lesson:** Bij testen altijd incognito venster gebruiken

## 2. WEB SCRAPING

### Bot Detection
- **Probleem:** Websites blokkeren automatische requests
- **Oplossing:** Realistic User-Agent headers gebruiken
```python
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...',
    'Accept-Language': 'nl-NL,nl;q=0.9,en;q=0.8',
}
```
- **Lesson:** Altijd browser-achtige headers meesturen

### Rate Limiting
- **Probleem:** Te snelle requests resulteren in bans
- **Oplossing:** `time.sleep(1-2)` tussen requests
- **Lesson:** Be polite to scraped websites

### Marktplaats Scraper Instabiliteit
- **Probleem:** Marktplaats HTML structuur verandert vaak, scraper breekt regelmatig
- **Commits:**
  - `ad0bbd3` - Restore working MarktplaatsScraper from earlier commit
  - `b03f16d` - Skip broken Marktplaats in unified_scraper_v2
- **Oplossing:**
  - Multiple scrapers maken (backup strategies)
  - Graceful degradation (continue on failure)
  - Version control om working versions te restoren
- **Lesson:** Websites kunnen hun HTML structure veranderen - maak robuuste error handling

### Multiple Sources Strategy
- **Lesson:** Niet afhankelijk zijn van 1 source
- **Oplossing:** 10+ sources geïmplementeerd:
  - Marktplaats.nl
  - AutoScout24 (NL, DE, BE)
  - eBay.de Motors
  - Kleinanzeigen.de
  - Gaspedaal.nl
  - 2dehands.be
  - AutoTrack.nl
  - AutoWereld.nl

### Error Handling Per Scraper
```python
try:
    results = scrape_autoscout24_json(country='de')
    all_results.extend(results)
    print(f"✅ Added {len(results)} ads")
except Exception as e:
    print(f"❌ Error: {e}")
    # Continue to next scraper!
```
- **Lesson:** 1 kapotte scraper mag niet hele proces stoppen

## 3. DATA MANAGEMENT

### Duplicate Detection
- **Probleem:** Dezelfde advertentie kan meerdere keren gevonden worden
- **Oplossing:** `external_id` als UNIQUE key in database
```python
'external_id': f'mp_nl_{id}',  # Format: source_country_id
```
- **Lesson:** Gestandaardiseerde ID format voorkomt duplicates

### is_active Flag vs Deletion
- **Commit:** `ac0de21` - Disable mark_inactive_ads to preserve old listings
- **Lesson:** Oude advertenties bewaren i.p.v. verwijderen
- **Reden:** Als scraper faalt, wil je oude data behouden
```python
# NOTE: We do NOT call mark_inactive_ads()
# This preserves old listings that couldn't be re-scraped
```

### Data Filtering
- **Year filtering:** Alleen 1979-1986 (oldtimer belasting vrijstelling)
```python
AND (year IS NULL OR (year >= 1979 AND year <= 1986))
```
- **Price filtering:** > 500 EUR om onderdelen/junk uit te filteren
```python
AND (price IS NULL OR price > 500)
```
- **Lesson:** Business logic filters in database queries = sneller en cleaner

### Search Term Precision
- **Probleem:** Te brede search terms (bijv. "mercedes diesel") geven moderne auto's
- **Oplossing:** Specifieke termen: 'w123 diesel', 'mercedes 240d', etc.
- **Lesson:** Narrow & specific > broad search terms

## 4. DATA EXTRACTION & PARSING

### Multiple Date Formats
```python
# Support: EZ 02/1986, Erstzulassung 02/1986, Bj. 1986, 1986-02, 1986
ez_match = re.search(r'(?:EZ|Erstzulassung|Bj\.?|Baujahr)?\s*(\d{1,2})[/.-]?(19[789]\d|199[0-7])', text)
```
- **Lesson:** Europese sites gebruiken verschillende datum formats - support ze allemaal

### Classic vs Modern Mercedes Filtering
- **Probleem:** Zoeken op "Mercedes diesel" geeft ook moderne modellen (GLC, CLA, etc.)
- **Oplossing:** Keyword lists:
```python
CLASSIC_KEYWORDS = ['w123', 'w124', '200d', '240d', '300d']
MODERN_KEYWORDS = ['glc', 'gle', 'cla', 'amg', '4matic', 'hybrid']
```
- **Lesson:** Content-based filtering essentieel bij broad searches

### Diesel vs Benzine
- **Probleem:** 200E = benzine, 200D = diesel (E = Einspritzung)
- **Oplossing:** Explicit benzine exclusion list
```python
BENZINE_KEYWORDS = ['200e', '230e', '280e', 'benzine', 'petrol']
```
- **Lesson:** Domain knowledge = betere filters

### Price Parsing
```python
# Handle: €15.000, € 15000, EUR 15,000
price_clean = re.sub(r'[€$£\s.]', '', price_text)
price_clean = price_clean.replace(',', '.')
```
- **Lesson:** Multiple currency formats ondersteunen

## 5. CODE ARCHITECTURE

### Evolution: unified_scraper v1 → v2
- **v1:** Alle scrapers samen, alles moet werken
- **v2:** Only working scrapers, skip broken ones
- **Commit:** `b03f16d` - Add unified_scraper_v2
- **Lesson:** Graceful degradation > all-or-nothing approach

### Modular Scraper Design
```
fetch_real_data.py         - Marktplaats + AutoScout24
scrape_extra_sources.py    - All other sources
unified_scraper_v2.py      - Orchestrator
```
- **Lesson:** Separate concerns = makkelijker te debuggen en onderhouden

### Try/Except per Scraper
- **Pattern:** Elke scraper in eigen try/except block
- **Voordeel:** 1 kapotte scraper stopt niet hele proces
- **Lesson:** Isolate failures

### Import Error Handling
```python
try:
    from scrape_extra_sources import scrape_autoscout24_json
except ImportError as e:
    print(f"ERROR: Could not import: {e}")
    sys.exit(1)
```
- **Lesson:** Fail fast en duidelijk bij missing dependencies

## 6. TESTING & DEBUGGING

### Test File Proliferation
- **Observatie:** 10+ test/debug files in git status:
  - `test_marktplaats_scraper.py`
  - `test_pagination.py`
  - `test_price_parsing.py`
  - `debug_scraper.py`, `debug_scraper2.py`
- **Lesson:** Incremental testing approach werkt goed voor web scraping
- **Best Practice:** Test individuele componenten (price parsing, pagination, etc.)

### Backup Versions
- `fetch_real_data_backup.py` aanwezig in project
- **Lesson:** Keep working versions before major refactors

### Git Restore Strategy
- **Commit:** `ad0bbd3` - Restore working MarktplaatsScraper from `4e3fddf`
- **Lesson:** Git history is je veiligheidsnet - commit werkende versies vaak

## 7. PROJECT SCOPE EVOLUTION

### Focus Shift: W123/W124 → 190/200 Series (1979-1986)
- **Initial:** Breed (W123, W124 diesels)
- **Refined:** Alleen 190/200 series 1979-1986
- **Commit:** `473ffb6` - Refactor for 190/200 series diesel only
- **Reden:** Oldtimer belasting vrijstelling (≤1987)
- **Lesson:** Domain requirements kunnen leiden tot scope refinement

### Feature Additions
- **Commit:** `cd0e225` - Add 5/6 cylinder filter for 1985-1987
- **Commit:** `0d06bb4` - Hot filter, Type kolom, sorteerbare tabel
- **Commit:** `93c1160` - Datum Ad column
- **Lesson:** User feedback → iterative feature additions

### Listing Limit Increase
- **Commit:** `66619dc` - Increase limit from 50 to 500
- **Commit:** `4bbf535` - Keep limit=500
- **Lesson:** Initial estimates kunnen te conservatief zijn

## 8. PLATFORM-SPECIFIC ISSUES

### Windows UTF-8 Encoding
```python
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```
- **Lesson:** Windows console heeft UTF-8 fix nodig voor special characters

### PythonAnywhere Deployment
- Separate deployment guide en scripts gemaakt
- **Files:** `PYTHONANYWHERE_GUIDE.md`, `pythonanywhere_wsgi.py`
- **Lesson:** Production environment ≠ development environment

## 9. KEY TAKEAWAYS

### Wat Goed Werkte
1. **Multiple sources:** Niet afhankelijk van 1 website
2. **Graceful degradation:** Continue on failure
3. **Git version control:** Easy restore van working versions
4. **Modular design:** Elke scraper is onafhankelijk
5. **Incremental testing:** Test individuele componenten
6. **Domain filtering:** Specifieke keywords voor betere resultaten

### Wat Challenging Was
1. **HTML structure changes:** Websites veranderen vaak
2. **Bot detection:** Constant headers aanpassen
3. **Deployment caching:** Python/browser cache issues
4. **Multi-process debugging:** Meerdere processen op zelfde poort
5. **Data quality:** Filtering nodig voor relevante results

### Best Practices voor Volgende Projecten
1. **Deployment routine maken vanaf dag 1** (process kill, cache clear, verify)
2. **Error isolation:** Elke component kan falen zonder hele systeem te stoppen
3. **Version control:** Commit vaak, especially working versions
4. **Test isolation:** Separate test files voor elke component
5. **Domain knowledge:** Investeer tijd in understanding business requirements
6. **Backup strategies:** Multiple scrapers, fallbacks, preserved data
7. **Platform-specific issues:** Fix early (UTF-8, etc.)
8. **Monitor & iterate:** User feedback → feature additions

---

**Project:** Mercedes W123/W124 Diesel Finder
**Timeline:** Initial commit → 20+ commits
**Current Status:** Production (PythonAnywhere, port 5000)
**Database:** mercedes_diesel.db (500+ listings from 10+ sources)
