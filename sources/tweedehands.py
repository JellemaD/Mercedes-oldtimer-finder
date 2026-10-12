"""2dehands (BE): same platform and API as Marktplaats, see marktplaats.search_lrp()."""

from .marktplaats import search_lrp

NAME = '2dehands'
COUNTRY = 'BE'
RUNNER = 'github'

BASE = 'https://www.2dehands.be'


def scrape():
    return search_lrp(BASE, NAME, COUNTRY, '2dh_')
