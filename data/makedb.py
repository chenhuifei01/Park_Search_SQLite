import json
import sqlite3
import pathlib
import requests


def schema():
    return """
    CREATE TABLE parks (
        id INTEGER PRIMARY KEY,
        name TEXT,
        address TEXT,
        history TEXT,
        description TEXT,
        url TEXT,
        tokens TEXT,
        latitude REAL,
        longitude REAL
    );
    CREATE TABLE park_times (
        id INTEGER PRIMARY KEY,
        park_id INTEGER,
        day TEXT,
        open_time TEXT,
        close_time TEXT,
        FOREIGN KEY(park_id) REFERENCES parks(id)
    );
    """


def geocode_address(address):
    # geocode using census geocoder
    resp = requests.get(
        f"https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address={address}&benchmark=2020&format=json"
    )
    data = resp.json()
    if data["result"]["addressMatches"]:
        return data["result"]["addressMatches"][0]["coordinates"]
    else:
        print(data)
        # some data does not geocode properly, so just return 0, 0
        return {"x": 0, "y": 0}


def generate_times(id):
    times = {}
    for day in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]:
        # 9-5
        times[day] = {
            "open": "0900",
            "close": "1700",
        }
        if id % 3 == 0:
            # 8-6
            times[day]["open"] = "0800"
            times[day]["close"] = "1800"
        if id % 11 == 0:
            # 5-11
            times[day]["open"] = "0500"
            times[day]["close"] = "2300"
        if id % 17 == 0:
            # 24 hours
            times[day]["open"] = "0000"
            times[day]["close"] = "2400"
        if day in ("sat", "sun") and id % 7 == 0:
            # 24 hours on weekend
            times[day]["open"] = "0000"
            times[day]["close"] = "2400"
        if day == "wed" and id % 5:
            # closed on wednesday
            times[day]["open"] = "0000"
            times[day]["close"] = "0000"

    return times


def makedb():
    path = pathlib.Path("data/parks.db")
    path.unlink()
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.executescript(schema())

    with open("data/normalized_parks.json") as f:
        parks = json.load(f)
        for id_, park in enumerate(parks):
            lon, lat = geocode_address(park["address"]).values()
            c.execute(
                "INSERT INTO parks (name, address, history, description, url, tokens, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    park["name"],
                    park["address"],
                    park["history"],
                    park["description"],
                    park["url"],
                    " ".join(park["tokens"]),
                    lat,
                    lon,
                ),
            )

            for day, times in generate_times(id_).items():
                c.execute(
                    "INSERT INTO park_times (park_id, day, open_time, close_time) VALUES (?, ?, ?, ?)",
                    (id_, day, times["open"], times["close"]),
                )
            c.execute("COMMIT")
    c.close()


if __name__ == "__main__":
    makedb()