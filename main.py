from flask import Flask, render_template, request
#from satellite_tracker import get_satellite_location

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
            location = "This satellite is not yet implemented"
            return render_template("satellite_tracker.html", response = [user_satellite, location])

    return render_template("satellite_tracker.html")

if __name__ == "__main__":
    app.run(debug=True)