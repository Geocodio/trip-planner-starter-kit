# Making a trip podcast episode

How the "Listen on the way" episodes are written, built and added to the app. Two parts: the editorial rules (what makes an episode worth listening to) and the technical pipeline (how a script becomes an MP3).

`episodes/example.txt` is a short script for the example trip. It is about 15 lines; a real episode runs several hundred.

---

## Part 1: Editorial

### Who is listening

- **Pitch it at your family.** Name the people in the car in `trip/family.md` and write for the youngest one who is paying attention. A teenager wants an older-cousin tone, not children's TV.
- Put each person's interest into the show. A word-origin fan gets an etymology thread; a film fan gets behind-the-scenes stories; a gross-facts fan gets the gross facts.
- Decide what must not be spoiled (a book or film someone has not finished) and keep to it.

### What an episode is for

Entertaining first, but every fact should pay off when the family is standing at the place. Prefer "look for this when you get there" over facts that only live in the car.

### Two hosts

Two hosts of equal standing who joke with each other. Neither is the expert. Both tell stories and both react. A sceptic line ("No way, that's made up") that moves between them is a good way to land a surprising fact. Give them names, a country or accent that matches your destination, and a small difference in character (one sillier, one steadier).

### A running bit

Pick one or two bits that return in every episode, so it feels like a show. Ideas:

1. A local word of the segment: one slang word per segment, with meaning, example and origin. Say the same phrase each time ("word of the segment"), because `mix.py` plays the sting right after it (`STING_WORD`).
2. Word-nerd moments: the origin of place names on the route.
3. Spotting challenges: three to five things that are really on your route ("bet you can't spot it"). No points and no prizes.
4. One hard trivia question near the end, then the answer.
5. Callbacks to yesterday and a setup for tomorrow.

### Tone

- Short, spoken sentences. Write for the ear.
- No quizzes with scores, no "shout it out", no safety nagging. A joke is better than a warning.
- Gross, spooky and surprising is welcome.

### Structure that works

1. Cold open: names, a hook joke, the episode title, the drive time.
2. First running-bit moment.
3. Two to four story segments: a hook, the story, a payoff at the destination.
4. A "today's mission" recap of what to find on site.
5. The trivia question.
6. Sign-off.

### Length from drive time

Aim for about a third to a half of the drive, so there is time to look out of the window. Dialogue reads at roughly 160 words per minute including banter.

| Drive | Episode | Script |
|---|---|---|
| 35 min | 12 min | about 1,900 words |
| 70 min | 18 to 19 min | about 3,000 words |

Use the real drive time from `trip.json` (`driveTimes`, from Geocodio).

### Spotting challenges must be on your route

Check that every landmark you send the family to look for is really on the road you drive. Get the route geometry from a routing service, geocode the landmark's street address with Geocodio, and check that it lies within about 1 km of the route. A made-up "look for the giant statue on your left" that is not there costs the show its trust.

### Fact checking

- Check every number, date and name against at least one good source (an encyclopedia, the attraction's own site, an official tourism or heritage body).
- If a popular story cannot be confirmed, frame it as "the story goes" or "the guides say".
- If a source contradicts a common claim, use the cautious version.
- Check names in other languages (macrons, pronunciation) against an official source.
- If the episode tells the family to be somewhere at a time (a daily geyser show at 10:15), check it against the plan and the booking, and add it to `trip.json` if it is new.

### Script format

`episodes/<slug>.txt`, one line per turn, `A: ` or `B: ` followed by the text:

```
A: Kia ora, Rivera family! I'm Mia.
B: And I'm Ben. Let's go.
```

- Alternate speakers. Two lines in a row from the same host sound like a glitch.
- Use audio tags sparingly: `[laughs]`, `[whispers]`, `[sighs]`, `[pause]`. Never write a line that is only "..."; use `[pause]`.
- Spell numbers the way they should be said ("ten fifteen", "seventy-four degrees").

### Brief checklist before writing

- [ ] Which day, which drive, departure time, drive length.
- [ ] The route, checked, and three to five spottable things on it.
- [ ] What they will see at the destination, and what to look for there.
- [ ] Stories that fit each person's interests.
- [ ] Callbacks to yesterday and a setup for tomorrow.
- [ ] Any plan change the episode implies.

---

## Part 2: Technical

### Files

```
podcast/
  GUIDE.md         this file
  build.sh         one command: script -> app/audio/<slug>.mp3
  dialogue.py      text-to-dialogue, chunked, with retry (voice IDs and model at the top)
  level.py         brings both speakers to the same loudness
  mix.py           theme intro and outro, and the stings
  speakers.py      prints loudness per speaker (a check)
  make_sounds.py   generates sounds/theme.mp3 and sounds/sting.mp3 with ElevenLabs
  sounds/          your theme and sting (generated, not shipped)
  episodes/        the scripts, one .txt per episode
  build/           work files per episode (git-ignored)
```

### One-time setup

1. `export ELEVENLABS_API_KEY=...` (see `.env.example`) and install `ffmpeg`.
2. **Pick the voices.** List voices from the ElevenLabs library filtered by the accent of your destination, listen to a few previews, and choose two that sound different from each other:
   ```
   curl -s -H "xi-api-key: $ELEVENLABS_API_KEY" "https://api.elevenlabs.io/v1/shared-voices?accent=new%20zealand&language=en" | python3 -m json.tool | less
   ```
   Add a voice to your account if the library requires it, then paste the two voice IDs into `VOICES` at the top of `dialogue.py`.
3. **Check the model.** `curl -s -H "xi-api-key: $ELEVENLABS_API_KEY" https://api.elevenlabs.io/v1/models` lists the models. Use the newest one that can do dialogue, and set `MODEL_ID` in `dialogue.py`. Check again before each new episode, since models change.
4. **Make the theme and sting once:** `python3 podcast/make_sounds.py`. Edit the two prompts in the script first. Reuse the files so every episode sounds like the same show. (It uses credits, so it skips files that already exist.)

### Build an episode

```
./podcast/build.sh <slug> "<Episode title>"
```

Steps:

1. **`dialogue.py`** splits the script into chunks of about 2,200 characters and sends each to `POST /v1/text-to-dialogue`. It retries a timed-out chunk up to three times and joins the chunks with ffmpeg. If one chunk still fails, redo only that chunk: `./podcast/build.sh <slug> "<title>" 3`.
2. **Transcript check.** Speech-to-text (`scribe_v1`, `diarize=true`, `num_speakers=2`) transcribes the result. The build stops if the transcript is more than 2 percent shorter than the script, which means a chunk dropped text.
3. **`level.py`** measures each speaker's loudness from the diarized turns and applies a separate gain to each, to -16 LUFS. Raw dialogue output is quiet and uneven. Gain changes fall in the middle of the pause between turns, so they do not click.
4. **`mix.py`** adds the start of the theme (fading out) at the beginning, the full theme at the end, and the sting just after each spoken `STING_WORD`. A limiter keeps peaks below full scale.
5. The build prints loudness, peak and duration, then copies the result to `app/audio/<slug>.mp3`.

Targets: integrated loudness about -17 LUFS, peak below -1 dBFS, speakers within 0.5 dB of each other (`speakers.py`).

### Put it in the app

1. In `trip/trip.json`, add the episode to that day's drive:
   ```
   "episode": {"file": "<slug>", "title": "<Title>", "about": "Start it as you leave the hotel."}
   ```
2. `python3 app/build.py`. The "Listen on the way" player appears on that drive card, and the audio is precached so it plays offline.
3. Redeploy `site/`. Phones get the episode the next time the app opens online.

### Gotchas

- **The ffmpeg limiter raises the volume by default.** Always use `alimiter=...:level=false`, or it clips.
- **A chunk can time out** at ElevenLabs. The retry covers most cases; otherwise redo that chunk alone.
- **Do not predict duration from script length** when you switch models. Measure and adjust.
- **Keep the MP3s small.** 64 kbps mono is fine for speech and keeps a 15 minute episode near 7 MB.
- **Safari needs byte ranges** to play audio, including from a cache. `app/sw.js` serves them (the `partial` function).
