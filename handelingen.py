import requests
import bs4
import re

# TODO: Fetch complete set of handelingen for a date.

# https://zoek.officielebekendmakingen.nl/h-tk-20172018-61-1.html
base_doc_url = 'https://zoek.officielebekendmakingen.nl/h-tk-'
# https://zoek.officielebekendmakingen.nl/handelingen/TK/2017-2018/61/
base_ovz_url = 'https://zoek.officielebekendmakingen.nl/handelingen/TK/'

regex_publicaties = 'Aantal publicaties: <strong>(?P<aantal>[0-9]+)'

def insert_dash(original):
    '''Inserts new inside original at pos.'''
    return original[:4] + '-' + original[4:]

def generate_ovz_url(vergaderjaar, volgnummer):
    print('Generate overzicht url om aantal documenten uit te halen')

    vergaderjaar_dash = insert_dash(str(vergaderjaar))
    ovz_url = base_ovz_url + vergaderjaar_dash + '/' + str(volgnummer) + '/'
    return ovz_url

def generate_doc_url(vergaderjaar, volgnummer, docnummer):
    """ Generate url based on variables """

    custom = str(vergaderjaar) + '-' + str(volgnummer) + '-' + str(docnummer)
    complete_url = base_doc_url + custom + '.xml'
    return complete_url


def download_document(url, soup=True):
    """ Downloads document from url, uses soup as default output. """

    document = requests.get(url)
    document.raise_for_status()

    if soup:
        document_soup = bs4.BeautifulSoup(document.text, 'html.parser')
        return document_soup
    else:
        return document


def fetch_aantal_vergaderitems(vergaderjaar, volgnummer):
    print('Haal aantal publicaties voor vergadering van de website')

    ovz_url = generate_ovz_url(vergaderjaar, volgnummer)
    print(ovz_url)
    document = download_document(ovz_url, soup=False)
    # print(document.text)
    match_aantal_items = re.search(regex_publicaties, document.text)
    aantal_items = int(match_aantal_items.group('aantal'))
    print(aantal_items)
    return aantal_items


def fetch_alle_vergaderitems(vergaderjaar, volgnummer):
    aantal_items = fetch_aantal_vergaderitems(vergaderjaar, volgnummer)
    
    # NOTE: Volgnummer is index 1 numbered.
    for i in range(1, aantal_items + 1):
        print('Volgnummer %i' % i)
        url = generate_doc_url(vergaderjaar, volgnummer, i)
        print(url)
        document = download_document(url)
        document_title = str(document.select('item-titel'))
        print(document_title)

        # TODO: Do something with the retrieved document.


def fetch_vergaderingen_voor_jaar(vergaderjaar):
    # TODO: Voor alle vergaderingen in het jaar: haal alle items op.
    print('Fetch alle vergaderingen')

    # FIXME: Hardcoded volgnummer for testing.
    fetch_alle_vergaderitems(vergaderjaar, 61)

if __name__ == '__main__':
    fetch_vergaderingen_voor_jaar(20172018)

# STRUCTURE
# Vergaderjaar  20172018
#   Vergadering 1:n
#       Stuk    1:m