"""Convert video files (.mov, .mp4, etc.) to GIF using ffmpeg.

Usage:
    python tools/to_gif.py <input_video> <output_gif> [--fps 10] [--width 600]

Note: macOS screen recordings use unicode narrow no-break space (U+202F) in
filenames. If the input path fails, the script falls back to glob matching.
"""
import glob
import subprocess
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description="Convert video to GIF")
parser.add_argument("input", help="Input video file path")
parser.add_argument("output", help="Output GIF file path")
parser.add_argument("--fps", type=int, default=10, help="Frames per second (default: 10)")
parser.add_argument("--width", type=int, default=600, help="Output width in pixels (default: 600)")

args = parser.parse_args()

# Resolve input path, falling back to glob if file not found (unicode filename issue)
input_path = args.input
if not Path(input_path).exists():
    candidates = glob.glob(input_path.replace(" AM.", "*AM.").replace(" PM.", "*PM."))
    if not candidates:
        candidates = glob.glob(input_path[:input_path.rfind(".")] + "*")
    if candidates:
        input_path = candidates[0]
        print(f"Resolved to: {input_path}")
    else:
        raise FileNotFoundError(f"Cannot find: {args.input}")

# Two-pass for better quality: generate palette then use it
palette = "/tmp/palette.png"

subprocess.run([
    "ffmpeg", "-y", "-i", input_path,
    "-vf", f"fps={args.fps},scale={args.width}:-1:flags=lanczos,palettegen",
    palette
], check=True)

subprocess.run([
    "ffmpeg", "-y", "-i", input_path,
    "-i", palette,
    "-lavfi", f"fps={args.fps},scale={args.width}:-1:flags=lanczos [x]; [x][1:v] paletteuse",
    args.output
], check=True)

print(f"Converted: {input_path} -> {args.output}")
print(f"Settings: {args.fps} fps, {args.width}px wide")
