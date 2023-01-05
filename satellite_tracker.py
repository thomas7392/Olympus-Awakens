# General imports
from urllib.request import urlopen
import numpy as np

# Time imports
import datetime
import pytz

# Astrodynamics imports
from skyfield.api import load, EarthSatellite


SATELLITE_TO_NORAD = dict(icesat2 = 43613,
                          iss = 25544,
                          hubble = 20580)


def query_tle(satellite, IS_NORAD = False):
    '''
    Request the tle from a specific satellite from celestrek.org
    '''

    # IF satellite is given, get its norad
    if not IS_NORAD:
        NORAD_ID = SATELLITE_TO_NORAD[satellite]
    else:
        NORAD_ID = satellite

    # Download TLE of last known position
    URL = f'https://celestrak.org/NORAD/elements/gp.php?CATNR={NORAD_ID}FORMAT=TLE'
    TLE_string = urlopen(URL).read().decode('utf-8')
    TLE_lines = TLE_string.strip().splitlines()

    return TLE_lines

def get_ground_track(satellite, IS_NORAD = False):

    '''
    Return an ephemeris of requested satellite in lat/lon for a ground track
    '''

    # Get tle lines
    TLE_lines = query_tle(satellite, IS_NORAD = IS_NORAD)

    # Catch false NORADS
    if TLE_lines[0] == 'No GP data found':
        return False
    elif len(TLE_lines) != 3:
        return False

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