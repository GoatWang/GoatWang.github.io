#!/usr/bin/env python3
"""Inject paragraph IDs into a Hugo markdown blog post.

Reads a Hugo markdown file, strips YAML frontmatter, walks through content
blocks, and injects <!-- ¶N --> markers before each content block. Outputs
the annotated markdown and a JSON ID map.

Usage:
    python inject_paragraph_ids.py <input.md> <output.md> --id-map <output.json>
"""

import argparse
import json
import re
import sys
from pathlib import Path


def parse_frontmatter(lines):
    """Return the index of the line after the closing '---' of YAML frontmatter.

    If no frontmatter is found, returns 0.
    """
    if not lines or lines[0].rstrip() != "---":
        return 0
    for i in range(1, len(lines)):
        if lines[i].rstrip() == "---":
            return i + 1
    return 0


def is_blank(line):
    return line.strip() == ""


def is_heading(line):
    return re.match(r"^#{1,6}\s", line) is not None


def is_blockquote(line):
    return line.startswith(">")


def is_fence(line):
    stripped = line.rstrip()
    return stripped.startswith("```") or stripped.startswith("~~~")


def is_unordered_list_item(line):
    return re.match(r"^[-*+]\s", line) is not None


def is_ordered_list_item(line):
    return re.match(r"^\d+\.\s", line) is not None


def is_list_item(line):
    return is_unordered_list_item(line) or is_ordered_list_item(line)


def is_list_continuation(line):
    """A line that continues a list block: either a new list item or indented continuation."""
    if is_list_item(line):
        return True
    # Indented continuation (at least 2 spaces or a tab)
    if re.match(r"^(\s{2,}|\t)", line) and line.strip():
        return True
    return False


def is_hugo_shortcode(line):
    return re.match(r"^\s*\{\{<.*>\}\}\s*$", line) is not None or \
           re.match(r"^\s*\{\{%.*%\}\}\s*$", line) is not None


def is_image_only(line):
    return re.match(r"^\s*!\[.*\]\(.*\)\s*$", line) is not None


def is_horizontal_rule(line):
    stripped = line.strip()
    return re.match(r"^[-*_]{3,}$", stripped) is not None


def extract_preview(lines):
    """Extract first 50 chars of text content from a block's lines."""
    text = " ".join(l.strip() for l in lines if l.strip())
    # Strip markdown formatting for preview
    text = re.sub(r"^#+\s*", "", text)
    text = re.sub(r"^>\s*", "", text)
    text = re.sub(r"^[-*+]\s", "", text)
    text = re.sub(r"^\d+\.\s", "", text)
    return text[:50]


def detect_blocks(lines, content_start):
    """Detect content blocks in the markdown content.

    Returns a list of block dicts:
        { "type": str, "start": int, "end": int, "lines": [str] }
    where start/end are 0-based indices into the original file lines.
    """
    blocks = []
    i = content_start
    n = len(lines)

    while i < n:
        line = lines[i]

        # Skip blank lines
        if is_blank(line):
            i += 1
            continue

        # Skip horizontal rules
        if is_horizontal_rule(line):
            i += 1
            continue

        # Skip Hugo shortcodes
        if is_hugo_shortcode(line):
            i += 1
            continue

        # Skip image-only lines
        if is_image_only(line):
            i += 1
            continue

        # Fenced code block
        if is_fence(line):
            start = i
            i += 1
            while i < n and not is_fence(lines[i]):
                i += 1
            if i < n:
                i += 1  # skip closing fence
            blocks.append({
                "type": "code",
                "start": start,
                "end": i - 1,
                "lines": lines[start:i],
            })
            continue

        # Heading
        if is_heading(line):
            blocks.append({
                "type": "heading",
                "start": i,
                "end": i,
                "lines": [line],
            })
            i += 1
            continue

        # Blockquote: consecutive lines starting with > (allow blank > lines within)
        if is_blockquote(line):
            start = i
            while i < n:
                if is_blockquote(lines[i]):
                    i += 1
                elif is_blank(lines[i]) and i + 1 < n and is_blockquote(lines[i + 1]):
                    # Blank line followed by another blockquote line -> continuation
                    i += 1
                else:
                    break
            blocks.append({
                "type": "blockquote",
                "start": start,
                "end": i - 1,
                "lines": lines[start:i],
            })
            continue

        # List block: consecutive list items (and their continuations)
        if is_list_item(line):
            start = i
            i += 1
            while i < n:
                if is_list_continuation(lines[i]):
                    i += 1
                elif is_blank(lines[i]) and i + 1 < n and is_list_continuation(lines[i + 1]):
                    # Blank line within list (loose list)
                    i += 1
                else:
                    break
            blocks.append({
                "type": "list",
                "start": start,
                "end": i - 1,
                "lines": lines[start:i],
            })
            continue

        # Regular paragraph: consecutive non-blank, non-special lines
        start = i
        i += 1
        while i < n:
            if is_blank(lines[i]):
                break
            if is_heading(lines[i]) or is_blockquote(lines[i]) or is_fence(lines[i]):
                break
            if is_list_item(lines[i]):
                break
            if is_hugo_shortcode(lines[i]):
                break
            if is_image_only(lines[i]):
                break
            if is_horizontal_rule(lines[i]):
                break
            i += 1
        blocks.append({
            "type": "paragraph",
            "start": start,
            "end": i - 1,
            "lines": lines[start:i],
        })
        continue

    return blocks


def main():
    parser = argparse.ArgumentParser(
        description="Inject paragraph IDs into a Hugo markdown blog post."
    )
    parser.add_argument("input", help="Input markdown file")
    parser.add_argument("output", help="Output annotated markdown file")
    parser.add_argument(
        "--id-map", required=True, help="Output JSON ID map file"
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: {input_path} not found", file=sys.stderr)
        sys.exit(1)

    text = input_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    # Ensure all lines have newline endings for consistency
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"

    content_start = parse_frontmatter(lines)
    blocks = detect_blocks(lines, content_start)

    # Build ID map and prepare output
    id_map = {}
    # We need to track offset for inserted comment lines
    output_lines = list(lines[:content_start])
    inserted_count = 0

    for idx, block in enumerate(blocks):
        pid = idx + 1
        marker = f"<!-- \u00b6{pid} -->\n"
        block_type = block["type"]

        id_map[f"\u00b6{pid}"] = {
            "type": block_type,
            "start_line": block["start"] + 1,  # 1-based
            "end_line": block["end"] + 1,       # 1-based
            "preview": extract_preview(block["lines"]),
        }

        # Figure out which original lines to emit before this block
        prev_end = blocks[idx - 1]["end"] + 1 if idx > 0 else content_start
        # Emit lines between previous block end and this block start (blanks, skipped lines, etc.)
        for j in range(prev_end, block["start"]):
            output_lines.append(lines[j])

        # Insert marker
        output_lines.append(marker)
        # Insert block lines
        for j in range(block["start"], block["end"] + 1):
            output_lines.append(lines[j])

    # Emit any trailing lines after the last block
    if blocks:
        last_end = blocks[-1]["end"] + 1
        for j in range(last_end, len(lines)):
            output_lines.append(lines[j])
    else:
        # No blocks found, just copy everything
        for j in range(content_start, len(lines)):
            output_lines.append(lines[j])

    # Write output
    output_path = Path(args.output)
    output_path.write_text("".join(output_lines), encoding="utf-8")

    id_map_path = Path(args.id_map)
    id_map_path.write_text(
        json.dumps(id_map, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Injected {len(blocks)} paragraph IDs into {args.output}")
    print(f"ID map written to {args.id_map}")


if __name__ == "__main__":
    main()
