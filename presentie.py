import datetime
import re
import matplotlib.pyplot as plt
import pandas

from handelingen import download_document, generate_url

regex_number = '(?P<number>[0-9]+)'
regex_day = '(?P<strDay>[a-zA-Z]+) (?P<day>[0-9]+) '
regex_monthyear = '(?P<strMonth>[a-z]+) (?P<year>[0-9]+)'
regex_date = regex_day + regex_monthyear
regex_time = 'Aanvang (?P<hour>[0-9]+):(?P<minute>[0-9]+) uur'


# Example URL: https://zoek.officielebekendmakingen.nl/h-tk-20162017-1-1.html
base_url = 'https://zoek.officielebekendmakingen.nl/h-tk-'
document_soort = 'h' # handeling
instantie = 'tk' # tweede kamer
vergaderjaren = [#20112012, 
                 #20122013, 
                 #20132014, 
                 #20142015, 
                 # 20152016, 
                 20162017, 
                 20172018]

# vergaderjaar = 20172018 # samenstelling van twee opvolgende jaren
max_volnummer = 1 # How to determine the max?

# NOTE: Magic number, even though I don't expect this to change soon.
total_mps = 150

# NOTE: Voorzitter is lid van de TK, dus moet ook op de namenlijst staan.
# TODO: Namenlijst huidige kamerleden gebruiken in plaats van regex voor
#       aanwezige kamerleden.
regex_voorzitter = 'Voorzitter: (?P<voorzitter>[a-zA-Z]+)'
regex_aanwezig = 'Aanwezig zijn (?P<aanwezig>[0-9]+)'
# regex_parlement = '(?P<naam>[^\n,]+)(,| en )'
# regex_kabinet = ''

sample_outfile = 'data/sample_data.csv'


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


def read_data_csv(infile):
    """ Read CSV file to pandas dataframe. """
    return pandas.read_csv(infile, sep=',')


def save_data_csv(dataframe, outfile, append=False):
    """ Save pandas dataframe to CSV file, with option to append. """

    if not append:
        print('Not appending data to existing csv')
        dataframe.to_csv(outfile, sep=',')
    else:
        print('Appending data to existing csv')
        dataframe.to_csv(outfile, sep=',', mode='a')


def process_opening_presentie(base_url):
    """ Parse opening and presentie file, save data to CSV. """

    doc_nr = 1

    for vergaderjaar in vergaderjaren:
        print(vergaderjaar)
        presentiedata = pandas.DataFrame(columns=['volgnummer', 
                                                  'datumtijd', 
                                                  'aanwezig'])

        # FIXME: Hardcoded range for testing purposes.
        for i in range(1,3):

            download_url = generate_url(vergaderjaar, i, doc_nr)
            handeling_soup = download_document(download_url)

            # TODO: Check if number == i
            # NOTE: Working under the assumption that 'vergadering-nummer', 
            # 'vergaderdatum' and 'vergadertijd' always consist of one element.
            str_nummer = str(handeling_soup.select('vergadering-nummer'))
            number = parse_number(str_nummer)
            str_datum = str(handeling_soup.select('vergaderdatum'))
            str_tijd = str(handeling_soup.select('vergadertijd'))
            date_and_time = parse_datetime(str_datum, str_tijd)

            volgnummer = str(vergaderjaar) + '-' + number

            # DONE: Put both month and date into a single datetime object.
            al = handeling_soup.select('al')

            for item in al:
                match_voorzitter = re.search(regex_voorzitter, str(item))
                match_aanwezig = re.search(regex_aanwezig, str(item))

                if match_aanwezig:
                    aanwezig = int(match_aanwezig.group('aanwezig'))
                if match_voorzitter:
                    print(match_voorzitter)
                else:
                    print('Not match voorzitter!')
            
            presentiedata = presentiedata.append({'volgnummer': volgnummer, 
                                                'datumtijd': date_and_time,
                                                'aanwezig': aanwezig},
                                                ignore_index=True)

        outfile = 'data/' + str(vergaderjaar) + '_presentiedata.csv'
        save_data_csv(presentiedata, outfile)

# TODO: Add routine to 

if __name__ == '__main__':
    process_opening_presentie(base_url)
