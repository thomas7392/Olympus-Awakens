from flask import Flask, render_template, request, jsonify
from flask_googlemaps import GoogleMaps, Map
import time
import os.path

from satellite_tracker import get_ground_track, get_current_satellite_position

from google.cloud import datastore

def get_maps_api_key():

    client = datastore.Client()
    task_key = client.key("Task", 5644004762845184)
    task = client.get(task_key)

    return task['key']

maps_api_key = get_maps_api_key()

# Google maps javascript api key
app = Flask(__name__)

GoogleMaps(app, key=maps_api_key)


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/update-satellite-position")
def update_satellite_position():

    latitude, longitude = get_current_satellite_position(TLE_lines)
    return jsonify({"latitude": latitude, "longitude": longitude})

@app.route("/satellite_tracker", methods = ['GET', 'POST'])
def satellite_tracker():

    # Dropdown menu with example satellites
    if request.method == 'POST':

        # Get satellite from dropdown or open norad field
        user_satellite = request.form.get("satellite", None)
        user_satellite_norad = request.form.get("satellite_norad", None)

        # Get ground track if satellite is from examples
        if user_satellite!=None:

            # Get ground track in lat/lon
            sat_data = get_ground_track(user_satellite)

        # Get ground track if satellite is from NORAD
        if user_satellite_norad!=None:

            # Request satellite from norad field
            sat_data = get_ground_track(user_satellite_norad, IS_NORAD = True)
            # Check if NORAD ID was found
            if sat_data == False:
                return render_template("satellite_tracker.html", no_sat = True)

        ground_track = [coord for coord in zip(sat_data['sat_lat'], sat_data['sat_lon'])]

        # Save the TLE_lines globally, to calculate future positions dynamically without additional query
        global TLE_lines
        TLE_lines = sat_data['sat_tle_lines']

        # Create map
        mymap = Map(identifier="view-side",
                    lat=0,
                    lng=0,
                    zoom = 2,
                    style = "width:100%; height:100%;",
                    markers=[{'icon': 'static/images/satellite_icon.png',
                            'lat': sat_data['sat_lat'][0],
                            'lng':  sat_data['sat_lon'][0]
                                }],
                    polylines=[ground_track]
                    )

        return render_template("satellite_tracker.html", mymap = mymap, **sat_data)

    return render_template("satellite_tracker.html")

if __name__ == "__main__":
    app.run(debug=True)