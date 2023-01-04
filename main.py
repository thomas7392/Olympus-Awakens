from flask import Flask, render_template, request
from flask_googlemaps import GoogleMaps, Map, icons

from satellite_tracker import get_ground_track

# Google maps javascript api key
app = Flask(__name__)

# Configure google maps API
GoogleMaps(app)


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/map")
def map():
    mymap = Map(
        identifier="gmap",
        varname="gmap",
        lat=37.4419,
        lng=-122.1419,
        markers={
            icons.dots.green: [(37.4419, -122.1419), (37.4500, -122.1350)],
            icons.dots.blue: [(37.4300, -122.1400, "Hello World")],
        },
        style="height:400px;width:600px;margin:0;",
    )

    return render_template("map.html", mymap = mymap)

@app.route("/satellite_tracker", methods = ['GET', 'POST'])
def satellite_tracker():

    # Dropdown menu with example satellites
    if request.method == 'POST':

        # Request satellite from dropdown
        user_satellite = request.form.get("satellite", None)
        if user_satellite!=None:

            # Get ground track in lat/lon
            sat_data = get_ground_track(user_satellite)

            # Create map
            mymap = Map(identifier="view-side",
                        lat=0,
                        lng=0,
                        markers=[(sat_data['sat_lat'][0], sat_data['sat_lon'][0])])
            return render_template("satellite_tracker.html", mymap=mymap, **sat_data)

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

                # Create map
                mymap = Map(identifier="view-side",
                        lat=0,
                        lng=0,
                        markers=[(sat_data['sat_lat'][0], sat_data['sat_lon'][0])])
                return render_template("satellite_tracker.html", mymap=mymap, **sat_data)

    return render_template("satellite_tracker.html")

if __name__ == "__main__":
    app.run(debug=True)