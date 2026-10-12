# CLAUDE.md - Project Memory

## DEPLOYMENT LESSONS LEARNED

### Bij elke deployment/herstart ALTIJD doen:

1. **Stop alle Python processen (PowerShell - meest betrouwbaar):**
   ```powershell
   powershell -Command "Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force"
   ```

2. **CONTROLEER of poort vrij is (KRITIEK!):**
   ```bash
   netstat -ano | findstr ":5000.*LISTENING"
   ```
   - Er mag maar **1 proces** LISTENING zijn, of geen
   - Bij meerdere processen: kill ze allemaal op PID!

3. **Bij meerdere processen op zelfde poort - kill op PID:**
   ```bash
   taskkill /F /PID <pid1> /PID <pid2> /PID <pid3>
   ```

4. **Verwijder __pycache__ folders:**
   ```powershell
   powershell -Command "Get-ChildItem -Recurse -Directory -Filter '__pycache__' | Remove-Item -Recurse -Force"
   ```

5. **Start server opnieuw:**
   ```bash
   python web_app.py
   ```

6. **Verifieer 1 proces:**
   ```bash
   netstat -ano | findstr ":5000.*LISTENING"
   ```

7. **Browser: incognito venster of hard refresh:**
   ```
   Ctrl + Shift + N (incognito) of Ctrl + Shift + R
   ```

### Waarom?
- Python cached gecompileerde .pyc bestanden in __pycache__
- Oude code blijft actief zolang server draait
- **MEERDERE processen op dezelfde poort** = browser connect naar oude versie!
- `taskkill /F /IM python.exe` stopt niet altijd alle processen
- Templates en wijzigingen worden pas zichtbaar na volledige herstart

### Quick Deploy Command (Windows):
```powershell
powershell -Command "Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force; Get-ChildItem -Recurse -Directory -Filter '__pycache__' | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
```
Wacht 2 seconden, dan:
```bash
python web_app.py
```

---

## Project Info
- **Naam:** Mercedes W123/W124 Diesel Finder
- **Poort:** 5000
- **Database:** mercedes_diesel.db
- **Scheduler:** Dagelijks om 06:00

---

## Uitgebreide Lessons Learned

Voor een volledige lijst van alle lessons learned uit dit project, zie **[LESSONS_LEARNED.md](LESSONS_LEARNED.md)**

Belangrijkste categorieën:
1. **Deployment & Server Management** - Process killing, cache clearing, multi-process issues
2. **Web Scraping** - Bot detection, rate limiting, HTML structure changes, multiple sources
3. **Data Management** - Duplicate detection, data preservation, filtering strategies
4. **Data Extraction & Parsing** - Multiple date formats, classic vs modern filtering, price parsing
5. **Code Architecture** - Graceful degradation, modular design, error isolation
6. **Testing & Debugging** - Incremental testing, backup versions, git restore strategies
7. **Project Scope Evolution** - Focus refinement, feature additions, user feedback
8. **Platform-Specific Issues** - UTF-8 encoding, PythonAnywhere deployment
