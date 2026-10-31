# 05 Day plans

Use once the ideas are voted and the fixed points are known. This is the step where the geography matters.

```
Build the day-by-day plan in trip.json from the voted ideas and the fixed points. Rules:
- Fit activities around the fixed points (flights, tickets, check-in times). Work backwards from timed items and leave 30 minutes of slack.
- Light arrival days: after a long flight the first day has at most one easy outing and an early night.
- Every item has a "what" line (what we physically do there) before any "story".
- Every place gets a street address, with the country.
- Add a drive for each day we move between places, listing the stops in order.

Then run python3 tools/drive_times.py so the drive times come from Geocodio, check each day's total against the family's energy rules, and move things if a day is too long. Rebuild with python3 app/build.py and summarise each day in two lines.
```
