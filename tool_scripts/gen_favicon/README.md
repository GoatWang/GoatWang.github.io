# gen_favicon

Generate favicon files from a source image.

## Requirements

- `Pillow` (installed automatically via `uv run --with`)

## Usage

```bash
uv run --with Pillow tool_scripts/gen_favicon/gen_favicon.py <input_image> [--output-dir static]
```

## Output

| File | Size | Purpose |
|------|------|---------|
| `favicon.ico` | 16/32/48px | Browser tab icon |
| `favicon-16x16.png` | 16x16 | Small favicon |
| `favicon-32x32.png` | 32x32 | Standard favicon |
| `apple-touch-icon.png` | 180x180 | iOS home screen icon |

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--output-dir` | `static` | Output directory for generated files |
