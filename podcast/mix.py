# Adds the theme intro and outro, and a sting after each spoken running-bit phrase, using word timings in <name>.json.
import json, subprocess, sys

# The sting plays right after every spoken occurrence of this word. If your running bit ends with "...of the segment",
# the word is "segment". Set it to None to skip stings.
STING_WORD = "segment"
ARTIST = "Trip podcast"

name, title, output = sys.argv[1], sys.argv[2], sys.argv[3]
words = json.load(open(f"{name}.json"))["words"]
cuts = [w["end"] + 0.15 for w in words if STING_WORD and w["text"].lower().strip("!.,?") == STING_WORD]
fmt = "aformat=sample_rates=44100:channel_layouts=mono"
parts = [f"[1:a]{fmt},atrim=0:8,afade=t=out:st=5.5:d=2.5,volume=0.5[intro]"]
labels = ["[intro]"]
bounds = [0] + cuts + [None]
for index in range(len(bounds) - 1):
    end = f":{bounds[index + 1]}" if bounds[index + 1] is not None else ""
    parts.append(f"[0:a]{fmt},atrim={bounds[index]}{end},asetpts=PTS-STARTPTS[v{index}]")
    labels.append(f"[v{index}]")
    if bounds[index + 1] is not None:
        parts.append(f"[2:a]{fmt},volume=0.45,apad=pad_dur=0.25[s{index}]")
        labels.append(f"[s{index}]")
parts.append(f"[1:a]{fmt},afade=t=in:d=1,volume=0.5,adelay=600[outro]")
labels.append("[outro]")
graph = ";".join(parts) + ";" + "".join(labels) + f"concat=n={len(labels)}:v=0:a=1,alimiter=limit=0.8:level=false[out]"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{name}.mp3", "-i", "theme.mp3", "-i", "sting.mp3", "-filter_complex", graph,
                "-map", "[out]", "-ac", "1", "-b:a", "64k", "-metadata", f"title={title}", "-metadata", f"artist={ARTIST}", output], check=True)
print(output, len(cuts), "stings")
