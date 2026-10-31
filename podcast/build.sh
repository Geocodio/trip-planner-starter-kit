#!/usr/bin/env bash
# Builds one episode: episodes/<slug>.txt becomes app/audio/<slug>.mp3.
# Usage: ./build.sh <slug> "<Title>" [chunk numbers to redo, e.g. 3,4]
# Needs ELEVENLABS_API_KEY, ffmpeg, and sounds/theme.mp3 + sounds/sting.mp3 (run make_sounds.py once).
# Work files stay in build/<slug> so a failed chunk can be redone alone.
set -euo pipefail
cd "$(dirname "$0")"
slug=$1 title=$2 redo=${3:-}
work=build/$slug
mkdir -p "$work" ../app/audio
cp "episodes/$slug.txt" sounds/theme.mp3 sounds/sting.mp3 "$work/"
cd "$work"
python3 ../../dialogue.py "$slug" "$title" "$redo"
# Transcribe with speaker labels: the transcript checks for dropped text and gives the word timings that level.py and mix.py use.
curl -sf https://api.elevenlabs.io/v1/speech-to-text -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -F model_id=scribe_v1 -F diarize=true -F num_speakers=2 -F "file=@$slug.mp3" > "$slug.json"
python3 - "$slug" <<'PY'
import json, re, sys
heard = len(json.load(open(f"{sys.argv[1]}.json"))["text"].split())
written = len(re.sub(r"\[.*?\]|^[AB]: ", "", open(f"{sys.argv[1]}.txt").read(), flags=re.M).split())
print(f"words heard {heard}, in script {written}")
if abs(heard - written) > written * 0.02: sys.exit("the audio is missing text: redo the chunk that dropped it")
PY
python3 ../../level.py "$slug"
python3 ../../speakers.py "$slug"
python3 ../../mix.py "$slug" "$title" final.mp3
ffmpeg -hide_banner -i final.mp3 -af ebur128=peak=true:framelog=quiet -f null - 2>&1 | grep -E "^\s+(I|Peak):"
ffprobe -v error -show_entries format=duration -of default=nw=1 final.mp3
cp final.mp3 "../../../app/audio/$slug.mp3"
