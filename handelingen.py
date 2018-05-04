import requests
import bs4
import re

# https://zoek.officielebekendmakingen.nl/h-tk-20172018-61-1.html
base_doc_url = 'https://zoek.officielebekendmakingen.nl/'
# https://zoek.officielebekendmakingen.nl/handelingen/TK/2017-2018/61/
base_ovz_url = 'https://zoek.officielebekendmakingen.nl/handelingen/TK/'

regex_publicaties = 'Aantal publicaties: <strong>(?P<aantal>[0-9]+)'

def insert_dash(original):
    """Insert dash between two years (eg 20172018 becomes 2017-2018)."""
    return original[:4] + '-' + original[4:]

def generate_ovz_url(vergaderjaar, volgnummer):
    """Generate overzicht url om aantal documenten uit te halen"""

    vergaderjaar_dash = insert_dash(str(vergaderjaar))
    ovz_url = base_ovz_url + vergaderjaar_dash + '/' + str(volgnummer) + '/'
    return ovz_url

def generate_doc_url(vergaderjaar, volgnummer, docnummer):
    """ Generate url based on variables """

    # Necessary conversions to strings.
    vergaderjaar = str(vergaderjaar)
    volgnr = str(volgnummer)
    docnr = str(docnummer)

    filename = 'h-tk-' + vergaderjaar + '-' + volgnr + '-' + docnr + '.xml'
    complete_url = base_doc_url + filename
    return complete_url, filename


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
    """Haal aantal publicaties voor vergadering van de website."""

    ovz_url = generate_ovz_url(vergaderjaar, volgnummer)
    document = download_document(ovz_url, soup=False)
    match_aantal_items = re.search(regex_publicaties, document.text)
    aantal_items = int(match_aantal_items.group('aantal'))
    return aantal_items


def save_handeling_document(filename, document):
    """Sla handeling op als XML-file mbv BeautifulSoup.prettify()."""

    savefilename = 'sourcefiles/' + filename
    print('Saving file to: %s' % savefilename)
    savefile = open(savefilename, 'w')
    savefile.write(document.prettify())


def fetch_alle_vergaderitems(vergaderjaar, volgnummer):
    """Haalt alle documenten voor een vergadering op in XML-formaat."""
    aantal_items = fetch_aantal_vergaderitems(vergaderjaar, volgnummer)
    
    # NOTE: Volgnummer is index 1 numbered.
    for i in range(1, aantal_items + 1):
        [url, filename] = generate_doc_url(vergaderjaar, volgnummer, i)
        document = download_document(url)
        save_handeling_document(filename, document)



def fetch_vergaderingen_voor_jaar(vergaderjaar):
    print('Fetch alle vergaderingen')

    # FIXME: Hardcoded number for testing.
    # i = 60

    # NOTE: Volgnummer is index 1 numbered.
    i = 1
    while True:

        print('Volgnummer: %i' % i)
        aantal_items = fetch_aantal_vergaderitems(vergaderjaar, i)
        print('Aantal items in deze vergadering: %i' % aantal_items)
        aantal_items_next = fetch_aantal_vergaderitems(vergaderjaar, i + 1)
        print('Aantal items in volgende vergadering: %i' % aantal_items_next)

        # NOTE: Assume that if the result is not 0, then it is > 0.
        # NOTE: Assume that if we have two zeros in a row, we reached the end 
        # of the year.
        if (aantal_items == 0) and (aantal_items_next != 0):
            print('Looks like we\'re missing some data, woops...')
            # TODO: Record missing data?
        elif (aantal_items == 0) and (aantal_items_next ==0):
            print('Looks like we hit the end of the stream, let\'s check.')
            vorig_aantal = fetch_aantal_vergaderitems(vergaderjaar, i-1)

            if (vorig_aantal != 0):
                print('Laatste vergadering is nummer %i met %i items' % (i-1, 
                       vorig_aantal))
                break
            else:
                print('WELP, this should not be possible!')

        print('Nu moeten alle vergaderitems worden gefetcht en verwerkt.')

        i = i + 1

if __name__ == '__main__':
    # fetch_vergaderingen_voor_jaar(20172018)

    fetch_alle_vergaderitems(20172018, 70)

# STRUCTURE
# Vergaderjaar  20172018
#   Vergadering 1:n
#       Stuk    1:m