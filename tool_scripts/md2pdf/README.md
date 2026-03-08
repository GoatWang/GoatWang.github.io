# md2pdf

Convert Markdown files to styled PDF.

## Requirements

- `markdown`, `weasyprint`, `pygments` (installed automatically via `uv run --with`)
- macOS: `pango` and `glib` via Homebrew (`brew install pango`). The script auto-detects the Homebrew lib path.

## Usage

```bash
uv run --with "markdown,weasyprint,pygments" tool_scripts/md2pdf/md2pdf.py <input.md> [output.pdf] [--css style.css]
```

If no output path is given, the PDF is saved alongside the input with a `.pdf` extension.

## Features

- GitHub-style styling (headings, code blocks, tables, blockquotes)
- Syntax highlighting for fenced code blocks (via Pygments)
- Table of contents support (`[TOC]` marker)
- Relative image paths resolved from input file location
- Custom CSS override via `--css`

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `output` | `<input>.pdf` | Output PDF file path |
| `--css` | built-in | Custom CSS file to override default styling |
