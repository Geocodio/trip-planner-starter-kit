# 08 Podcast brief

Use for a drive of an hour or more. Needs ELEVENLABS_API_KEY and ffmpeg. Read podcast/GUIDE.md first.

```
Write a podcast episode for the drive on <date>, following podcast/GUIDE.md. First interview me with multiple-choice questions: who is in the car, what each person likes, what to skip, how much humour, and any running bit we want. Then:
1. Get the route and drive time from trip.json (Geocodio drive times) and pick a length of about a third to a half of the drive.
2. Pick three to five things that really are on our route for the spotting challenges, and check each one against the route.
3. Fact check every number, date and name against a good source.
4. Write podcast/episodes/<slug>.txt with two hosts, one line per turn, "A: " and "B: ".
5. Show me the script before building audio, because building costs ElevenLabs credits.

After I approve: ./podcast/build.sh <slug> "<Title>", add the episode to the day's drive in trip.json, rebuild the app and redeploy.
```
