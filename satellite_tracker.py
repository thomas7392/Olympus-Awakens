# General imports
from urllib.request import urlopen
import numpy as np

# Time imports
import datetime
import pytz
import os

# Astrodynamics imports
from skyfield.api import load, EarthSatellite, wgs84
from skyfield.elementslib import osculating_elements_of

# Querying imports
from get_tle_local import get_tle_local
from get_tle_firestore import get_tle_firestore

SATELLITE_TO_NORAD = dict(icesat2 = 43613,
                          iss = 25544,
                          hubble = 20580,
                          SENTINEL_1A = 39634,
                          SENTINEL_1B = 41456,
                          SENTINEL_2A = 40697,
                          SENTINEL_2B = 42063,
                          SENTINEL_3A = 41335,
                          SENTINEL_3B = 43437,
                          SENTINEL_5P = 42969,
                          SENTINEL_6 = 46984)

MU_EARTH = 3.986004418e14

def get_tle(norad, method):

    if method == "local":
        return get_tle_firestore(norad)

    if method == "firestore":
        return get_tle_firestore(norad)


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
        get_tle_method = "firestore"

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
    heights = wgs84.height_of(geocentric).km
    elements = osculating_elements_of(geocentric)

    sat_data = dict(sat_name = satellite_name,
                    sat_norad = satellite_norad,
                    sat_lat = lat,
                    sat_lon = lon,
                    sat_tle_lines = TLE_lines,
                    tle1 = TLE_lines[0],
                    tle2 = TLE_lines[1],
                    tle3 = TLE_lines[2],
                    )

    return sat_data

def get_current_satellite_position(TLE_lines):

    # Get time to calculate lat/lon
    sat = EarthSatellite(TLE_lines[1], TLE_lines[2])
    ts = load.timescale(builtin=True)
    base = datetime.datetime.now(pytz.utc)
    time = ts.from_datetime(base)

    # Calculate info at current time
    geocentric = sat.at(time)
    subsat = geocentric.subpoint()
    elements = osculating_elements_of(geocentric)
    tle_date = sat.epoch.utc_jpl()[5:]

    # Store relevant info in a json
    sat_data = dict(
        longitude = subsat.longitude.degrees,
        latitude = subsat.latitude.degrees,
        tle_date = tle_date,
        altitude = wgs84.height_of(geocentric).km,
        a = elements.semi_major_axis.km,
        e = elements.eccentricity,
        i = elements.inclination.degrees,
        raan = elements.longitude_of_periapsis.degrees,
        aop = elements.argument_of_periapsis.degrees,
        ta = elements.true_anomaly.degrees,
        speed = vis_viva(trajectory_equation(elements.semi_major_axis.m,
                                            elements.eccentricity,
                                            elements.true_anomaly.radians), elements.semi_major_axis.m)/1e3
    )

    return sat_data

def trajectory_equation(a, e, theta):
    r = (a * (1 - e**2))/(1 + e * np.cos(theta))
    return r

def vis_viva(r, a):
    v = np.sqrt(MU_EARTH * (2/r - 1/a))
    return v