# Trip planner: working rules for Claude

This repo plans one family trip and turns the plan into a private offline app and podcast episodes. Follow these rules in every session.

## Source of truth

- `trip/trip.json` is the single source of truth. The app (`site/`) and the audio are generated from it. Never edit `site/` by hand, and never keep plan facts anywhere else.
- `trip/family.md` describes the travellers. Plan against it: ages, interests, energy, rules. If the user states a new preference, add it to `family.md`.
- The schema is documented in `trip/README.md`. Keep `trip.json` valid against it.

## How to work

1. Interview first. Before building or changing anything big (a new trip, a new day, a rebuilt app), ask the user multiple-choice questions about what matters: who, when, pace, budget, what to avoid. Ask a few at a time, not a form of twenty.
2. Plan against `family.md`. Check each activity against the ages, energy and rules.
3. Every suggested activity gets a plain "what it actually is" line before any history: what you physically do there. "A boardwalk around a steaming orange lake, 45 minutes" beats "a significant geothermal site".
4. Keep the book-and-check list in `trip.json` (`checklist`). It covers visas, entry declarations, driving permits, insurance, health or waiver forms, timed tickets, and rental pickup and return times. Add an item when a plan change creates one, and keep the `when` deadlines current.
5. After every change to `trip.json`, run `python3 app/build.py`, check it builds, and tell the user what to redeploy (`site/` goes to the static host).

## Real tools for real data

- Geocoding and drive times come from Geocodio, never from memory. Run `python3 tools/drive_times.py` after adding places or drives. It needs `GEOCODIO_API_KEY`. Places must have a street address, not a venue name.
- For lookups while planning, use the Geocodio CLI and its Claude Code skill: `npx skills add geocodio/geocodio-cli`.
- Booking facts (times, references, pickup rules) come from the confirmation emails the user points you at, never from memory. When the user says "check my email", read the confirmation, update the booking and every plan item that depends on it.
- Check bookings against the source. If a plan time does not match what the booking page or email says, say so before changing anything.
- When you are not sure of an opening time, a price or an entry rule, say you are not sure and name where to check.

## Style

- Plain language. No filler. No em dashes.
- Identifiers in code are spelled out in full. Comments describe what the code does now.
- Python 3 standard library only. No dependencies to install.
- Keep real personal data (booking references, addresses of real hotels, emails) out of any public fork of this repo.
