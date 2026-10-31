# Brings each speaker to the same loudness, using the diarized word timings in <name>.json; rewrites <name>.mp3.
import json, re, subprocess, sys

name, target = sys.argv[1], -16.0
words = [w for w in json.load(open(f"{name}.json"))["words"] if w.get("type", "word") == "word" and w.get("speaker_id")]
turns = []
for word in words:
    if turns and turns[-1][0] == word["speaker_id"]:
        turns[-1][2] = word["end"]
    else:
        turns.append([word["speaker_id"], word["start"], word["end"]])
for previous, current in zip(turns, turns[1:]):  # split each pause between speakers at its middle so gain changes fall in silence
    middle = (previous[2] + current[1]) / 2
    previous[2] = current[1] = middle
turns[0][1], turns[-1][2] = 0, 1e6


def between(spans):
    return "+".join(f"between(t,{start:.3f},{end:.3f})" for _, start, end in spans)


def loudness(source, spans):
    output = subprocess.run(["ffmpeg", "-hide_banner", "-i", source, "-af", f"aselect='{between(spans)}',asetpts=N/SR/TB,ebur128=framelog=quiet",
                             "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", output)[-1])


filters = []
for speaker in sorted({turn[0] for turn in turns}):
    spans = [turn for turn in turns if turn[0] == speaker]
    gain = target - loudness(f"{name}.mp3", spans)
    print(speaker, f"{gain:+.1f} dB")
    filters.append(f"volume={gain:.2f}dB:enable='{between(spans)}'")
# level=false keeps the limiter from raising the volume, which would clip.
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{name}.mp3", "-af", ",".join(filters) + ",alimiter=limit=0.89:level=false",
                "-b:a", "128k", f"{name}-level.mp3"], check=True)
subprocess.run(["mv", f"{name}-level.mp3", f"{name}.mp3"], check=True)
