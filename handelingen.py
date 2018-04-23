import requests
import bs4

# TODO: Fetch complete set of handelingen for a date.

def generate_url(base_url, vergaderjaar, volgnummer, docnummer):
    """ Generate url based on variables """

    custom = str(vergaderjaar) + '-' + str(volgnummer) + '-' + str(docnummer)
    complete_url = base_url + custom + '.xml'
    return complete_url


def download_document(url, soup=True):
    """ Downloads document from url, uses soup as default output. """

    # TODO: Be able to handle server errors.
    document = requests.get(url)
    document.raise_for_status()

    if soup:
        document_soup = bs4.BeautifulSoup(document.text, 'html.parser')
        return document_soup
    else:
        return document


if __name__ == '__main__':
    print('Main')