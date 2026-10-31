# Prints the loudness of each speaker in <name>.mp3, from the diarized transcript in <name>.json. Use it to check level.py.
import json, re, subprocess, sys

name = sys.argv[1]
words = [w for w in json.load(open(f"{name}.json"))["words"] if w.get("type", "word") == "word" and w.get("speaker_id")]
turns = []
for word in words:
    if turns and turns[-1][0] == word["speaker_id"] and word["start"] - turns[-1][2] < 1.0:
        turns[-1][2] = word["end"]
    else:
        turns.append([word["speaker_id"], word["start"], word["end"]])


def loudness(spans):
    expression = "+".join(f"between(t,{start:.2f},{end:.2f})" for _, start, end in spans)
    output = subprocess.run(["ffmpeg", "-hide_banner", "-i", f"{name}.mp3", "-af", f"aselect='{expression}',asetpts=N/SR/TB,ebur128=framelog=quiet",
                             "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", output)[-1])


for speaker in sorted({turn[0] for turn in turns}):
    spans = [turn for turn in turns if turn[0] == speaker and turn[2] - turn[1] > 1.5]
    print(name, speaker, len(spans), "turns", loudness(spans), "LUFS")
