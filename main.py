from flask import Flask, render_template, request
from flask_googlemaps import GoogleMaps, Map
import time

from satellite_tracker import get_ground_track

# Google maps javascript api key
app = Flask(__name__)

# Configure google maps API
GoogleMaps(app, key="AIzaSyBihjb3EO5c1KkuDDMSWXXjLfCri30FRHc")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/satellite_tracker", methods = ['GET', 'POST'])
def satellite_tracker():

    # Dropdown menu with example satellites
    if request.method == 'POST':

        # Request satellite from dropdown
        user_satellite = request.form.get("satellite", None)
        if user_satellite!=None:

            # Get ground track in lat/lon
            sat_data = get_ground_track(user_satellite)
            ground_track = [coord for coord in zip(sat_data['sat_lat'], sat_data['sat_lon'])]

            # Create map
            mymap = Map(identifier="view-side",
                        lat=0,
                        lng=0,
                        zoom = 2,
                        style = "width:900px; height:450px;",
                        markers=[{'icon': 'static/images/satellite_icon.png',
                                'lat': sat_data['sat_lat'][0],
                                'lng':  sat_data['sat_lon'][0]
                                    }],
                        polylines=[ground_track]
                        )

            return render_template("satellite_tracker.html", mymap = mymap, **sat_data)

    # Field with NORAD ID
    if request.method == 'POST':

        # Request satellite from norad field
        user_satellite = request.form.get("satellite_norad", None)
        if user_satellite != None:

            # Get ground track in lat/lon
            sat_data = get_ground_track(user_satellite, IS_NORAD = True)


            if sat_data == False:
                return render_template("satellite_tracker.html", no_sat = True)
            else:

                # # Create map
                # mymap = Map(identifier="view-side",
                #         lat=0,
                #         lng=0,
                #         markers=[(sat_data['sat_lat'][0], sat_data['sat_lon'][0])])
                return render_template("satellite_tracker.html" **sat_data)

    return render_template("satellite_tracker.html")

if __name__ == "__main__":
    app.run(debug=True)