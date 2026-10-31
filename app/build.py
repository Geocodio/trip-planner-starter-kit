#!/usr/bin/env python3
"""Builds the trip app: trip/trip.json -> site/ (static files, no server code).

Run from anywhere: python3 app/build.py
Pages: index.html (Today), bookings.html, checklist.html. Drive times come from
the "driveTimes" object that tools/drive_times.py writes into trip.json.
"""
import datetime
import hashlib
import html
import json
import shutil
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP, SITE, AUDIO = ROOT / "app", ROOT / "site", ROOT / "app" / "audio"
TRIP = json.loads((ROOT / "trip" / "trip.json").read_text())
PLACES, DRIVE_TIMES = TRIP["places"], TRIP.get("driveTimes", {})
STATIC_FILES = ["app.css", "app.js", "manifest.webmanifest", "icon.svg"]

TABS = [("index.html", "Today", "M3 11l9-8 9 8v10h-6v-6H9v6H3z"),
        ("bookings.html", "Bookings", "M3 9a2 2 0 0 0 2-2V5h14v2a2 2 0 0 0 0 4v2a2 2 0 0 0 0 4v2H5v-2a2 2 0 0 0-2-2zM13 5v14"),
        ("checklist.html", "Check list", "M5 12l4 4 10-10")]


def esc(text):
    return html.escape(str(text), quote=True)


def format_date(iso, pattern="{weekday} {day} {month}"):
    date = datetime.date.fromisoformat(iso)
    return pattern.format(weekday=date.strftime("%a"), day=date.day, month=date.strftime("%b"))


def maps_search_url(place_key):
    return "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(PLACES[place_key]["address"])


def maps_route_url(place_keys):
    """One Google Maps directions link through every stop, using street addresses."""
    address = lambda key: urllib.parse.quote(PLACES[key]["address"])
    link = f"https://www.google.com/maps/dir/?api=1&travelmode=driving&origin={address(place_keys[0])}&destination={address(place_keys[-1])}"
    middle = "%7C".join(address(key) for key in place_keys[1:-1])
    return link + (f"&waypoints={middle}" if middle else "")


def format_minutes(minutes):
    hours, rest = divmod(minutes, 60)
    return f"{hours} h {rest:02d} min" if hours else f"{rest} min"


def render_plan_item(item, bookings_by_id):
    place = PLACES.get(item.get("place"))
    links = []
    if place:
        links.append(f'<a href="{esc(maps_search_url(item["place"]))}">{esc(place["name"])} (map)</a>')
    if item.get("booking") in bookings_by_id:
        links.append(f'<a href="bookings.html#{esc(item["booking"])}">Booking</a>')
    story = f'<p class="story">{esc(item["story"])}</p>' if item.get("story") else ""
    return (f'<li><time>{esc(item["time"])}</time><div><h4>{esc(item["title"])}</h4>'
            f'<p class="what"><b>What it actually is</b> {esc(item["what"])}</p>{story}'
            f'<p class="links">{" ".join(links)}</p></div></li>')


def render_drive(drive):
    stops = [stop["place"] for stop in drive["stops"]]
    legs = [DRIVE_TIMES.get(f"{origin}>{destination}") for origin, destination in zip(stops, stops[1:])]
    measured = all(legs)
    total_km = f'{sum(leg["km"] for leg in legs):.0f} km' if measured else "?"
    total_time = format_minutes(sum(leg["minutes"] for leg in legs)) if measured else "?"
    rows = []
    for position, stop in enumerate(drive["stops"]):
        if position:
            leg = legs[position - 1]
            rows.append(f'<li class="leg">{leg["km"]} km, {format_minutes(leg["minutes"])}</li>' if leg
                        else '<li class="leg">run tools/drive_times.py</li>')
        note = f'<p>{esc(stop["note"])}</p>' if stop.get("note") else ""
        rows.append(f'<li class="stop"><span class="dot">{chr(65 + position)}</span><h4>{esc(PLACES[stop["place"]]["name"])}</h4>{note}</li>')
    episode = drive.get("episode")
    listen = ""
    if episode and (AUDIO / f'{episode["file"]}.mp3').exists():
        listen = (f'<div class="listen"><h4>Listen on the way</h4><p>{esc(episode["about"])}</p>'
                  f'<audio controls preload="none" src="audio/{esc(episode["file"])}.mp3"></audio></div>')
    return (f'<section class="drive"><h3>{esc(drive["title"])}</h3><p>{esc(drive["intro"])}</p>'
            f'<div class="facts"><div><b>{total_km}</b><small>distance</small></div><div><b>{total_time}</b><small>driving</small></div></div>'
            f'<a class="go" href="{esc(maps_route_url(stops))}">Open in Google Maps</a>{listen}'
            f'<ol class="stops">{"".join(rows)}</ol></section>')


def render_day(day, bookings_by_id):
    items = "".join(render_plan_item(item, bookings_by_id) for item in day["items"])
    drive = render_drive(day["drive"]) if day.get("drive") else ""
    return (f'<section class="day" data-date="{day["date"]}" hidden><p class="eyebrow">{format_date(day["date"])}</p>'
            f'<h2>{esc(day["title"])}</h2><p class="summary">{esc(day["summary"])}</p><ol class="plan">{items}</ol>{drive}</section>')


def render_bookings():
    cards = []
    for booking in TRIP["bookings"]:
        place = PLACES.get(booking.get("place"))
        where = f'<a href="{esc(maps_search_url(booking["place"]))}">{esc(place["name"])}</a><br>{esc(place["address"])}' if place else ""
        cards.append(f'<article class="card" id="{esc(booking["id"])}"><h3>{esc(booking["title"])}</h3>'
                     f'<p class="meta">{format_date(booking["date"])}, {esc(booking["time"])}</p><p>{where}</p>'
                     f'<p class="ref">Reference <code>{esc(booking["reference"])}</code></p><p>{esc(booking.get("notes", ""))}</p></article>')
    return "".join(cards)


def render_checklist():
    rows = []
    for entry in TRIP["checklist"]:
        link = f' <a href="{esc(entry["url"])}">Open the official page</a>' if entry.get("url") else ""
        rows.append(f'<li class="card check"><label><input type="checkbox" data-id="{esc(entry["id"])}"><span>'
                    f'<b>{esc(entry["title"])}</b><small>{esc(entry["when"])}</small>'
                    f'<em>{esc(entry.get("notes", ""))}{link}</em></span></label></li>')
    return f'<p class="note" id="progress"></p><ul class="checks">{"".join(rows)}</ul>'


def render_page(file_name, heading, body, extra=""):
    tabs = "".join(f'<a href="{href}"{" class=on" if href == file_name else ""}><svg viewBox="0 0 24 24" class="ic"><path d="{icon}"/></svg>{label}</a>'
                   for href, label, icon in TABS)
    days = TRIP["days"]
    chips = ('<nav class="chips">' + "".join(f'<button data-date="{day["date"]}">{format_date(day["date"], "{weekday} {day}")}</button>' for day in days) + "</nav>"
             if file_name == "index.html" else "")
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            f'<title>{esc(heading)} | {esc(TRIP["title"])}</title><link rel="manifest" href="manifest.webmanifest"><link rel="icon" href="icon.svg">'
            f'<meta name="theme-color" content="#0f1a18"><meta name="apple-mobile-web-app-capable" content="yes"><link rel="apple-touch-icon" href="icon.svg">'
            f'<link rel="stylesheet" href="app.css"></head><body data-timezone="{esc(TRIP["timezone"])}">'
            f'<header><p class="eyebrow">{esc(TRIP["title"])}</p><h1>{esc(heading)}</h1>{chips}</header><main>{body}</main>'
            f'<nav class="tabs">{tabs}</nav><script src="app.js"></script></body></html>')


def main():
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    bookings_by_id = {booking["id"]: booking for booking in TRIP["bookings"]}
    pages = {
        "index.html": render_page("index.html", "Today", "".join(render_day(day, bookings_by_id) for day in TRIP["days"])),
        "bookings.html": render_page("bookings.html", "Bookings", render_bookings()),
        "checklist.html": render_page("checklist.html", "Book and check", render_checklist()),
    }
    for name, content in pages.items():
        (SITE / name).write_text(content)
    for name in STATIC_FILES:
        shutil.copy(APP / name, SITE / name)
    if AUDIO.exists():
        shutil.copytree(AUDIO, SITE / "audio")

    # The service worker precaches every file listed here; a changed file changes the version, which replaces the cache.
    files = sorted(str(path.relative_to(SITE)) for path in SITE.rglob("*") if path.is_file())
    digest = hashlib.sha256(b"".join((SITE / name).read_bytes() for name in files)).hexdigest()[:10]
    worker = (APP / "sw.js").read_text().replace("__VERSION__", digest).replace("__FILES__", json.dumps(["./"] + files))
    (SITE / "sw.js").write_text(worker)
    print(f"built site/ with {len(files) + 1} files, version {digest}")


if __name__ == "__main__":
    main()
