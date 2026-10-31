#!/usr/bin/env python3
"""Generates your show's theme and sting with ElevenLabs, into podcast/sounds/theme.mp3 and sting.mp3.

Run once: ELEVENLABS_API_KEY=... python3 podcast/make_sounds.py
The theme comes from the music endpoint (POST /v1/music) and the sting from the sound-effects endpoint
(POST /v1/sound-generation). Edit the two prompts below to match your trip, and rerun until you like them.
Existing files are kept unless you pass --force, because each generation uses credits.
"""
import json
import os
import sys
import urllib.request

THEME_PROMPT = "Upbeat acoustic road trip theme, ukulele and hand percussion, sunny and playful, instrumental, short and loopable"
THEME_SECONDS = 12
STING_PROMPT = "A short cheerful two-note chime with a little sparkle, a quick game-show style reward sound"
STING_SECONDS = 2

SOUNDS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")


def post(path, body):
    request = urllib.request.Request(f"https://api.elevenlabs.io/v1/{path}?output_format=mp3_44100_128", data=json.dumps(body).encode(),
                                     headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=300) as response:
        return response.read()


def main():
    force = "--force" in sys.argv
    os.makedirs(SOUNDS, exist_ok=True)
    jobs = [("theme.mp3", "music", {"prompt": THEME_PROMPT, "music_length_ms": THEME_SECONDS * 1000}),
            ("sting.mp3", "sound-generation", {"text": STING_PROMPT, "duration_seconds": STING_SECONDS})]
    for file_name, endpoint, body in jobs:
        target = os.path.join(SOUNDS, file_name)
        if os.path.exists(target) and not force:
            print("keeping", target)
            continue
        with open(target, "wb") as file:
            file.write(post(endpoint, body))
        print("wrote", target)


if __name__ == "__main__":
    if not os.environ.get("ELEVENLABS_API_KEY"):
        sys.exit("Set ELEVENLABS_API_KEY first.")
    main()
