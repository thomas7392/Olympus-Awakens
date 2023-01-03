from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/chess")
def chess():
    return render_template("chess.html")

if __name__ == "__main__":
    app.run(debug=True)