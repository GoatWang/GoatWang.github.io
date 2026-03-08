# report_renderer — LLM Review Report Viewer

Dynamic server that renders LLM review reports from `reports/` on the fly. No generated files — reads markdown directly and serves HTML.

## Setup

```bash
cd tool_scripts/report_renderer
uv sync  # installs markdown + pygments
```

## Usage

```bash
cd tool_scripts/report_renderer && uv run render.py
```

Open http://localhost:8899

### Routes

| URL | Page |
|-----|------|
| `/` | Index — lists all report folders, click to view |
| `/report/<folder>` | Report page with tabbed view |
| `/static/images/...` | Blog post images |

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--port` | `8899` | Server port |

## Features

- No build step — renders markdown to HTML on each request
- Index page to pick which report to view
- Synthesis tab shown first (orange accent) when available
- Two-level tabs: Task (Title / Tone / Arrangement / AI Slop) → Model (Claude / Gemini / Grok)
- Only shows tabs for tasks that have reports
- Blog post images rendered correctly via `/static/images/`
- Dark GitHub-style theme
