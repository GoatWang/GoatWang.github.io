#!/usr/bin/env python3
"""
Report Renderer — dynamic server that renders LLM review reports on the fly.

Usage:
    cd tool_scripts/report_renderer && uv run render.py [--port 8899]

No files are generated. The server reads markdown from reports/ and renders
HTML dynamically on each request.

Routes:
    /                          → Index page listing all report folders
    /report/<folder_name>      → Report page with tabbed view
    /report/<folder_name>/interactive → Two-panel interactive review viewer
    /static/images/...         → Serves blog post images
"""

import argparse
import http.server
import json
import pathlib
import re
import socketserver
import sys
import urllib.parse

import markdown
from pygments.formatters import HtmlFormatter


SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR / "../.."
REPORTS_DIR = PROJECT_ROOT / "reports"
CONTENT_DIR = PROJECT_ROOT / "content" / "posts"

REPORT_DIR_PATTERN = re.compile(r"^(\d{8})_(\d+)_(.+)$")
REPORT_FILE_PATTERN = re.compile(r"^(\w+?)_(\w+)\.md$")

TASKS = ["title", "tone", "arrangement", "ai_slop"]
TASK_LABELS = {"title": "Title", "tone": "Tone", "arrangement": "Arrangement", "ai_slop": "AI Slop"}
KNOWN_MODELS = {"claude", "gemini", "grok"}


def scan_single_report(report_dir: pathlib.Path):
    data = {"models": {}, "synthesis": None}

    synth_file = report_dir / "synthesis.md"
    if synth_file.exists():
        data["synthesis"] = synth_file.read_text(encoding="utf-8")

    for f in sorted(report_dir.iterdir()):
        if not f.is_file() or f.name.startswith("_"):
            continue
        fm = REPORT_FILE_PATTERN.match(f.name)
        if not fm:
            continue
        model, task = fm.groups()
        if model in KNOWN_MODELS and task in TASKS:
            if model not in data["models"]:
                data["models"][model] = {}
            data["models"][model][task] = f.read_text(encoding="utf-8")

    return data


def find_report_dirs():
    dirs = []
    if not REPORTS_DIR.exists():
        return dirs
    for entry in sorted(REPORTS_DIR.iterdir()):
        if entry.is_dir() and REPORT_DIR_PATTERN.match(entry.name):
            dirs.append(entry)
    return dirs


def rewrite_image_paths(md_text: str) -> str:
    return re.sub(
        r'(!\[[^\]]*\])\(/images/',
        r'\1(/static/images/',
        md_text,
    )


def render_md(md_text: str) -> str:
    md_text = rewrite_image_paths(md_text)
    return markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "codehilite", "toc"],
        extension_configs={"codehilite": {"css_class": "codehilite", "guess_lang": False}},
    )


PYGMENTS_CSS = HtmlFormatter(style="github-dark").get_style_defs(".codehilite")


def build_index_page():
    report_dirs = find_report_dirs()
    rows = []
    for report_dir in sorted(report_dirs, reverse=True):
        m = REPORT_DIR_PATTERN.match(report_dir.name)
        if not m:
            continue
        date, order_id, post_name = m.groups()
        display_date = f"{date[:4]}-{date[4:6]}-{date[6:]}"
        display_name = post_name.replace("_", " ").title()

        data = scan_single_report(report_dir)
        model_list = sorted(data["models"].keys())
        models_str = ", ".join(m.capitalize() for m in model_list) if model_list else "—"
        task_set = set()
        for m_tasks in data["models"].values():
            task_set.update(m_tasks.keys())
        tasks_str = ", ".join(TASK_LABELS.get(t, t) for t in TASKS if t in task_set) if task_set else "—"
        synth_str = "Yes" if data["synthesis"] else "No"

        link = f"/report/{report_dir.name}"
        rows.append(
            f"<tr>"
            f'<td><a href="{link}">{display_name}</a></td>'
            f"<td>{display_date}</td>"
            f"<td>#{order_id}</td>"
            f"<td>{models_str}</td>"
            f"<td>{tasks_str}</td>"
            f"<td>{synth_str}</td>"
            f"</tr>"
        )

    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Post Review Reports</title>
<style>
{INDEX_CSS}
</style>
</head>
<body>
<div class="page">
  <h1>Post Review Reports</h1>
  <table>
    <thead>
      <tr>
        <th>Post</th>
        <th>Date</th>
        <th>Run</th>
        <th>Models</th>
        <th>Tasks</th>
        <th>Synthesis</th>
      </tr>
    </thead>
    <tbody>
      {"".join(rows)}
    </tbody>
  </table>
</div>
</body>
</html>"""


def build_report_page(report_dir: pathlib.Path):
    data = scan_single_report(report_dir)
    m = REPORT_DIR_PATTERN.match(report_dir.name)
    date, order_id, post_name = m.groups()
    display_date = f"{date[:4]}-{date[4:6]}-{date[6:]}"
    display_name = post_name.replace("_", " ").title()

    models = data["models"]
    synthesis = data["synthesis"]
    model_list = sorted(models.keys())
    section_id = "report"

    task_tabs_html = []
    task_panels_html = []
    tab_index = 0

    if synthesis:
        synth_tab_id = f"{section_id}-synthesis"
        task_tabs_html.append(
            f'<button class="tab-btn task-tab synthesis-tab active" '
            f'data-target="{synth_tab_id}" data-group="{section_id}-tasks">'
            f"Synthesis</button>"
        )
        rendered_synth = render_md(synthesis)
        task_panels_html.append(
            f'<div class="tab-panel task-panel active" id="{synth_tab_id}">'
            f'<div class="synthesis-content">{rendered_synth}</div>'
            f"</div>"
        )
        tab_index = 1

    for ti, task in enumerate(TASKS):
        if not any(task in models.get(m, {}) for m in model_list):
            continue

        task_tab_id = f"{section_id}-{task}"
        active_cls = " active" if (tab_index == 0 and ti == 0) else ""
        task_tabs_html.append(
            f'<button class="tab-btn task-tab{active_cls}" '
            f'data-target="{task_tab_id}" data-group="{section_id}-tasks">'
            f"{TASK_LABELS[task]}</button>"
        )

        model_tabs_html = []
        model_panels_html = []
        first_model = True

        for model in model_list:
            if task not in models.get(model, {}):
                continue
            model_tab_id = f"{task_tab_id}-{model}"
            model_active = " active" if first_model else ""
            first_model = False
            model_tabs_html.append(
                f'<button class="tab-btn model-tab{model_active}" '
                f'data-target="{model_tab_id}" data-group="{task_tab_id}-models">'
                f"{model.capitalize()}</button>"
            )
            rendered = render_md(models[model][task])
            model_panels_html.append(
                f'<div class="tab-panel model-panel{model_active}" id="{model_tab_id}">'
                f"{rendered}</div>"
            )

        task_panels_html.append(
            f'<div class="tab-panel task-panel{active_cls}" id="{task_tab_id}">'
            f'<div class="tab-bar model-bar">{"".join(model_tabs_html)}</div>'
            f'<div class="model-panels">{"".join(model_panels_html)}</div>'
            f"</div>"
        )

    interactive_link = f"/report/{report_dir.name}/interactive"

    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{display_date} — {display_name} #{order_id}</title>
<style>
{REPORT_CSS}
{PYGMENTS_CSS}
</style>
</head>
<body>
<div class="page">
  <header>
    <a class="back-link" href="/">← All Reports</a>
    <a class="interactive-link" href="{interactive_link}">Interactive View →</a>
    <h1>{display_date} — {display_name} <span class="order-id">#{order_id}</span></h1>
  </header>
  <main>
    <div class="tab-bar task-bar">{"".join(task_tabs_html)}</div>
    <div class="task-panels">{"".join(task_panels_html)}</div>
  </main>
</div>
<script>
{JS}
</script>
</body>
</html>"""


def _strip_frontmatter(text: str) -> str:
    """Remove YAML frontmatter (--- ... ---) from markdown text."""
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return text[end + 3:].lstrip("\n")
    return text


def load_interactive_data(report_dir: pathlib.Path) -> dict:
    """Load all data needed for the interactive view."""
    m = REPORT_DIR_PATTERN.match(report_dir.name)
    _, _, post_basename = m.groups()

    # Prefer the annotated post (has <!-- ¶N --> markers for direct splitting)
    # Fall back to the original blog post if annotated version doesn't exist
    post_content = None
    annotated_path = report_dir / "_annotated.md"
    if annotated_path.exists():
        raw = annotated_path.read_text(encoding="utf-8")
        post_content = _strip_frontmatter(raw)
    else:
        candidates = sorted(CONTENT_DIR.glob(f"*{post_basename}.md"))
        if candidates:
            raw = candidates[0].read_text(encoding="utf-8")
            post_content = _strip_frontmatter(raw)

    # Read JSON sidecar files (may not exist yet)
    annotations = None
    ann_path = report_dir / "_annotations.json"
    if ann_path.exists():
        annotations = json.loads(ann_path.read_text(encoding="utf-8"))

    summary = None
    sum_path = report_dir / "_summary.json"
    if sum_path.exists():
        summary = json.loads(sum_path.read_text(encoding="utf-8"))

    id_map = None
    map_path = report_dir / "_id_map.json"
    if map_path.exists():
        id_map = json.loads(map_path.read_text(encoding="utf-8"))

    return {
        "post_content": post_content,
        "annotations": annotations,
        "summary": summary,
        "id_map": id_map,
    }


def _split_by_markers(post_content: str) -> list[tuple[str, str]]:
    """Split post content by <!-- ¶N --> markers.

    Returns list of (paragraph_id, markdown_chunk) tuples.
    Paragraphs without a marker get id "ungrouped-N".
    """
    marker_re = re.compile(r"<!--\s*¶(\S+)\s*-->")
    parts = marker_re.split(post_content)

    result = []
    ungrouped_idx = 0

    # parts[0] is text before first marker (if any)
    if parts[0].strip():
        result.append((f"ungrouped-{ungrouped_idx}", parts[0]))
        ungrouped_idx += 1

    # After that, pairs of (id, content)
    for i in range(1, len(parts), 2):
        pid = parts[i]
        content = parts[i + 1] if i + 1 < len(parts) else ""
        if content.strip():
            result.append((f"\u00b6{pid}", content))

    return result


def _split_by_id_map(post_content: str, id_map: dict) -> list[tuple[str, str]]:
    """Split post content using _id_map.json line ranges."""
    lines = post_content.split("\n")
    # id_map values: {"start_line": N, "end_line": M} (1-indexed)
    entries = []
    for pid, info in sorted(id_map.items(), key=lambda x: x[1].get("start_line", 0)):
        start = info.get("start_line", 1) - 1  # convert to 0-indexed
        end = info.get("end_line", len(lines))
        chunk = "\n".join(lines[start:end])
        if chunk.strip():
            entries.append((pid, chunk))
    return entries


def _split_by_blanks(post_content: str) -> list[tuple[str, str]]:
    """Fallback: split into logical blocks by double newlines."""
    blocks = re.split(r"\n{2,}", post_content)
    result = []
    for i, block in enumerate(blocks):
        if block.strip():
            result.append((f"block-{i}", block))
    return result


def render_post_interactive(
    post_content: str,
    id_map: dict | None,
    summary: dict | None,
) -> str:
    """Render the post with colored paragraph blocks for the left panel."""
    # Determine splitting strategy
    if "<!-- \u00b6" in post_content:
        blocks = _split_by_markers(post_content)
    elif id_map:
        blocks = _split_by_id_map(post_content, id_map)
    else:
        blocks = _split_by_blanks(post_content)

    html_parts = []
    for pid, md_chunk in blocks:
        action = ""
        if summary and pid in summary:
            action = summary[pid].get("top_action", "") or ""

        rendered = render_md(md_chunk)
        safe_id = pid.replace("\u00b6", "p").replace("-", "_")
        html_parts.append(
            f'<div class="para" id="{safe_id}" data-action="{action}" data-pid="{pid}">'
            f'<span class="pid-badge">{pid}</span>'
            f"{rendered}"
            f"</div>"
        )

    return "\n".join(html_parts)


def build_interactive_page(report_dir: pathlib.Path) -> str:
    """Build the two-panel interactive review page."""
    data = load_interactive_data(report_dir)
    m = REPORT_DIR_PATTERN.match(report_dir.name)
    date, order_id, post_name = m.groups()
    display_date = f"{date[:4]}-{date[4:6]}-{date[6:]}"
    display_name = post_name.replace("_", " ").title()

    has_annotations = data["annotations"] is not None and data["summary"] is not None

    # Build left panel content
    if data["post_content"]:
        left_html = render_post_interactive(
            data["post_content"], data["id_map"], data["summary"]
        )
    else:
        left_html = (
            '<div class="no-post-msg">'
            "Could not find the original blog post for this report."
            "</div>"
        )

    # Build annotation data for JS
    annotations_json = json.dumps(
        data["annotations"] or {}, ensure_ascii=False
    )

    # Build right panel placeholder
    if has_annotations:
        right_html = (
            '<div class="filter-controls">'
            '  <div class="filter-group">'
            '    <span class="filter-label">Dimensions:</span>'
            '    <label><input type="checkbox" class="dim-filter" value="ai_slop" checked> AI Slop</label>'
            '    <label><input type="checkbox" class="dim-filter" value="arrangement" checked> Arrangement</label>'
            '    <label><input type="checkbox" class="dim-filter" value="tone" checked> Tone</label>'
            '    <label><input type="checkbox" class="dim-filter" value="title" checked> Title</label>'
            '    <label><input type="checkbox" class="dim-filter" value="synthesis" checked> Synthesis</label>'
            "  </div>"
            '  <div class="filter-group">'
            '    <span class="filter-label">Min score:</span>'
            '    <input type="range" id="severity-slider" min="0" max="10" value="0" step="1">'
            '    <span id="severity-value">0</span>'
            "  </div>"
            "</div>"
            '<div id="annotation-panel">'
            '<div class="annotation-placeholder">Click a paragraph on the left to view annotations.</div>'
            "</div>"
        )
    else:
        right_html = (
            '<div class="no-annotations-msg">'
            "<p>No annotations found.</p>"
            "<p>Run the review pipeline with updated templates to generate "
            "interactive annotations (<code>_annotations.json</code> and "
            "<code>_summary.json</code>).</p>"
            "</div>"
        )

    tabbed_link = f"/report/{report_dir.name}"

    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Interactive Review — {display_date} — {display_name} #{order_id}</title>
<style>
{INTERACTIVE_CSS}
{PYGMENTS_CSS}
</style>
</head>
<body>
<div class="top-header">
  <div class="header-left">
    <a class="back-link" href="{tabbed_link}">&larr; Report</a>
    <h1>{display_date} &mdash; {display_name} <span class="order-id">#{order_id}</span></h1>
  </div>
  <div class="header-right">
    <a class="view-link" href="{tabbed_link}">Tabbed View</a>
  </div>
</div>
<div class="two-panel">
  <div class="left-panel">
    {left_html}
  </div>
  <div class="right-panel">
    {right_html}
  </div>
</div>
<script>
const ANNOTATIONS = {annotations_json};
{INTERACTIVE_JS}
</script>
</body>
</html>"""


INDEX_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #0d1117; color: #c9d1d9; line-height: 1.6;
}
.page { max-width: 1100px; margin: 0 auto; padding: 32px 48px; }
h1 {
  font-size: 22px; color: #f0f6fc; margin-bottom: 24px;
  padding-bottom: 16px; border-bottom: 1px solid #30363d;
}
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th, td { padding: 10px 14px; border: 1px solid #30363d; text-align: left; }
th { background: #161b22; color: #f0f6fc; font-weight: 600; }
tr:nth-child(even) { background: rgba(22, 27, 34, 0.5); }
tr:hover { background: #1f2937; }
a { color: #58a6ff; text-decoration: none; font-weight: 500; }
a:hover { text-decoration: underline; }
"""

REPORT_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #0d1117; color: #c9d1d9; line-height: 1.6;
}
.page { max-width: 1100px; margin: 0 auto; padding: 32px 48px; }
.back-link {
  color: #58a6ff; text-decoration: none; font-size: 14px;
  display: inline-block; margin-bottom: 12px;
}
.back-link:hover { text-decoration: underline; }
.interactive-link {
  color: #58a6ff; text-decoration: none; font-size: 14px;
  float: right; margin-top: 2px;
}
.interactive-link:hover { text-decoration: underline; }
header h1 {
  font-size: 22px; color: #f0f6fc; margin-bottom: 24px;
  padding-bottom: 16px; border-bottom: 1px solid #30363d;
}
.order-id { font-size: 14px; color: #6e7681; font-weight: normal; }

/* Tabs */
.tab-bar { display: flex; gap: 4px; border-bottom: 1px solid #30363d; }
.model-bar { margin-top: 8px; border-bottom: 1px solid #21262d; }
.tab-btn {
  padding: 8px 16px; border: none; background: transparent; color: #8b949e;
  cursor: pointer; font-size: 14px; border-bottom: 2px solid transparent;
  transition: all 0.15s;
}
.tab-btn:hover { color: #c9d1d9; }
.tab-btn.active { color: #f0f6fc; border-bottom-color: #58a6ff; }
.model-tab.active { border-bottom-color: #3fb950; }
.synthesis-tab { font-weight: 600; }
.synthesis-tab.active { border-bottom-color: #f0883e; }
.tab-panel { display: none; }
.tab-panel.active { display: block; }
.task-panel { padding-top: 8px; }
.model-panel { padding: 20px 0; }

/* Markdown content */
.synthesis-content h1, .synthesis-content h2, .synthesis-content h3, .synthesis-content h4,
.model-panel h1, .model-panel h2, .model-panel h3, .model-panel h4 {
  color: #f0f6fc; margin-top: 24px; margin-bottom: 12px;
}
.synthesis-content h1, .model-panel h1 { font-size: 20px; }
.synthesis-content h2, .model-panel h2 { font-size: 18px; }
.synthesis-content h3, .model-panel h3 { font-size: 16px; }
.synthesis-content p, .model-panel p { margin-bottom: 12px; }
.synthesis-content table, .model-panel table {
  width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 13px;
}
.synthesis-content th, .synthesis-content td,
.model-panel th, .model-panel td {
  padding: 8px 12px; border: 1px solid #30363d; text-align: left;
}
.synthesis-content th, .model-panel th {
  background: #161b22; color: #f0f6fc; font-weight: 600;
}
.synthesis-content tr:nth-child(even), .model-panel tr:nth-child(even) {
  background: rgba(22, 27, 34, 0.5);
}
.synthesis-content ul, .synthesis-content ol,
.model-panel ul, .model-panel ol { margin: 12px 0; padding-left: 24px; }
.synthesis-content li, .model-panel li { margin-bottom: 6px; }
.synthesis-content code, .model-panel code {
  background: #161b22; padding: 2px 6px; border-radius: 4px; font-size: 13px;
}
.synthesis-content pre, .model-panel pre {
  background: #161b22; padding: 16px; border-radius: 8px;
  overflow-x: auto; margin: 12px 0;
}
.synthesis-content pre code, .model-panel pre code { padding: 0; background: none; }
.synthesis-content blockquote, .model-panel blockquote {
  border-left: 3px solid #30363d; padding-left: 16px; color: #8b949e; margin: 12px 0;
}
.synthesis-content blockquote { border-left-color: #f0883e; }
.synthesis-content hr, .model-panel hr {
  border: none; border-top: 1px solid #30363d; margin: 24px 0;
}
.synthesis-content strong, .model-panel strong { color: #f0f6fc; }
.synthesis-content img, .model-panel img {
  max-width: 100%; height: auto; border-radius: 8px; margin: 12px 0;
}
.synthesis-content { padding: 20px 0; }
@media (max-width: 768px) { .page { padding: 16px; } }
"""

JS = """
document.addEventListener('click', function(e) {
  if (!e.target.classList.contains('tab-btn')) return;
  var target = e.target.dataset.target;
  var group = e.target.dataset.group;
  document.querySelectorAll('[data-group="' + group + '"]').forEach(function(btn) {
    btn.classList.remove('active');
  });
  e.target.classList.add('active');
  var parent = e.target.closest('.tab-bar').parentElement;
  var panelClass = e.target.classList.contains('task-tab') ? 'task-panel' : 'model-panel';
  parent.querySelectorAll(':scope > .task-panels > .' + panelClass +
    ', :scope > .model-panels > .' + panelClass).forEach(function(panel) {
    panel.classList.remove('active');
  });
  document.getElementById(target).classList.add('active');
});
"""


INTERACTIVE_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #0d1117; color: #c9d1d9; line-height: 1.6;
  overflow: hidden; height: 100vh;
}

/* Header */
.top-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 24px; border-bottom: 1px solid #30363d;
  background: #161b22;
}
.header-left { display: flex; align-items: center; gap: 16px; }
.header-left h1 { font-size: 18px; color: #f0f6fc; margin: 0; }
.order-id { font-size: 13px; color: #6e7681; font-weight: normal; }
.back-link, .view-link {
  color: #58a6ff; text-decoration: none; font-size: 13px; white-space: nowrap;
}
.back-link:hover, .view-link:hover { text-decoration: underline; }

/* Two-panel layout */
.two-panel {
  display: grid; grid-template-columns: 55% 45%;
  height: calc(100vh - 53px); /* subtract header */
}
.left-panel {
  overflow-y: auto; padding: 24px 32px;
  border-right: 1px solid #30363d;
}
.right-panel {
  overflow-y: auto; padding: 20px 24px;
  position: sticky; top: 0;
}

/* Paragraph blocks */
.para {
  position: relative; padding: 12px 16px; margin-bottom: 8px;
  border-radius: 6px; border-left: 3px solid transparent;
  cursor: pointer; transition: all 0.15s;
}
.para:hover { background: rgba(88, 166, 255, 0.04); }
.para[data-action="rewrite"]  { border-left: 3px solid #f85149; background: rgba(248,81,73,0.05); }
.para[data-action="move"]     { border-left: 3px solid #d29922; background: rgba(210,153,34,0.05); }
.para[data-action="merge"],
.para[data-action="split"]    { border-left: 3px solid #a371f7; background: rgba(163,113,247,0.05); }
.para[data-action="remove"]   { border-left: 3px solid #484f58; background: rgba(72,79,88,0.1); }
.para[data-action="minor"]    { border-left: 3px solid #58a6ff; background: rgba(88,166,255,0.05); }
.para.active                  { outline: 2px solid #58a6ff; outline-offset: 2px; }

/* ¶ badge */
.pid-badge {
  position: absolute; top: 6px; right: 8px;
  font-size: 11px; color: #484f58; font-family: monospace;
  user-select: none; pointer-events: none;
}

/* Markdown inside paragraphs */
.para h1, .para h2, .para h3, .para h4 { color: #f0f6fc; margin-top: 16px; margin-bottom: 8px; }
.para h1 { font-size: 20px; } .para h2 { font-size: 18px; } .para h3 { font-size: 16px; }
.para p { margin-bottom: 10px; }
.para table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 13px; }
.para th, .para td { padding: 8px 12px; border: 1px solid #30363d; text-align: left; }
.para th { background: #161b22; color: #f0f6fc; font-weight: 600; }
.para tr:nth-child(even) { background: rgba(22, 27, 34, 0.5); }
.para ul, .para ol { margin: 10px 0; padding-left: 24px; }
.para li { margin-bottom: 4px; }
.para code { background: #161b22; padding: 2px 6px; border-radius: 4px; font-size: 13px; }
.para pre { background: #161b22; padding: 16px; border-radius: 8px; overflow-x: auto; margin: 10px 0; }
.para pre code { padding: 0; background: none; }
.para blockquote { border-left: 3px solid #30363d; padding-left: 16px; color: #8b949e; margin: 10px 0; }
.para hr { border: none; border-top: 1px solid #30363d; margin: 20px 0; }
.para strong { color: #f0f6fc; }
.para img { max-width: 100%; height: auto; border-radius: 8px; margin: 10px 0; }

/* Filter controls */
.filter-controls {
  margin-bottom: 16px; padding: 12px 16px;
  background: #161b22; border-radius: 8px; border: 1px solid #30363d;
}
.filter-group {
  display: flex; align-items: center; gap: 10px;
  flex-wrap: wrap; margin-bottom: 8px;
}
.filter-group:last-child { margin-bottom: 0; }
.filter-label { font-size: 12px; color: #8b949e; font-weight: 600; min-width: 80px; }
.filter-group label {
  font-size: 12px; color: #c9d1d9; cursor: pointer;
  display: flex; align-items: center; gap: 4px;
}
.filter-group input[type="checkbox"] { accent-color: #58a6ff; }
.filter-group input[type="range"] { width: 120px; accent-color: #58a6ff; }
#severity-value { font-size: 12px; color: #8b949e; min-width: 16px; }

/* Annotation panel */
#annotation-panel { }
.annotation-placeholder, .no-annotations-msg, .no-post-msg {
  color: #6e7681; font-size: 14px; padding: 32px 16px; text-align: center;
}
.no-annotations-msg code {
  background: #161b22; padding: 2px 6px; border-radius: 4px; font-size: 13px;
}

/* Annotation cards */
.ann-card {
  background: #161b22; border: 1px solid #30363d; border-radius: 8px;
  padding: 14px 16px; margin-bottom: 10px;
}
.ann-card-header {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  margin-bottom: 8px;
}
.dim-badge {
  font-size: 11px; font-weight: 600; padding: 2px 8px;
  border-radius: 12px; text-transform: uppercase; letter-spacing: 0.5px;
}
.dim-badge[data-dim="ai_slop"]      { background: rgba(248,81,73,0.15); color: #f85149; }
.dim-badge[data-dim="arrangement"]   { background: rgba(210,153,34,0.15); color: #d29922; }
.dim-badge[data-dim="tone"]          { background: rgba(163,113,247,0.15); color: #a371f7; }
.dim-badge[data-dim="title"]         { background: rgba(88,166,255,0.15); color: #58a6ff; }
.dim-badge[data-dim="synthesis"]     { background: rgba(240,136,62,0.15); color: #f0883e; }

.score-badge {
  font-size: 11px; font-weight: 600; padding: 2px 8px;
  border-radius: 12px; background: rgba(139,148,158,0.15); color: #8b949e;
}
.action-tag {
  font-size: 11px; font-weight: 500; padding: 2px 8px;
  border-radius: 4px; background: #21262d; color: #c9d1d9;
}
.source-label {
  font-size: 11px; color: #484f58; margin-left: auto;
}
.ann-issue { font-size: 13px; color: #c9d1d9; line-height: 1.5; }
.ann-suggestion-toggle {
  font-size: 12px; color: #58a6ff; cursor: pointer;
  margin-top: 8px; user-select: none; display: flex; align-items: center; gap: 4px;
}
.ann-suggestion-toggle:hover { text-decoration: underline; }
.ann-suggestion-toggle .chevron {
  display: inline-block; transition: transform 0.2s; font-size: 10px;
}
.ann-suggestion-toggle.open .chevron { transform: rotate(90deg); }
.ann-suggestion-body {
  max-height: 0; overflow: hidden; transition: max-height 0.3s ease;
  font-size: 13px; color: #8b949e; line-height: 1.5;
}
.ann-suggestion-body.open { max-height: 500px; padding-top: 8px; }

/* Responsive */
@media (max-width: 900px) {
  .two-panel { grid-template-columns: 1fr; height: auto; }
  body { overflow: auto; }
  .left-panel { border-right: none; border-bottom: 1px solid #30363d; }
  .right-panel { position: static; }
  .top-header { flex-direction: column; gap: 8px; align-items: flex-start; }
}
"""

INTERACTIVE_JS = """
// Click handler for paragraphs
document.querySelectorAll('.para').forEach(function(el) {
  el.addEventListener('click', function() {
    document.querySelectorAll('.para.active').forEach(function(p) {
      p.classList.remove('active');
    });
    el.classList.add('active');
    renderAnnotations(el.dataset.pid);
  });
});

// Render annotations in right panel
function renderAnnotations(pid) {
  var panel = document.getElementById('annotation-panel');
  if (!panel) return;

  var entries = ANNOTATIONS[pid];
  if (!entries || entries.length === 0) {
    panel.innerHTML = '<div class="annotation-placeholder">No annotations for ' + pid + '</div>';
    return;
  }

  // Get active filters
  var activeCats = getActiveCategorySet();
  var minScore = getMinScore();

  // Filter entries
  var filtered = entries.filter(function(e) {
    if (!dimPassesFilter(e.dimension, activeCats)) return false;
    if (e.score !== undefined && e.score < minScore) return false;
    return true;
  });

  if (filtered.length === 0) {
    panel.innerHTML = '<div class="annotation-placeholder">No annotations match current filters for ' + pid + '</div>';
    return;
  }

  // Group by dimension
  var groups = {};
  filtered.forEach(function(e) {
    if (!groups[e.dimension]) groups[e.dimension] = [];
    groups[e.dimension].push(e);
  });

  var html = '';
  Object.keys(groups).sort().forEach(function(dim) {
    groups[dim].forEach(function(e, i) {
      var cardId = pid + '-' + dim + '-' + i;
      html += '<div class="ann-card">';
      html += '<div class="ann-card-header">';
      html += '<span class="dim-badge" data-dim="' + dimCategory(dim) + '">' + dim.replace(/_/g, ' ') + '</span>';
      if (e.score !== undefined) {
        html += '<span class="score-badge">' + e.score + '/10</span>';
      }
      if (e.action) {
        html += '<span class="action-tag">' + e.action + '</span>';
      }
      html += '<span class="source-label">' + (e.source || '') + '</span>';
      html += '</div>';
      html += '<div class="ann-issue">' + escapeHtml(e.issue) + '</div>';
      if (e.suggestion) {
        html += '<div class="ann-suggestion-toggle" onclick="toggleSuggestion(this)" data-target="' + cardId + '">';
        html += '<span class="chevron">&#9654;</span> Show suggestion';
        html += '</div>';
        html += '<div class="ann-suggestion-body" id="sug-' + cardId + '">' + escapeHtml(e.suggestion) + '</div>';
      }
      html += '</div>';
    });
  });

  panel.innerHTML = html;
}

function toggleSuggestion(toggleEl) {
  var target = document.getElementById('sug-' + toggleEl.dataset.target);
  if (!target) return;
  var isOpen = target.classList.contains('open');
  target.classList.toggle('open');
  toggleEl.classList.toggle('open');
  if (isOpen) {
    toggleEl.innerHTML = '<span class="chevron">&#9654;</span> Show suggestion';
  } else {
    toggleEl.innerHTML = '<span class="chevron">&#9654;</span> Hide suggestion';
  }
}

function escapeHtml(text) {
  var div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Dimension category mapping
var AI_SLOP_DIMS = new Set(['density','monotony','template','cliche','hedging','emotion','thoroughness','overload','coherence']);

function dimCategory(dim) {
  if (AI_SLOP_DIMS.has(dim)) return 'ai_slop';
  if (dim.startsWith('tone')) return 'tone';
  if (dim.startsWith('synthesis')) return 'synthesis';
  if (dim === 'title') return 'title';
  if (dim === 'arrangement') return 'arrangement';
  return dim; // fallback to raw dimension
}

// Filter helpers
function getActiveCategorySet() {
  var checks = document.querySelectorAll('.dim-filter');
  var active = new Set();
  checks.forEach(function(cb) {
    if (cb.checked) active.add(cb.value);
  });
  if (checks.length === 0) return new Set(['ai_slop','arrangement','tone','title','synthesis']);
  return active;
}

function dimPassesFilter(dim, activeCats) {
  return activeCats.has(dimCategory(dim));
}

function getMinScore() {
  var slider = document.getElementById('severity-slider');
  return slider ? parseInt(slider.value, 10) : 0;
}

// Filter change handlers
document.querySelectorAll('.dim-filter').forEach(function(cb) {
  cb.addEventListener('change', function() {
    applyFilters();
    refreshActiveAnnotation();
  });
});

var severitySlider = document.getElementById('severity-slider');
if (severitySlider) {
  severitySlider.addEventListener('input', function() {
    document.getElementById('severity-value').textContent = this.value;
    applyFilters();
    refreshActiveAnnotation();
  });
}

function refreshActiveAnnotation() {
  var active = document.querySelector('.para.active');
  if (active) renderAnnotations(active.dataset.pid);
}

function applyFilters() {
  var activeCats = getActiveCategorySet();
  var minScore = getMinScore();

  document.querySelectorAll('.para').forEach(function(el) {
    var pid = el.dataset.pid;
    var entries = ANNOTATIONS[pid];
    if (!entries) return;

    // Check if any annotation passes filter
    var hasVisible = entries.some(function(e) {
      if (!dimPassesFilter(e.dimension, activeCats)) return false;
      if (e.score !== undefined && e.score < minScore) return false;
      return true;
    });

    // Dim paragraphs with no visible annotations (but don't hide them)
    el.style.opacity = hasVisible ? '1' : '0.4';
  });
}

// Scroll-spy with IntersectionObserver
var observer = new IntersectionObserver(function(entries) {
  entries.forEach(function(entry) {
    if (entry.isIntersecting && !document.querySelector('.para.active')) {
      // Only auto-highlight when no paragraph is manually selected
      entry.target.style.boxShadow = 'inset 0 0 0 1px rgba(88,166,255,0.2)';
    } else {
      if (!entry.target.classList.contains('active')) {
        entry.target.style.boxShadow = 'none';
      }
    }
  });
}, {
  root: document.querySelector('.left-panel'),
  threshold: 0.3
});

document.querySelectorAll('.para').forEach(function(el) {
  observer.observe(el);
});

// Initial filter application
applyFilters();
"""


class ReportHandler(http.server.BaseHTTPRequestHandler):
    """Dynamic handler that renders reports on each request."""

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path.rstrip("/")

        # Index page
        if path == "" or path == "/":
            self._send_html(build_index_page())
            return

        # Interactive page: /report/<folder_name>/interactive
        if path.startswith("/report/") and path.endswith("/interactive"):
            folder_name = path[len("/report/"):-len("/interactive")]
            report_dir = REPORTS_DIR / folder_name
            if report_dir.is_dir() and REPORT_DIR_PATTERN.match(folder_name):
                self._send_html(build_interactive_page(report_dir))
                return
            self._send_404()
            return

        # Report page: /report/<folder_name>
        if path.startswith("/report/"):
            folder_name = path[len("/report/"):]
            report_dir = REPORTS_DIR / folder_name
            if report_dir.is_dir() and REPORT_DIR_PATTERN.match(folder_name):
                self._send_html(build_report_page(report_dir))
                return
            self._send_404()
            return

        # Static files: /static/images/...
        if path.startswith("/static/"):
            file_path = PROJECT_ROOT / path.lstrip("/")
            if file_path.is_file():
                self._send_file(file_path)
                return
            self._send_404()
            return

        self._send_404()

    def _send_html(self, html: str):
        data = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_file(self, file_path: pathlib.Path):
        ext = file_path.suffix.lower()
        content_types = {
            ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".gif": "image/gif", ".svg": "image/svg+xml", ".webp": "image/webp",
            ".css": "text/css", ".js": "application/javascript",
        }
        content_type = content_types.get(ext, "application/octet-stream")
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_404(self):
        self.send_response(404)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        pass  # suppress request logs


def main():
    parser = argparse.ArgumentParser(description="Serve LLM review reports dynamically")
    parser.add_argument("--port", type=int, default=8899, help="Server port (default: 8899)")
    args = parser.parse_args()

    if not REPORTS_DIR.exists():
        print(f"Reports directory not found: {REPORTS_DIR}", file=sys.stderr)
        sys.exit(1)

    report_count = len(find_report_dirs())
    print(f"Found {report_count} report(s) in {REPORTS_DIR}")
    print(f"Serving at http://localhost:{args.port}")
    print("Press Ctrl+C to stop.\n")

    with socketserver.TCPServer(("", args.port), ReportHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
