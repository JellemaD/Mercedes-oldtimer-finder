#!/usr/bin/env python3
"""
Unified Mercedes Diesel Scraper V2
Combines ALL sources: Marktplaats + Extra sources

Sources:
- Marktplaats.nl
- AutoScout24 (DE, NL)
- eBay.de
- Kleinanzeigen.de
- Gaspedaal.nl
- 2dehands.be
- AutoTrack.nl
- AutoWereld.nl
"""

import sys
from datetime import datetime
from database import Database
import config

def main():
    print("="*80)
    print("  UNIFIED MERCEDES DIESEL SCRAPER V2")
    print("  190/200 Series Diesel (1979-1986)")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Models: {config.MODELS}")
    print(f"Year range: {config.YEAR_FROM}-{config.YEAR_TO}")
    print()
    print("Using: Marktplaats + scrape_extra_sources.py (all sources)")
    print()

    db = Database()
    all_results = []

    # Import functions from scrape_extra_sources
    try:
        from scrape_extra_sources import (
            scrape_autoscout24_json,
            scrape_ebay_motors,
            scrape_kleinanzeigen,
            scrape_gaspedaal,
            scrape_2dehands,
            scrape_autotrack,
            scrape_autowereld
        )
    except ImportError as e:
        print(f"ERROR: Could not import scrape_extra_sources.py: {e}")
        print("Make sure scrape_extra_sources.py is in the same directory!")
        sys.exit(1)

    # Import Marktplaats from fetch_real_data
    try:
        from fetch_real_data import scrape_marktplaats
    except ImportError:
        print("WARNING: Could not import Marktplaats scraper from fetch_real_data.py")
        scrape_marktplaats = None

    # ========================================================================
    # Marktplaats.nl
    # ========================================================================
    print("\n" + "="*60)
    print("MARKTPLAATS.NL")
    print("="*60)
    if scrape_marktplaats:
        try:
            results = scrape_marktplaats()
            all_results.extend(results)
            print(f"✅ Added {len(results)} ads from Marktplaats.nl")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("⚠️  Marktplaats scraper not available")

    # ========================================================================
    # AutoScout24 Germany
    # ========================================================================
    print("\n" + "="*60)
    print("AUTOSCOUT24.DE")
    print("="*60)
    try:
        results = scrape_autoscout24_json(country='de')
        all_results.extend(results)
        print(f"✅ Added {len(results)} ads from AutoScout24.de")
    except Exception as e:
        print(f"❌ Error: {e}")

    # ========================================================================
    # AutoScout24 Netherlands
    # ========================================================================
    print("\n" + "="*60)
    print("AUTOSCOUT24.NL")
    print("="*60)
    try:
        results = scrape_autoscout24_json(country='nl')
        all_results.extend(results)
        print(f"✅ Added {len(results)} ads from AutoScout24.nl")
    except Exception as e:
        print(f"❌ Error: {e}")

    # ========================================================================
    # eBay Motors Germany
    # ========================================================================
    print("\n" + "="*60)
    print("EBAY.DE MOTORS")
    print("="*60)
    try:
        results = scrape_ebay_motors()
        all_results.extend(results)
        print(f"✅ Added {len(results)} ads from eBay.de")
    except Exception as e:
        print(f"❌ Error: {e}")

    # ========================================================================
    # Kleinanzeigen.de (formerly eBay Kleinanzeigen)
    # ========================================================================
    print("\n" + "="*60)
    print("KLEINANZEIGEN.DE")
    print("="*60)
    try:
        results = scrape_kleinanzeigen()
        all_results.extend(results)
        print(f"✅ Added {len(results)} ads from Kleinanzeigen.de")
    except Exception as e:
        print(f"❌ Error: {e}")

    # ========================================================================
    # Gaspedaal.nl
    # ========================================================================
    print("\n" + "="*60)
    print("GASPEDAAL.NL")
    print("="*60)
    try:
        results = scrape_gaspedaal()
        all_results.extend(results)
        print(f"✅ Added {len(results)} ads from Gaspedaal.nl")
    except Exception as e:
        print(f"❌ Error: {e}")

    # ========================================================================
    # 2dehands.be (Selenium required)
    # ========================================================================
    print("\n" + "="*60)
    print("2DEHANDS.BE")
    print("="*60)
    try:
        results = scrape_2dehands()
        all_results.extend(results)
        print(f"✅ Added {len(results)} ads from 2dehands.be")
    except Exception as e:
        print(f"❌ Error: {e}")

    # ========================================================================
    # AutoTrack.nl
    # ========================================================================
    print("\n" + "="*60)
    print("AUTOTRACK.NL")
    print("="*60)
    try:
        results = scrape_autotrack()
        all_results.extend(results)
        print(f"✅ Added {len(results)} ads from AutoTrack.nl")
    except Exception as e:
        print(f"❌ Error: {e}")

    # ========================================================================
    # AutoWereld.nl
    # ========================================================================
    print("\n" + "="*60)
    print("AUTOWERELD.NL")
    print("="*60)
    try:
        results = scrape_autowereld()
        all_results.extend(results)
        print(f"✅ Added {len(results)} ads from AutoWereld.nl")
    except Exception as e:
        print(f"❌ Error: {e}")

    # ========================================================================
    # Save to Database
    # ========================================================================
    print("\n" + "="*80)
    print("SAVING TO DATABASE")
    print("="*80)

    saved_count = 0
    error_count = 0
    duplicate_count = 0

    for ad in all_results:
        try:
            if db.add_advertisement(ad):
                saved_count += 1
            else:
                duplicate_count += 1
        except Exception as e:
            error_count += 1
            if error_count <= 3:  # Only show first 3 errors
                print(f"❌ Error saving ad: {e}")

    print(f"\nTotal ads scraped: {len(all_results)}")
    print(f"✅ New/updated: {saved_count}")
    print(f"⏭️  Duplicates: {duplicate_count}")
    print(f"❌ Errors: {error_count}")

    # ========================================================================
    # Final Statistics
    # ========================================================================
    stats = db.get_statistics()

    print("\n" + "="*80)
    print("DATABASE STATISTICS")
    print("="*80)
    print(f"Total active ads (1979-1986): {stats['total_active']}")
    print(f"By country: {stats['by_country']}")
    print(f"Last update: {stats['last_scrape']}")
    print()
    print("="*80)
    print(f"✅ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # NOTE: We do NOT call mark_inactive_ads()
    # This preserves old listings that couldn't be re-scraped

if __name__ == '__main__':
    main()
