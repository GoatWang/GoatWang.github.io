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


class ReportHandler(http.server.BaseHTTPRequestHandler):
    """Dynamic handler that renders reports on each request."""

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path.rstrip("/")

        # Index page
        if path == "" or path == "/":
            self._send_html(build_index_page())
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
