import requests
import bs4
import re

# https://zoek.officielebekendmakingen.nl/h-tk-20172018-61-1.html
base_doc_url = 'https://zoek.officielebekendmakingen.nl/h-tk-'
# https://zoek.officielebekendmakingen.nl/handelingen/TK/2017-2018/61/
base_ovz_url = 'https://zoek.officielebekendmakingen.nl/handelingen/TK/'

regex_publicaties = 'Aantal publicaties: <strong>(?P<aantal>[0-9]+)'

def insert_dash(original):
    '''Inserts new inside original at pos.'''
    return original[:4] + '-' + original[4:]

def generate_ovz_url(vergaderjaar, volgnummer):
    """Generate overzicht url om aantal documenten uit te halen"""

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
    """Haal aantal publicaties voor vergadering van de website"""

    ovz_url = generate_ovz_url(vergaderjaar, volgnummer)
    document = download_document(ovz_url, soup=False)
    match_aantal_items = re.search(regex_publicaties, document.text)
    aantal_items = int(match_aantal_items.group('aantal'))
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
        # Return it?


def fetch_vergaderingen_voor_jaar(vergaderjaar):
    print('Fetch alle vergaderingen')

    i = 60
    while True:

        print('Volgnummer: %i' % i)
        aantal_items = fetch_aantal_vergaderitems(vergaderjaar, i)
        print('Aantal items in deze vergadering: %i' % aantal_items)
        aantal_items_next = fetch_aantal_vergaderitems(vergaderjaar, i + 1)
        print('Aantal items in volgende vergadering: %i' % aantal_items_next)

        # NOTE: Assume that if the result is not 0, then it is > 0.
        # NOTE: Assume that if we have two zeros in a row, we reached the end 
        # of the year.
        if (aantal_items != 0) and (aantal_items_next != 0):
            print('We\'re still in the middle of it, woop!')
        elif (aantal_items == 0) and (aantal_items_next != 0):
            print('Looks like we\'re missing some data, woops...')
        elif (aantal_items != 0) and (aantal_items_next == 0):
            print('Huidige vergadering aanwezig, we gaan door.')
        elif (aantal_items == 0) and (aantal_items_next ==0):
            print('Looks like we hit the end of the stream, let\'s check.')
            vorig_aantal = fetch_aantal_vergaderitems(vergaderjaar, i-1)

            if (vorig_aantal != 0):
                print('Laatste vergadering is nummer %i met %i items' % (i-1, 
                       vorig_aantal))
                break
            else:
                print('WELP, this should not be possible!')

        # fetch_alle_vergaderitems(vergaderjaar, i)
        print('Nu moeten alle vergaderitems worden gefetcht en verwerkt.')
        # Fetch aantal vergaderitems.
        # Als niet nul: ga verder.
            # Als volgende niet nul: ga door, record missing data.
        i = i + 1

    # FIXME: Hardcoded volgnummer for testing.
    # fetch_alle_vergaderitems(vergaderjaar, 61)

if __name__ == '__main__':
    fetch_vergaderingen_voor_jaar(20172018)

# STRUCTURE
# Vergaderjaar  20172018
#   Vergadering 1:n
#       Stuk    1:m