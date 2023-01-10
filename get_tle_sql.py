# General imports
from urllib.request import urlopen
import datetime

# Google imports
from google.cloud.sql.connector import Connector, IPTypes

# Sql imports
import sqlalchemy
import pymysql

# Local imports
from utils import get_secret

MAX_TLE_CACHE_TIME = 6 * 60 # Minutes

def get_tle_sql(norad):
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

def is_expired(sat_data):
    '''
    Checks if an entry in the json cache is experid based on stored
    time and current time
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


def connect_with_connector(database) -> sqlalchemy.engine.base.Engine:
    """
    Initializes a connection pool for a Cloud SQL instance of MySQL.
    Uses the Cloud SQL Python Connector package.
    """

    instance_connection_name =  "olympus-awakens:europe-west4:thomasgoldman-website"
    db_user = "root"
    db_pass = get_secret("sql-password")
    db_name = database

    ip_type = IPTypes.PUBLIC

    connector = Connector(ip_type)

    def getconn() -> pymysql.connections.Connection:
        conn: pymysql.connections.Connection = connector.connect(
            instance_connection_name,
            "pymysql",
            user=db_user,
            password=db_pass,
            db=db_name,
        )
        return conn

    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
    )
    return connector, pool

def add_satellite(norad, tle_lines):

    # Connect with sql
    connector, pool = connect_with_connector("satellite-tracker")
    with pool.connect() as db_conn:

        # # create ratings table in our movies database
        # db_conn.execute(
        #   "CREATE TABLE IF NOT EXISTS tle "
        #   "( id SERIAL NOT NULL, "
        #   "norad INT NOT NULL, "
        #   "tle1 VARCHAR(255) NOT NULL, "
        #   "tle2 VARCHAR(255) NOT NULL, "
        #   "tle3 VARCHAR(255) NOT NULL, "
        #   "year INT NOT NULL, "
        #   "month INT NOT NULL, "
        #   "day INT NOT NULL, "
        #   "hour INT NOT NULL, "
        #   "minute INT NOT NULL, "
        #   "second INT NOT NULL, "
        #   "PRIMARY KEY (id));"
        # )

        # insert data into our ratings table
        insert_satellite = sqlalchemy.text(
          "INSERT INTO tle (norad, tle1, tle2, tle3, year, month, day, hour, minute, second)\
          VALUES (:norad, :tle1, :tle2, :tle3, :year, :month, :day, :hour, :minute, :second)",
        )

        time_now = datetime.datetime.utcnow()

        # insert entries into table
        db_conn.execute(insert_satellite,
                        norad=norad,
                        tle1=tle_lines[0],
                        tle2=tle_lines[1],
                        tle3=tle_lines[2],
                        year=time_now.year,
                        month=time_now.month,
                        day=time_now.day,
                        hour=time_now.hour,
                        minute=time_now.minute,
                        second=time_now.second)

    # Close connection
    connector.close()

def update_satellite(norad, tle_lines):
    '''
    Update an existing satellite in the sql database
    '''

    # Connect to sql
    connector, pool = connect_with_connector("satellite-tracker")

    with pool.connect() as db_conn:
        time_now = datetime.datetime.utcnow()
        db_conn.execute(
            f"UPDATE tle\
            SET norad={norad},\
            tle1='{tle_lines[0]}',\
            tle2='{tle_lines[1]}',\
            tle3='{tle_lines[2]}',\
            year={time_now.year},\
            month={time_now.month},\
            day={time_now.day},\
            hour={time_now.hour},\
            minute={time_now.minute},\
            second={time_now.second}\
            WHERE norad = {norad};")


    connector.close()



def print_sql_table(database, table):
    '''
    Prints the full content of the satellite tle database
    '''

    # Connect to sql
    connector, pool = connect_with_connector(database)

    with pool.connect() as db_conn:

        # query and fetch ratings table
        results = db_conn.execute(f"SELECT * FROM {table}").fetchall()

        # show results
        for row in results:
            print(row)

    connector.close()


def remove_satellite(norad):
    '''
    Remove a satellite by norad from the sql database
    '''
    # Connect to sql
    connector, pool = connect_with_connector("satellite-tracker")

    with pool.connect() as db_conn:
        db_conn.execute(f"DELETE FROM tle WHERE norad={norad};")

    connector.close()

def get_satellite(norad):
    '''
    query a satellite by norad id from the sql database
    '''

    # Connect to sql
    connector, pool = connect_with_connector("satellite-tracker")
    with pool.connect() as db_conn:

        # Query based on norad
        satellite = db_conn.execute(f"SELECT * FROM tle WHERE norad={norad};").fetchall()

    connector.close()

    # Check if satellite exists
    if len(satellite) == 0:
        return None

    # Convert sql row to python dict manually because nothing works...
    sat_data = {"norad": satellite[0]["norad"],
            "tle_lines": [satellite[0]["tle1"], satellite[0]["tle2"], satellite[0]["tle3"]],
            "year": satellite[0]["year"],
            "month": satellite[0]["month"],
            "day": satellite[0]["day"],
            "hour": satellite[0]["hour"],
            "minute": satellite[0]["minute"],
            "second": satellite[0]["second"]}

    return sat_data

def clean_table(database, table):
    '''
    Remove all rows in the table but keep table structure intact
    '''
    # Connect to sql
    connector, pool = connect_with_connector(database)
    with pool.connect() as db_conn:
        db_conn.execute(f"DELETE FROM {table};")
    connector.close()







