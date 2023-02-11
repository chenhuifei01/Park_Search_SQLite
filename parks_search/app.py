import re
import sys
import random
from flask import Flask, request, render_template
from . import search

app = Flask(__name__)


def get_parameters(args):
    errors = []
    # get parameters from query string
    search_params = {}
    name = request.args.get("name")
    query_terms = request.args.get("query_terms")
    zip_code = request.args.get("zip_code")
    day = request.args.get("day")
    hour = request.args.get("time_hour")
    minute = request.args.get("time_min")
    am_pm = request.args.get("time_ampm")

    lat = request.args.get("lat")
    lon = request.args.get("lon")
    dist = request.args.get("distance")

    # validate parameters
    if name:
        search_params["name"] = name
    if query_terms:
        search_params["query_terms"] = query_terms.split()
    if zip_code:
        if re.match(r"\d{5}", zip_code):
            search_params["zip_code"] = zip_code
        else:
            errors.append("Invalid zip code parameter")
    if day or hour:
        hour = int(hour)
        if day not in ("mon", "tue", "wed", "thu", "fri", "sat", "sun"):
            errors.append("Invalid day parameter")
        if hour not in range(1, 13):
            errors.append("Invalid hour parameter")
        if minute not in ("00", "15", "30", "45"):
            errors.append("Invalid minute parameter")
        if am_pm not in ("am", "pm"):
            errors.append("Invalid am/pm parameter")
        if not errors:
            if hour == 12:
                hour = 0
            if am_pm == "pm":
                hour += 12
            search_params["open_at"] = (day, f"{hour:02d}{minute}")
    if lat or lon or dist:
        try:
            lat = float(lat)
            lon = float(lon)
            dist = float(dist)
            search_params["near"] = (lat, lon, dist)
        except ValueError:
            errors.append("Invalid lat/lon/distance parameters")

    return search_params, errors


@app.route("/")
def index():
    search_params, errors = get_parameters(request.args)

    if errors:
        return render_template("index.html", errors=errors, args=request.args)
    elif search_params:
        parks = search.search_parks(search_params)
        return render_template(
            "index.html", parks=parks, search_params=search_params, args=request.args
        )
    else:
        return render_template("index.html", args={})


if __name__ == "__main__":
    port = random.randint(5000, 10000)
    app.run(host="0.0.0.0", port=port)