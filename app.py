from flask import Flask, request, render_template, Response
import requests
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
app = Flask(__name__)
search_requests_total = Counter(
    'search_requests_total', 'Total number of requests to /search')

# Create a Histogram to measure the duration of /search method calls
search_duration_seconds = Histogram(
    'search_duration_seconds', 'Duration of /search method calls')


@app.route("/")
def home():

    return render_template("home.html")


def measure_search_duration(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        search_duration_seconds.observe(duration)
        return result
    return wrapper


@app.route("/search", methods=["POST"])
@measure_search_duration
def search():
    search_requests_total.inc()

    query = request.form["q"]

    location = requests.get(
        "https://nominatim.openstreetmap.org/search",
        {"q": query, "format": "json", "limit": "1"},
    ).json()

    if location:
        coordinate = [location[0]["lat"], location[0]["lon"]]

        time = requests.get(
            "https://timeapi.io/api/Time/current/coordinate",
            {"latitude": coordinate[0], "longitude": coordinate[1]},
        )

        return render_template("success.html", location=location[0], time=time.json())

    else:
        return render_template("fail.html")


@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
