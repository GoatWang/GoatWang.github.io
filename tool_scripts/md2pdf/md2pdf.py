"""Convert Markdown files to PDF with styled output.

Usage:
    uv run --with "markdown,weasyprint,pygments" tool_scripts/md2pdf/md2pdf.py <input.md> [output.pdf] [--css style.css]

Supports GitHub-flavored features: fenced code blocks with syntax highlighting,
tables, table of contents, and more.
"""

import argparse
import os
import platform
import subprocess
import sys

# On macOS with Homebrew, WeasyPrint needs help finding native libraries.
if platform.system() == "Darwin":
    brew_prefix = subprocess.run(
        ["brew", "--prefix"], capture_output=True, text=True
    ).stdout.strip()
    if brew_prefix:
        lib_path = os.path.join(brew_prefix, "lib")
        os.environ.setdefault("DYLD_FALLBACK_LIBRARY_PATH", lib_path)

import markdown
from weasyprint import HTML

DEFAULT_CSS = """
@page {
    size: A4;
    margin: 2.5cm;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    font-size: 12pt;
    line-height: 1.6;
    color: #24292e;
    max-width: 100%;
}

h1, h2, h3, h4, h5, h6 {
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    font-weight: 600;
    line-height: 1.25;
}

h1 { font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
h2 { font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
h3 { font-size: 1.25em; }

p { margin: 0 0 1em 0; }

a { color: #0366d6; text-decoration: none; }

code {
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    font-size: 0.85em;
    background-color: #f6f8fa;
    padding: 0.2em 0.4em;
    border-radius: 3px;
}

pre {
    background-color: #f6f8fa;
    border-radius: 6px;
    padding: 16px;
    overflow-x: auto;
    line-height: 1.45;
    margin: 0 0 1em 0;
}

pre code {
    background: none;
    padding: 0;
    font-size: 0.85em;
}

blockquote {
    margin: 0 0 1em 0;
    padding: 0 1em;
    color: #6a737d;
    border-left: 0.25em solid #dfe2e5;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 0 0 1em 0;
}

th, td {
    border: 1px solid #dfe2e5;
    padding: 6px 13px;
    text-align: left;
}

th {
    background-color: #f6f8fa;
    font-weight: 600;
}

tr:nth-child(even) { background-color: #f6f8fa; }

img { max-width: 100%; }

hr {
    border: none;
    border-top: 1px solid #eaecef;
    margin: 1.5em 0;
}

ul, ol { padding-left: 2em; margin: 0 0 1em 0; }
li { margin: 0.25em 0; }

/* Pygments code highlighting */
.codehilite { background: #f6f8fa; border-radius: 6px; padding: 16px; margin: 0 0 1em 0; }
.codehilite pre { background: none; padding: 0; margin: 0; }
"""


def convert(input_path, output_path, css_path=None):
    with open(input_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    extensions = [
        "fenced_code",
        "codehilite",
        "tables",
        "toc",
        "smarty",
        "md_in_html",
    ]
    extension_configs = {
        "codehilite": {
            "css_class": "codehilite",
            "guess_lang": True,
        },
    }

    html_body = markdown.markdown(
        md_text, extensions=extensions, extension_configs=extension_configs
    )

    css = DEFAULT_CSS
    if css_path:
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>{css}</style>
</head>
<body>
{html_body}
</body>
</html>"""

    base_url = os.path.dirname(os.path.abspath(input_path))
    HTML(string=html, base_url=base_url).write_pdf(output_path)
    print(f"Converted: {input_path} -> {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Convert Markdown to PDF")
    parser.add_argument("input", help="Input Markdown file")
    parser.add_argument("output", nargs="?", help="Output PDF file (default: same name with .pdf)")
    parser.add_argument("--css", help="Custom CSS file (overrides default styling)")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: {args.input} not found", file=sys.stderr)
        sys.exit(1)

    output = args.output or os.path.splitext(args.input)[0] + ".pdf"
    convert(args.input, output, args.css)


if __name__ == "__main__":
    main()
