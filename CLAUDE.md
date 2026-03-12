# CLAUDE.md - Project Instructions

## File Naming Convention for `prompts/` Folder

When creating ANY files in the `prompts/` folder (including .py, .md, .yaml, .json, etc.), use the naming convention `YYYYMMDD_ID_description.extension` where:

- `YYYYMMDD` is the current date (e.g., 20250929)
- `ID` is a sequential number starting from 0 for each day (0, 1, 2, ...)
- `description` is a brief task description using underscores
- `extension` is the appropriate file extension (.py, .md, .yaml, .json, etc.)

### Auto-determining the ID

Before creating a file, scan the `prompts/` folder for files with today's date prefix using:

```bash
ls prompts/ | grep "^YYYYMMDD" | cut -d'_' -f2 | sort -n | tail -1
```

Then use (max_id + 1) as the new ID. If no files exist for today, start with 0.

### Examples

- `prompts/20250929_0_grok4_comedy_search.py`
- `prompts/20250926_0_rate_comedy_materials_plan.md`
- `prompts/20250929_1_title_generation_template.yaml`

## Temporary & Intermediate Files

All temporary files generated during work should be placed in the `prompts/` folder using the same naming convention above. This includes:

- Screenshots and design mockups
- Design docs and planning notes
- Experiment scripts and results
- Investigation intermediate files
- Any other throwaway/working files

The `prompts/` folder is gitignored, so these files won't be committed to the repository.

## Python Scripts & Dependencies

Use `uv` to run any Python scripts. **Never install packages globally with `pip`.**

- **Reusable tools** go in `tool_scripts/<tool_name>/` — each tool gets its own folder with a `README.md`
- **One-time scripts** go in `prompts/` using the date-based naming convention

### Reusable tools (`tool_scripts/`)

Each tool folder is a `uv` project with its own `.venv`. To set up a new tool:

```bash
cd tool_scripts/<tool_name>
uv init
uv add <dependencies>
```

Run tools using their local venv Python:

```bash
tool_scripts/<tool_name>/.venv/bin/python tool_scripts/<tool_name>/<script>.py [args]
```

### One-time scripts (`prompts/`)

Run one-time scripts with inline dependencies using `uv run --with`:

```bash
uv run --with some-package prompts/20260307_0_one_time_task.py
```

### Available tools

See each tool's `README.md` for details:

- `tool_scripts/to_gif/` — Convert video to GIF (requires ffmpeg)
- `tool_scripts/gen_favicon/` — Generate favicon files from an image (requires Pillow)
- `tool_scripts/md2pdf/` — Convert Markdown to PDF (requires pango via Homebrew)

## Service Selection Standards

When evaluating or recommending third-party services for this project, apply these principles in order:

1. **API-first** — Every service must be fully controllable via API so Claude Code or other agents can manage it programmatically. Avoid services that require manual UI configuration for core operations. If the agent can't configure branding, templates, or settings via API, reject the service.
2. **Personal data in repo** — All personal configuration, templates, and branding assets (favicon, name, descriptions, email templates) must live in the Git repo as source of truth and be deployable via API. The agent must be able to update these without manual UI interaction.
3. **User data can be managed** — Subscriber data and other user-generated data can live on third-party services, as long as it's accessible and exportable via API. No hard lock-in.
4. **No manual uploads** — Do not upload branding, images, or metadata to third-party dashboards manually. If a service requires manual UI config that can't be done via API, prefer an alternative.
5. **Serverless for glue logic** — Use Cloudflare Workers or similar serverless platforms for small proxy/glue endpoints (e.g., subscribe form proxy). Avoid running custom servers on personal hardware for production blog features. Use SaaS for hard infra problems (email deliverability, CDN, DNS).

### Current service decisions

| Need | Service | Why |
|------|---------|-----|
| Email delivery | Resend (SMTP relay) | Free tier 3K/month, full API, high deliverability |
| Subscriber management | Resend Audiences | API-managed, free tier sufficient |
| Subscribe proxy | Cloudflare Worker | Serverless, hides API key from client |
| Static hosting | GitHub Pages | Free, deploys from repo |
| Analytics | Google Analytics | Already configured |

## VS Code Markdown Image Preview

Blog posts reference images with absolute paths like `/images/posts/...`, but images live in `static/images/`. VS Code can't resolve these paths for markdown preview. A symlink at the project root fixes this:

```bash
ln -s static/images images
```

This symlink is gitignored (see `.gitignore`). If the `images` symlink doesn't exist at the project root, create it before editing posts so VS Code preview renders images correctly.

## Shared Web Report Viewer

When the user requests a web report (HTML page for viewing analysis results, summaries, or any structured output), generate it and save to the shared web viewer.

### Server Info

- **Path:** `/Users/wanghsuanchung/web_server/`
- **Port:** 8801 (internal), 2222 (external)
- **Framework:** Django 5.1 (managed by `uv`)
- **Start:** `bash /Users/wanghsuanchung/web_server/start_server.sh`
- **Reports dir:** `/Users/wanghsuanchung/web_server/reports/GoatWang.github.io/`

### How to Generate a Report

1. Create an HTML file with mobile-friendly design (viewport meta, RWD CSS)
2. Save to `/Users/wanghsuanchung/web_server/reports/GoatWang.github.io/YYYYMMDD_HHMMSS_<type>.html`
   - Or directory-based: `YYYYMMDD_HHMMSS_<type>/index.html` (with optional `metadata.json` containing `{"title": "..."}`)
3. **Naming: timestamp FIRST** — e.g., `20260310_143000_newsletter_preview.html`
4. Read `/Users/wanghsuanchung/web_server/config.json` to build the URL:
   - `http://<fixed_ip>:<external_port>/reports/GoatWang.github.io/<slug>/`
5. Reply with a short summary + the report URL

### HTML Report Requirements

- `<meta name="viewport" content="width=device-width, initial-scale=1.0">`
- Tables wrapped for horizontal scroll: `style="display:block; overflow-x:auto;"`
- Font size >= 14px for body text
- Max-width container (e.g., 960px) with auto margins

### When to Generate a Report vs Plain Text

- **Report**: Multi-section analysis, tables, comparisons, structured data, anything > ~10 lines
- **Plain text**: Simple one-liner answers, short status updates

## GIF Generation for Blog Posts

Use `tool_scripts/to_gif/to_gif.py` to convert screen recordings to GIF:

```bash
python3 tool_scripts/to_gif/to_gif.py <input_video> <output_gif> --fps <fps> --width <width>
```

### Sizing for Retina displays

PaperMod's post content container is **720px** wide (`--main-width: 720px`). Images are constrained to `max-width: 100%` of this container. On Retina (2x) displays, a 720px-displayed image needs **1440px** intrinsic width to look sharp.

- **Always generate GIFs at 1440px wide** for blog post content (2x the 720px container).
- Safari uses a worse downscaling algorithm than Chrome for GIFs. If GIFs are not 2x, they will look blurry on Safari but fine on Chrome.

### Framerate vs file size tradeoff

Lower fps = smaller file. Current sweet spot: **3fps** at 1440px wide. This keeps file sizes manageable (~2MB for 25s, ~11MB for 80s) while still being readable.

### macOS screen recording filename issue

macOS uses Unicode narrow no-break space (U+202F) between time and AM/PM in screen recording filenames. The `to_gif.py` script handles this via glob fallback.
