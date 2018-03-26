#! Python 3.6.4

import requests, bs4
import datetime
import re
import matplotlib.pyplot as plt

regex_number = '(?P<number>[0-9]+)'
regex_day = '(?P<strDay>[a-zA-Z]+) (?P<day>[0-9]+) '
regex_monthyear = '(?P<strMonth>[a-z]+) (?P<year>[0-9]+)'
regex_date = regex_day + regex_monthyear
regex_time = 'Aanvang (?P<hour>[0-9]+):(?P<minute>[0-9]+) uur'

# NOTE: Voorzitter is lid van de TK, dus moet ook op de namenlijst staan.
# TODO: Namenlijst huidige kamerleden gebruiken in plaats van regex voor
#       aanwezige kamerleden.
regex_voorzitter = 'Voorzitter: (?P<voorzitter>[a-zA-Z]+)'
regex_aanwezig = 'Aanwezig zijn (?P<aanwezig>[0-9]+)'
# regex_parlement = '(?P<naam>[^\n,]+)(,| en )'
# regex_kabinet = ''


def download_document(url, soup=True):
    """ Downloads document from url, uses soup as default output. """
    document = requests.get(url)
    document.raise_for_status()

    if soup:
        document_soup = bs4.BeautifulSoup(document.text, 'html.parser')
        return document_soup
    else:
        return document


def parse_number(str_nummer):
    """ Get the number from nummer tag. """
    match = re.search(regex_number, str_nummer)
    if match:
        number = match.group('number')
        return number
    else:
        print('Whoops, something went wrong in parse_number!')


def convert_dutch_month(month):
    """ Convert Dutch name of months to numbers. """
    return {
        'januari'   :  1,
        'februari'  :  2,
        'maart'     :  3,
        'april'     :  4,
        'mei'       :  5,
        'juni'      :  6,
        'juli'      :  7,
        'augustus'  :  8,
        'september' :  9,
        'oktober'   : 10,
        'november'  : 11,
        'december'  : 12
    }[month]


def parse_datetime(str_datum, str_tijd):
    """ Parse date and time strings to return a single date-time object. """
    match_date = re.search(regex_date, str_datum)
    match_time = re.search(regex_time, str_tijd)
    print('Match date:\n')
    print(match_date)
    print('Match time:\n')
    print(match_time)
    if match_date and match_time:
        day = int(match_date.group('day'))
        int_month = int(convert_dutch_month(match_date.group('strMonth')))
        year = int(match_date.group('year'))
        hour = int(match_time.group('hour'))
        minute = int(match_time.group('minute'))
        date_and_time = datetime.datetime(day=day, 
                                          month=int_month, 
                                          year=year, 
                                          hour=hour, 
                                          minute=minute)
        return date_and_time
    else:
        print("Whoops, something went wrong in parse_datetime!")


def parse_al_tags(al_item):
    print("Parsing al tags, there are four kinds in the opening type.")
    # TODO: Remove obsolete function, see what can be reused.

    match_voorzitter = re.search(regex_voorzitter, al_item)
    match_aanwezig = re.search(regex_aanwezig, al_item)
    # match_parlement = re.search(regex_parlement, al_item)
    # match_kabinet = re.search(regex_kabinet, al_item)

    voorzitter = ''
    aanwezig = ''
    parlementsleden = ''
    kabinetsleden = ''

    if match_voorzitter:
        voorzitter = match_voorzitter.group('voorzitter')
        print("Voorzitter: %s" % voorzitter)
    elif match_aanwezig:
        aanwezig = int(match_aanwezig.group('aanwezig'))
        print("Aantal aanwezigen: %s" % aanwezig)
    # elif match_parlement:
        # print("Namen parlementsleden")
        # TODO: Check if number of parsed names == aantal aanwezigen.
    # elif match_kabinet:
        # print("Namen en functies kabinetsleden")
    else:
        print("WELP, there's a kind that's not one of the above.")
    return [voorzitter, aanwezig, parlementsleden, kabinetsleden]


def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{p:.2f}%  ({v:d})'.format(p=pct,v=val)
    return my_autopct


def plot_present_over_time(present_mps, date_and_time):
    print("Plot a bar chart of present per day/vergadernummer.")

def plot_present_mps(present_mps, date_and_time):
    print("Plotting a pie chart with number of present MPs")
    # NOTE: Magic number, even though I don't expect this to change soon.
    total_mps = 150
    absent_mps = total_mps - present_mps

    values = [present_mps, absent_mps]
    labels = ['Aanwezig (%i)' % present_mps, 
              'Afwezig (%i)' % absent_mps]
    # Plot
    plt.pie(values,
            autopct=make_autopct(values),
            startangle=90,
            counterclock=True)

    plt.title('Opening\n%s' % str(date_and_time))
    plt.axis('equal')
    plt.legend(labels, loc='lower left')
    plt.show()

document_soort = 'h' # handeling
instantie = 'tk' # tweede kamer
vergaderjaar = 20172018 # samenstelling van twee opvolgende jaren
max_volnummer = 1 # range van 

def process_handelingen():
    # TODO: How to figure out the vergaderjaar and volgnummer?
    # NOTE: Hardcoded base URL, kind of a magic number.
    base_url = 'https://zoek.officielebekendmakingen.nl/h-tk-20172018-'
    # FIXME: Hardcoded range, base this on URL?
    for i in range(50, 52):
        print('i: %i' % i)
        download_url = base_url + str(i) + '-1.xml'
        handeling_soup = download_document(download_url)

        # TODO: Check if number == i
        # NOTE: Working under the assumption that 'vergadering-nummer', 
        # 'vergaderdatum' and 'vergadertijd' always consist of one element.
        str_nummer = str(handeling_soup.select('vergadering-nummer'))
        number = parse_number(str_nummer)
        print('Number of current handeling: %s' % number)

        str_datum = str(handeling_soup.select('vergaderdatum'))
        str_tijd = str(handeling_soup.select('vergadertijd'))
        print('Datum: %s' % str_datum)
        print('Datum: %s' % str_tijd)

        date_and_time = parse_datetime(str_datum, str_tijd)
        print('Date and time of current handeling: %s' % date_and_time)

        # DONE: Put both month and date into a single datetime object.
        al = handeling_soup.select('al')

        for item in al:
            print('Here I will parse the \'al\' tags')
            match_aanwezig = re.search(regex_aanwezig, str(item))

            if match_aanwezig:
                aanwezig = int(match_aanwezig.group('aanwezig'))
                plot_present_mps(aanwezig, date_and_time)


if __name__ == '__main__':
    process_handelingen()

#   <al-groep> bevat de volgende data in <al> tags.
#       Voorzitter:\s(?P<Voorzitter>[a-zA-Z]+)
#       Voorzitter.             <nadruk type="vet">Voorzitter: naam</nadruk>
#       Aantal aanwezigen.      Aanwezig zijn ### leden der Kamer, te weten:
#                               
#       Aanwezigen parlement.   Naam, Naam, ..., Naam en Naam,
#       Aanwezigen kabinet.     en Naam, positie, ..., en Naam, positie.