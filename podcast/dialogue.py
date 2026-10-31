# Turns <name>.txt (lines of "A: text" / "B: text") into <name>.mp3 with ElevenLabs text-to-dialogue, one request per ~2,200 characters.
# Optional third argument: comma-separated chunk numbers to regenerate; the other chunks are reused from disk.
import json, os, subprocess, sys, urllib.request

# ---- Configuration: change these for your show ------------------------------------------------------------------
# Voice IDs are placeholders. Pick two voices that match where you are going (see GUIDE.md, "Pick the voices"):
#   curl -s -H "xi-api-key: $ELEVENLABS_API_KEY" "https://api.elevenlabs.io/v1/shared-voices?accent=new%20zealand&language=en"
VOICES = {"A": "REPLACE_WITH_VOICE_ID_FOR_HOST_A", "B": "REPLACE_WITH_VOICE_ID_FOR_HOST_B"}
# The newest dialogue-capable model. Check GET /v1/models before each episode (GUIDE.md).
MODEL_ID = "eleven_v4"
ARTIST = "Trip podcast"
# -----------------------------------------------------------------------------------------------------------------

name, title = sys.argv[1], sys.argv[2]
if any(voice.startswith("REPLACE") for voice in VOICES.values()):
    sys.exit("Set the two voice IDs at the top of dialogue.py first (see GUIDE.md).")
lines = [line.split(": ", 1) for line in open(f"{name}.txt").read().splitlines() if line.strip()]
chunks, current, size = [], [], 0
for speaker, text in lines:
    if current and size + len(text) > 2200:
        chunks.append(current)
        current, size = [], 0
    current.append({"text": text, "voice_id": VOICES[speaker]})
    size += len(text)
chunks.append(current)
only = set(map(int, sys.argv[3].split(","))) if len(sys.argv) > 3 and sys.argv[3] else None
for index, inputs in enumerate(chunks):
    part = f"{name}-{index}.mp3"
    if only is not None and index not in only:
        continue
    request = urllib.request.Request("https://api.elevenlabs.io/v1/text-to-dialogue?output_format=mp3_44100_128",
        data=json.dumps({"inputs": inputs, "model_id": MODEL_ID}).encode(),
        headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "Content-Type": "application/json"})
    for attempt in range(3):  # long chunks sometimes time out at ElevenLabs; a retry usually works
        try:
            open(part, "wb").write(urllib.request.urlopen(request, timeout=300).read())
            break
        except TimeoutError:
            if attempt == 2:
                raise
    print(part, len(inputs))
open(f"{name}-list.txt", "w").write("".join(f"file '{name}-{index}.mp3'\n" for index in range(len(chunks))))
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{name}-list.txt", "-ac", "1", "-b:a", "64k",
                "-metadata", f"title={title}", "-metadata", f"artist={ARTIST}", f"{name}.mp3"], check=True)
