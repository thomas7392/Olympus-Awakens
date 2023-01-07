from urllib.request import urlopen
import datetime
import json
from os import makedirs, path
import pytz

TLE_CACHE_PATH = ".cache/tle.json"
MAX_TLE_CACHE_TIME = 6 * 60 # Minutes
CACHE_PATH = ".cache/"

def get_tle(norad):
    '''
    This function searches the cache for a tle and if not present
    or if experied (after x hours), queries a new one. This shoud
    result in querying celestrak to a minimum.
    '''

    # initialize not removing the key
    remove = False

    # Check if cache exists
    if not path.exists(CACHE_PATH):
        print("Hello, world")
        makedirs(CACHE_PATH)

    # Check if there is a tle.json
    if not path.exists(TLE_CACHE_PATH):
        create_empty_json()

    # Open en search for the satellite
    with open(TLE_CACHE_PATH) as json_file:
        TLE_json = json.load(json_file)

        if str(norad) in TLE_json.keys():

            # Check if still up to date
            if not is_expired(TLE_json, norad):

                # if valid, return the tle
                return TLE_json[str(norad)]["tle"]

    # query new tle and save it (overriding potentially exisiting tle of this satellite)
    TLE_lines = query_tle(norad)
    add_satellite(norad, TLE_lines)
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

def create_empty_json():
    '''
    Created an empty json
    '''

    #Create empty json
    empty_json = dict()
    with open(TLE_CACHE_PATH, "w") as file:
        json.dump(empty_json, file)
    return True

def add_satellite(norad, TLE_lines):
    '''
    Adds a satellite's tle to the existing tle json cached storage
    '''

    # Open and read the json
    with open(TLE_CACHE_PATH) as json_file:
        json_decoded = json.load(json_file)

    time_now = datetime.datetime.utcnow()
    satellite = {"year": time_now.year,
       "month": time_now.month,
       "day": time_now.day,
       "hour": time_now.hour,
       "minute": time_now.minute,
        "second": time_now.second,
       "tle": TLE_lines}

    json_decoded[str(norad)] = satellite

    with open(TLE_CACHE_PATH, "w") as json_file:
        json_file.write(json.dumps(json_decoded))

    return True

def remove_satellite(norad):
    '''
    Removes a satallite from the json cache
    '''

    # Open and read the json
    with open(TLE_CACHE_PATH) as json_file:
        json_decoded = json.load(json_file)

    del json_decoded[str(norad)]

    with open(TLE_CACHE_PATH, "w") as json_file:
        json_file.write(json.dumps(json_decoded))

    return True

def is_expired(TLE_json, norad):
    '''
    Checks if an entry in the json cache is experid based on stored
    time and current time
    '''
    # Get now time and time of tle creation in json
    time_now = datetime.datetime.utcnow()
    time_tle = datetime.datetime(TLE_json[str(norad)]["year"],
                                 TLE_json[str(norad)]["month"],
                                 TLE_json[str(norad)]["day"],
                                 hour = TLE_json[str(norad)]["hour"],
                                 minute = TLE_json[str(norad)]["minute"],
                                second = TLE_json[str(norad)]["second"])

    # If TLE not young enough, update
    if (time_now - time_tle).total_seconds() / 60.0 > MAX_TLE_CACHE_TIME:
        print("I found an expired one")
        return True

    return False




