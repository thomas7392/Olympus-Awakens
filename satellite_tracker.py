# General imports
from urllib.request import urlopen
import numpy as np

# Time imports
import datetime
import pytz
import os

# Astrodynamics imports
from skyfield.api import load, EarthSatellite

# Querying imports
from get_tle_local import get_tle_local
from get_tle_sql import get_tle_sql

SATELLITE_TO_NORAD = dict(icesat2 = 43613,
                          iss = 25544,
                          hubble = 20580)


def get_tle(norad, method):

    if method == "sql":
        return get_tle_sql(norad)

    if method == "local":
        return get_tle_local(norad)


def get_ground_track(satellite, IS_NORAD = False):

    '''
    Return an ephemeris of requested satellite in lat/lon for a ground track
    '''

    # Possible convert to norad
    if IS_NORAD:
        norad = satellite
    else:
        norad = SATELLITE_TO_NORAD[satellite]

    # Choose if searchgin tle in local cache (dev) or in
    # the sql database (production)
    if os.path.exists("api_secrets.py"):
        get_tle_method = "local"
    else:
        get_tle_method = "sql"

    # TLE_lines = get_tle(norad, get_tle_method )
    TLE_lines = get_tle(norad, get_tle_method)

    if TLE_lines is None:
        return None

    satellite_norad = TLE_lines[1].split(" ")[1][:-1]
    satellite_name = TLE_lines[0]

    # Create skyfield satellite object and load skyfield times
    sat = EarthSatellite(TLE_lines[1], TLE_lines[2])
    ts = load.timescale(builtin=True)

    # Create 270 minutes ahead from now in steps of 1 minute
    base = datetime.datetime.now(pytz.utc)
    datetime_times = [base + datetime.timedelta(minutes=x) for x in range(0, 270)]
    times = ts.from_datetimes(datetime_times)

    # Get satellite ephemeris in lat/lon
    geocentric = sat.at(times)
    subsat = geocentric.subpoint()

    lon = subsat.longitude.degrees
    lat = subsat.latitude.degrees

    sat_data = dict(sat_name = satellite_name,
                    sat_norad = satellite_norad,
                    sat_lat = lat,
                    sat_lon = lon,
                    sat_tle_lines = TLE_lines,
                    sat_first_lat = np.round(lat[0], 4),
                    sat_first_lon = np.round(lon[0], 4)
                    )
    return sat_data

def get_current_satellite_position(TLE_lines):

    # Get time to calculate lat/lon
    sat = EarthSatellite(TLE_lines[1], TLE_lines[2])
    ts = load.timescale(builtin=True)
    base = datetime.datetime.now(pytz.utc)
    time = ts.from_datetime(base)

    # Calculate lat/lon
    geocentric = sat.at(time)
    subsat = geocentric.subpoint()
    lon = subsat.longitude.degrees
    lat = subsat.latitude.degrees

    return lat, lon