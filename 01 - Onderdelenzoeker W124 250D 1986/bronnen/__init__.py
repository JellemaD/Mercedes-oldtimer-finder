"""
Sources for the parts finder. Each module defines:
    NAME, COUNTRY
    def zoek(onderdelen) -> list[dict]   # listings (sources.common.listing()) with 'onderdeel_ids'
                                         # left empty; zoek.py matches them against the parts.
Search sites (Kleinanzeigen, Marktplaats) query per part term; forum sources list the latest
threads of their parts-for-sale section and let zoek.py match them.
The helpers in ../sources/common.py (fetch, listing, dedupe) are reused.
"""
