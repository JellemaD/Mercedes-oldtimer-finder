"""
Keep only cars from dry regions without road salt (Durk: "no rust, so no snow and salt").

    ES  drop the wet north (Galicia, Asturias, Cantabria, Basque Country, Navarra, La Rioja), the
        cold salted plateau (Castilla y León, Huesca, Teruel) and Canarias/Ceuta/Melilla (outside the
        EU VAT area: customs)
    PT  drop the rainy north-west and the cold interior (Viana do Castelo, Braga, Porto, Vila Real,
        Bragança, Viseu, Guarda) and the islands
    GR  drop Epirus and Western Macedonia (snow, salt on the mountain roads)
    FR  keep only the Mediterranean departments (06, 13, 83, 84, 30, 34, 11, 66, Corsica)
    IT  keep only the south and the islands (Lazio without Rieti, Campania, Puglia, Basilicata,
        Calabria, Sicily, Sardinia)
    NL, BE, DE: salt countries, kept for now (the photo rust check judges those cars).

A location we can't place is kept: better one car too many than a good one missed.
region_ok(country, location) -> (ok, reason)
"""

import re
import unicodedata


def _plain(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower()
    return re.sub(r'\s+', ' ', s).strip()


# Spain: province names (as sites write them) and 2-digit postcode prefixes to DROP
ES_DROP_NAMES = {
    'a coruna', 'la coruna', 'coruna', 'lugo', 'ourense', 'orense', 'pontevedra', 'asturias', 'oviedo',
    'cantabria', 'santander', 'alava', 'araba', 'guipuzcoa', 'gipuzkoa', 'vizcaya', 'bizkaia', 'bilbao',
    'navarra', 'pamplona', 'la rioja', 'rioja', 'logrono', 'avila', 'burgos', 'leon', 'palencia',
    'salamanca', 'segovia', 'soria', 'valladolid', 'zamora', 'huesca', 'teruel', 'las palmas',
    'santa cruz de tenerife', 'sta. c. tenerife', 'tenerife', 'ceuta', 'melilla',
}
ES_DROP_ZIP = {'15', '27', '32', '36', '33', '39', '01', '20', '48', '31', '26', '05', '09', '24', '34',
               '37', '40', '42', '47', '49', '22', '44', '35', '38', '51', '52'}
PT_DROP_DISTRICTS = {'viana do castelo', 'braga', 'porto', 'vila real', 'braganca', 'viseu', 'guarda',
                     'acores', 'azores', 'madeira', 'ilha da madeira', 'ponta delgada', 'funchal'}
GR_DROP_ZIP = {'44', '45', '46', '48', '50', '51', '52', '53'}
FR_KEEP_ZIP = {'06', '13', '83', '84', '30', '34', '11', '66', '20'}
IT_KEEP_ZIP = {'00', '01', '03', '04', '07', '08', '09', '70', '71', '72', '73', '74', '75', '76',
               '80', '81', '82', '83', '84', '85', '87', '88', '89', '90', '91', '92', '93', '94',
               '95', '96', '97', '98'}


def _zip(loc):
    m = re.search(r'\b(\d{5})\b', loc or '')
    return m.group(1) if m else None


def region_ok(country, location):
    loc = _plain(location)
    z = _zip(location)
    if country == 'ES':
        if z and z[:2] in ES_DROP_ZIP:
            return False, 'natte/koude regio (ES)'
        parts = [p.strip() for p in loc.split(',')]
        if any(p in ES_DROP_NAMES for p in parts) or loc in ES_DROP_NAMES:
            return False, 'natte/koude regio (ES)'
    elif country == 'PT':
        district = loc.split(',')[-1].strip() if loc else ''
        if district in PT_DROP_DISTRICTS:
            return False, 'natte/koude regio (PT)'
    elif country == 'GR':
        if z and z[:2] in GR_DROP_ZIP:
            return False, 'bergregio met sneeuw (GR)'
    elif country == 'FR':
        if not z or z[:2] not in FR_KEEP_ZIP:
            return False, 'niet het Middellandse Zee-gebied (FR)'
    elif country == 'IT':
        if not z or z[:2] not in IT_KEEP_ZIP:
            return False, 'niet Zuid-Italië of eilanden (IT)'
    return True, ''
