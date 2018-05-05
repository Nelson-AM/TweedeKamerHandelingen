regex_publicaties = 'Aantal publicaties: <strong>(?P<aantal>[0-9]+)'

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

def maak_kamerleden_regex():
    print('Maakt regex van alle achternamen van kamerleden')