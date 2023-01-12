from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_googlemaps import GoogleMaps, Map
import os.path
import os

from satellite_tracker import get_ground_track, get_current_satellite_position
from utils import get_secret

# When developing locally, get local key
if os.path.exists("api_secrets.py"):
    from api_secrets import MAPS_DEV_API_KEY as maps_api_key
else:
    maps_api_key = get_secret("production_maps_api_key")

# Google maps javascript api key
app = Flask(__name__)

GoogleMaps(app, key=maps_api_key)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/'),
        'favicon.ico')

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/update_satellite_position", methods = ['POST', 'GET'])
def update_satellite_position():

    #global TLE_lines
    if request.method == "POST":
        tle1=request.values.get('tle1')
        tle2=request.values.get('tle2')
        tle3=request.values.get('tle3')
        TLE_lines = [tle1, tle2, tle3]

        latitude, longitude = get_current_satellite_position(TLE_lines)

        return jsonify({"latitude": latitude, "longitude": longitude})

    return None

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
            if user_satellite_norad.isdigit() and len(user_satellite_norad) == 5:
                sat_data = get_ground_track(user_satellite_norad, IS_NORAD = True)
            else:
                return render_template("satellite_tracker.html", no_norad = True)

            # Check if NORAD ID was found
            if sat_data is None:
                return render_template("satellite_tracker.html", no_sat = True)

        ground_track = [coord for coord in zip(sat_data['sat_lat'], sat_data['sat_lon'])]

        # Create map
        mymap = Map(identifier="view-side",
                    lat=0,
                    lng=0,
                    zoom = 2,
                    streetview_control=False,
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