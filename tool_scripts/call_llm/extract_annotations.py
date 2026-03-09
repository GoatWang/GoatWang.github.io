#!/usr/bin/env python3
"""Post-process LLM report markdown files to extract JSON annotation blocks.

Scans a report directory for .md files, extracts fenced ```json``` blocks,
validates annotation structure, and produces per-file sidecar .json files
plus merged _annotations.json and _summary.json.

Usage:
    python extract_annotations.py <report_dir>
"""

import argparse
import json
import re
import sys
from pathlib import Path

ACTION_PRIORITY = {
    "remove": 0,
    "rewrite": 1,
    "move": 2,
    "merge": 3,
    "split": 4,
    "minor": 5,
}

REQUIRED_FIELDS = {"paragraph_ids", "dimension", "issue"}


def extract_json_text(content: str) -> str | None:
    """Extract JSON text from markdown content using multiple strategies."""
    # Strategy 1: fenced ```json ... ``` block
    match = re.search(r"```json\s*\n(.*?)```", content, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Strategy 2: bare {...} containing "annotations"
    match = re.search(r"(\{[^{}]*\"annotations\".*\})", content, re.DOTALL)
    if match:
        return match.group(1).strip()

    return None


def validate_annotation(ann: dict, index: int, source: str) -> bool:
    """Validate a single annotation has required fields with correct types."""
    missing = REQUIRED_FIELDS - set(ann.keys())
    if missing:
        print(f"  WARNING: {source} annotation[{index}] missing fields: {missing}")
        return False

    if not isinstance(ann["paragraph_ids"], list) or not all(
        isinstance(pid, str) for pid in ann["paragraph_ids"]
    ):
        print(
            f"  WARNING: {source} annotation[{index}] 'paragraph_ids' must be list of strings"
        )
        return False

    if not isinstance(ann["dimension"], str):
        print(
            f"  WARNING: {source} annotation[{index}] 'dimension' must be a string"
        )
        return False

    if not isinstance(ann["issue"], str):
        print(f"  WARNING: {source} annotation[{index}] 'issue' must be a string")
        return False

    return True


def process_file(md_path: Path) -> tuple[str, list[dict]] | None:
    """Process a single .md file. Returns (source_name, annotations) or None."""
    source = md_path.stem
    content = md_path.read_text(encoding="utf-8")

    json_text = extract_json_text(content)
    if json_text is None:
        print(f"  WARNING: No JSON block found in {md_path.name}, skipping")
        return None

    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as e:
        print(f"  WARNING: Malformed JSON in {md_path.name}: {e}")
        return None

    if not isinstance(data, dict) or "annotations" not in data:
        print(f"  WARNING: No 'annotations' key in {md_path.name}, skipping")
        return None

    annotations = data["annotations"]
    if not isinstance(annotations, list):
        print(f"  WARNING: 'annotations' is not a list in {md_path.name}, skipping")
        return None

    valid = []
    for i, ann in enumerate(annotations):
        if validate_annotation(ann, i, md_path.name):
            valid.append(ann)

    if not valid:
        print(f"  WARNING: No valid annotations in {md_path.name}")
        return None

    # Write sidecar JSON
    sidecar_path = md_path.with_suffix(".json")
    sidecar_path.write_text(
        json.dumps({"annotations": valid}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"  Wrote {sidecar_path.name} ({len(valid)} annotations)")

    return source, valid


def build_merged(
    all_annotations: dict[str, list[dict]],
) -> dict[str, list[dict]]:
    """Build merged annotations grouped by paragraph ID."""
    merged: dict[str, list[dict]] = {}

    for source, annotations in all_annotations.items():
        for ann in annotations:
            entry = {"source": source}
            entry["dimension"] = ann["dimension"]
            if "score" in ann:
                entry["score"] = ann["score"]
            if "action" in ann:
                entry["action"] = ann["action"]
            entry["issue"] = ann["issue"]
            if "suggestion" in ann:
                entry["suggestion"] = ann["suggestion"]

            for pid in ann["paragraph_ids"]:
                merged.setdefault(pid, []).append(entry)

    return dict(sorted(merged.items(), key=_paragraph_sort_key))


def _paragraph_sort_key(item: tuple[str, list]) -> tuple[int, str]:
    """Sort paragraph IDs numerically when possible (e.g. ¶1 before ¶10)."""
    pid = item[0]
    digits = re.sub(r"[^\d]", "", pid)
    if digits:
        return (0, digits.zfill(10))
    return (1, pid)


def build_summary(merged: dict[str, list[dict]]) -> dict[str, dict]:
    """Build summary with top action and annotation count per paragraph."""
    summary: dict[str, dict] = {}

    for pid, entries in merged.items():
        actions = [e["action"] for e in entries if "action" in e]
        top_action = None
        if actions:
            top_action = min(
                actions, key=lambda a: ACTION_PRIORITY.get(a, 999)
            )

        summary[pid] = {
            "top_action": top_action,
            "annotation_count": len(entries),
        }

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Extract JSON annotations from LLM report markdown files."
    )
    parser.add_argument(
        "report_dir",
        type=Path,
        help="Directory containing .md report files",
    )
    args = parser.parse_args()

    report_dir: Path = args.report_dir
    if not report_dir.is_dir():
        print(f"Error: {report_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    md_files = sorted(
        f for f in report_dir.glob("*.md") if not f.name.startswith("_")
    )

    if not md_files:
        print(f"No .md files found in {report_dir}")
        sys.exit(0)

    print(f"Found {len(md_files)} report file(s) in {report_dir}\n")

    all_annotations: dict[str, list[dict]] = {}
    succeeded = 0
    failed = 0

    for md_path in md_files:
        print(f"Processing {md_path.name}...")
        result = process_file(md_path)
        if result is not None:
            source, annotations = result
            all_annotations[source] = annotations
            succeeded += 1
        else:
            failed += 1

    # Write merged annotations
    if all_annotations:
        merged = build_merged(all_annotations)
        merged_path = report_dir / "_annotations.json"
        merged_path.write_text(
            json.dumps(merged, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"\nWrote {merged_path.name} ({len(merged)} paragraph(s))")

        # Write summary
        summary = build_summary(merged)
        summary_path = report_dir / "_summary.json"
        summary_path.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {summary_path.name}")

    # Print summary
    total = succeeded + failed
    print(f"\nDone: {succeeded}/{total} files extracted, {failed} skipped")


if __name__ == "__main__":
    main()
