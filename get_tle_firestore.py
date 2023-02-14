from urllib.request import urlopen

from google.cloud import datastore

import datetime

MAX_TLE_CACHE_TIME = 6 * 60 # Minutes

def get_tle_firestore(norad):
    '''
    This function manages the where the TLE is taken from.
    '''

    sat_data = get_satellite(norad)

    # If not found, query from celestrak and add to database
    if sat_data is None:
        TLE_lines = query_tle(norad)

        # Check if existing norad
        if len(TLE_lines) != 3:
            return None

        add_satellite(norad, TLE_lines)
        return TLE_lines

    else:
        # If expired update
        if is_expired(sat_data):
            TLE_lines = query_tle(norad)

            # Check is existing norad
            if len(TLE_lines) != 3:
                return None

            update_satellite(norad, TLE_lines)
            return TLE_lines

    #If valid, return
    return sat_data["tle_lines"]


def query_tle(norad):
    '''
    Request the tle from a specific satellite from celestrek.org
    '''

    # Download TLE of last known position
    URL = f'https://celestrak.org/NORAD/elements/gp.php?CATNR={norad}FORMAT=TLE'
    TLE_string = urlopen(URL).read().decode('utf-8')
    TLE_lines = TLE_string.strip().splitlines()

    return TLE_lines

def add_satellite(norad, tle_lines):
    '''
    Add a new satellite to the datastore
    '''

    # Prepare connection and entity
    client = datastore.Client()
    complete_key = client.key("Satellite", int(norad))
    time_now = datetime.datetime.utcnow()

    # Create entitiy
    sat = datastore.Entity(key=complete_key)

    # Insert data
    sat.update(
        {
            "tle1": tle_lines[0],
            "tle2": tle_lines[1],
            "tle3": tle_lines[2],
            "time": time_now
        }
    )

    # Upload new entity
    client.put(sat)

def get_satellite(norad):
    '''
    Retrieves the tle lines of a satellite from the firestore database
    based on the NORAD ID
    '''
    client = datastore.Client()
    key = client.key("Satellite", int(norad))
    sat = client.get(key)

    if sat == None:
        return None

    sat_data = {"norad": norad,
        "tle_lines": [sat["tle1"], sat["tle2"], sat["tle3"]],
        "year": sat["time"].year,
        "month": sat["time"].month,
        "day": sat["time"].day,
        "hour": sat["time"].hour,
        "minute": sat["time"].minute,
        "second": sat["time"].second}

    return sat_data

def is_expired(sat_data):
    '''
    Checks if the tle_lines of the satellite are expired
    '''

    # Get now time and time of tle creation in json
    time_now = datetime.datetime.utcnow()
    time_tle = datetime.datetime(sat_data["year"],
                                 sat_data["month"],
                                 sat_data["day"],
                                 hour = sat_data["hour"],
                                 minute = sat_data["minute"],
                                second = sat_data["second"])

    # If TLE not young enough, update
    if (time_now - time_tle).total_seconds() / 60.0 > MAX_TLE_CACHE_TIME:
        print("I found an expired one")
        return True

    return False

def update_satellite(norad, tle_lines):
    '''
    TODO
    '''

    client = datastore.Client()
    time_now = datetime.datetime.utcnow()

    with client.transaction():

        key = client.key("Satellite", int(norad))
        sat = client.get(key)

        # Change time and tle_lines
        sat["tle1"] = tle_lines[0]
        sat["tle2"] = tle_lines[1]
        sat["tle3"] = tle_lines[2]
        sat["time"] = time_now

        client.put(sat)


