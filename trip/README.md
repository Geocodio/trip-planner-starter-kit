# trip.json schema

`trip.json` is the single source of truth. `app/build.py` renders it into the app in `site/`. `tools/drive_times.py` fills in the fields marked "tool".

```
{
  "title": "Display name of the trip",
  "timezone": "Pacific/Auckland",          // IANA zone of the destination; decides which day counts as "today"
  "places": { "<key>": Place, ... },
  "days": [ Day, ... ],                   // in date order
  "bookings": [ Booking, ... ],
  "checklist": [ ChecklistItem, ... ],
  "driveTimes": { "<from>><to>": {"minutes": 23, "km": 17.9} }   // tool: written by drive_times.py
}
```

## Place

```
{ "name": "Hobbiton Movie Set",
  "address": "501 Buckland Road, Hinuera, Matamata 3472, New Zealand",   // street address, with the country
  "ll": [-37.87, 175.68] }                                               // tool: latitude and longitude
```

Geocodio geocodes addresses, not venue names, so store the street address and include the country. A place that only matches a town or region (for example a trailhead with no street) is rejected by `drive_times.py`; use the address of the nearest car park or visitor centre.

## Day

```
{ "date": "2027-01-13",
  "title": "The scenic way to Rotorua",
  "summary": "One or two sentences.",
  "items": [ Item, ... ],
  "drive": Drive }                        // optional
```

## Item (one line of the day plan)

```
{ "time": "14:30",
  "title": "Skyline Rotorua gondola",
  "what": "Plain description of what you physically do there.",   // required: no history here
  "story": "Optional history or a fun fact.",
  "place": "skyline",                     // optional: key in places, adds a map link
  "booking": "rotorua-hotel" }            // optional: id in bookings, adds a link to the booking
```

## Drive

```
{ "title": "Auckland to Rotorua",
  "intro": "One or two sentences.",
  "stops": [ {"place": "aucklandHotel"}, {"place": "skyline", "note": "Where to park."}, {"place": "rotoruaHotel"} ],
  "episode": { "file": "example", "title": "The Road to Rotorua", "about": "Start it as you leave." } }   // optional
```

Each pair of consecutive stops is one leg; `drive_times.py` measures every leg. The "Listen on the way" player appears when `app/audio/<file>.mp3` exists (build it with `podcast/build.sh`).

## Booking

```
{ "id": "hobbiton-tour", "title": "Hobbiton Movie Set tour", "date": "2027-01-15",
  "time": "13:00 tour", "place": "hobbiton", "reference": "EXAMPLE-5504", "notes": "Anything to remember." }
```

## ChecklistItem

```
{ "id": "nzeta", "title": "NZeTA", "when": "At least 72 hours before departure",
  "notes": "What to do.", "url": "https://..." }     // url optional
```

Checkbox state is stored in each phone's localStorage under the item `id`, so keep ids stable.

The example hotels are placeholders at public street addresses. Replace each place with the street address of where you are really staying or going.
