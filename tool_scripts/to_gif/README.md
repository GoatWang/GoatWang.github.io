# to_gif

Convert video files (.mov, .mp4, etc.) to GIF using ffmpeg.

## Requirements

- `ffmpeg` installed (`brew install ffmpeg`)

## Usage

```bash
python3 tool_scripts/to_gif/to_gif.py <input_video> <output_gif> --fps <fps> --width <width>
```

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--fps` | 10 | Frames per second |
| `--width` | 600 | Output width in pixels |

## Notes

- For blog posts, use **1440px width** and **3fps** for Retina-sharp GIFs at manageable file sizes.
- macOS screen recordings use a unicode narrow no-break space (U+202F) in filenames. The script handles this via glob fallback.
