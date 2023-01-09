from google.cloud import memcache

def get_tle_memcache(norad):
    '''
    Getting tle from memcache or query
    '''

    print("searching in memcache")

    TLE_lines = memcache.get(f"{norad}")

    # If not found, query from celestrak and add to database
    if TLE_lines is None:
        TLE_lines = query_tle(norad)

        # Check is existing norad
        if len(TLE_lines) != 3:
            return None

        memcache.add(key=f"{norad}", value=TLE_lines, time=6 * 60 * 60)

    return TLE_lines

def query_tle(norad):
    '''
    Request the tle from a specific satellite from celestrek.org
    '''

    # Download TLE of last known position
    URL = f'https://celestrak.org/NORAD/elements/gp.php?CATNR={norad}FORMAT=TLE'
    TLE_string = urlopen(URL).read().decode('utf-8')
    TLE_lines = TLE_string.strip().splitlines()

    return TLE_lines