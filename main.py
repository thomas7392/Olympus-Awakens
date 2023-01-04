from flask import Flask, render_template, request
from satellite_tracker import get_ground_track

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/satellite_tracker", methods = ['GET', 'POST'])
def satellite_tracker():

    # Dropdown menu with example satellites
    if request.method == 'POST':
        user_satellite = request.form.get("satellite", None)
        if user_satellite!=None:
            sat_data = get_ground_track(user_satellite)
            return render_template("satellite_tracker.html", **sat_data)

    # Dropdown menu with NORAD ID
    if request.method == 'POST':
        user_satellite = request.form.get("satellite_norad", None)
        if user_satellite != None:
            sat_data = get_ground_track(user_satellite, IS_NORAD = True)
            if sat_data == False:
                return render_template("satellite_tracker.html", no_sat = True)
            return render_template("satellite_tracker.html", **sat_data)

    return render_template("satellite_tracker.html")

if __name__ == "__main__":
    app.run(debug=True)