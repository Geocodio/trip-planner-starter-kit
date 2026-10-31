#!/usr/bin/env python3
"""Fills in coordinates and drive times for trip/trip.json with the Geocodio API.

Geocodio geocodes street addresses, not venue names. Every place in trip.json
therefore stores a street address (plus the country, which selects the right
dataset); a name like "Hobbiton Movie Set" on its own would not resolve.

What it does:
  1. Geocodes each place that has no "ll" (latitude, longitude) yet and stores it on the place.
  2. Reads every day's drive.stops, takes each pair of consecutive stops as a leg,
     asks the Geocodio distance API (mode=driving) for minutes and kilometres,
     and stores them in the top-level "driveTimes" object as "from>to".

Legs that are already measured are skipped, so reruns cost nothing. Use --refresh
to measure everything again and --dry-run to list the requests without sending them.

Usage: GEOCODIO_API_KEY=... python3 tools/drive_times.py [--dry-run] [--refresh]
"""
import argparse
import json
import math
import os
import sys
import urllib.parse
import urllib.request

TRIP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "trip", "trip.json")
GEOCODIO = "https://api.geocod.io/v2"


def call_geocodio(path, params):
    query = urllib.parse.urlencode({**params, "api_key": os.environ["GEOCODIO_API_KEY"]}, doseq=True)
    with urllib.request.urlopen(f"{GEOCODIO}/{path}?{query}", timeout=30) as response:
        return json.load(response)


def geocode(address):
    result = call_geocodio("geocode", {"q": address, "limit": 1})["results"][0]
    if result["accuracy_type"] in ("place", "county", "state"):
        raise ValueError(f"{address!r} only matched a {result['accuracy_type']}; check the street address")
    return [result["location"]["lat"], result["location"]["lng"]]


def measure(origin, destination):
    """Whole minutes and kilometres (one decimal) for a driving leg between two [lat, lng] pairs."""
    leg = call_geocodio("distance", {
        "origin": f"{origin[0]},{origin[1]}",
        "destinations[]": f"{destination[0]},{destination[1]}",
        "mode": "driving",
    })["destinations"][0]
    return {"minutes": math.ceil(leg["duration_seconds"] / 60), "km": round(leg["distance_km"], 1)}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--dry-run", action="store_true", help="list what would be requested and change nothing")
    parser.add_argument("--refresh", action="store_true", help="measure again even when results are already stored")
    arguments = parser.parse_args()
    if not arguments.dry_run and not os.environ.get("GEOCODIO_API_KEY"):
        sys.exit("Set GEOCODIO_API_KEY (copy .env.example to .env and export it).")

    trip = json.load(open(TRIP_PATH))
    places = trip["places"]
    drive_times = trip.setdefault("driveTimes", {})

    for key, place in places.items():
        if place.get("ll") and not arguments.refresh:
            continue
        print(f"geocode {key}: {place['address']}")
        if not arguments.dry_run:
            place["ll"] = geocode(place["address"])

    for day in trip["days"]:
        stops = [stop["place"] for stop in day.get("drive", {}).get("stops", [])]
        for origin, destination in zip(stops, stops[1:]):
            key = f"{origin}>{destination}"
            if key in drive_times and not arguments.refresh:
                continue
            print(f"drive   {key}")
            if not arguments.dry_run:
                drive_times[key] = measure(places[origin]["ll"], places[destination]["ll"])
                print(f"        {drive_times[key]['minutes']} min, {drive_times[key]['km']} km")

    if not arguments.dry_run:
        with open(TRIP_PATH, "w") as file:
            json.dump(trip, file, indent=2, ensure_ascii=False)
            file.write("\n")


if __name__ == "__main__":
    main()
