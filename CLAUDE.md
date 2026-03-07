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

Run scripts with inline dependencies using `uv run --with`:

```bash
uv run --with Pillow tool_scripts/gen_favicon/gen_favicon.py static/images/avatar.jpeg
uv run --with some-package prompts/20260307_0_one_time_task.py
```

Available tools (see each tool's `README.md` for details):

- `tool_scripts/to_gif/` — Convert video to GIF (requires ffmpeg)
- `tool_scripts/gen_favicon/` — Generate favicon files from an image (requires Pillow)

## Service Selection Standards

When evaluating or recommending third-party services for this project, apply these principles in order:

1. **Data ownership** — All data must be retainable on our own server or in the repo. Never lock subscriber lists, content, or config into a platform that can't be fully exported or API-accessed.
2. **API-first** — Every service must be fully controllable via API so Claude Code or other agents can manage it programmatically. Avoid services that require manual UI configuration for core operations.
3. **Source in repo** — All configuration, templates, and branding assets (favicon, name, descriptions, email templates) must live in the Git repo as source of truth. The service should consume these, not host its own copies.
4. **No unnecessary uploads** — Do not upload branding, images, or metadata to third-party dashboards. If a service requires it, prefer a self-hosted alternative.
5. **Self-hosted preferred** — When a reliable open-source self-hosted option exists (e.g., Listmonk for newsletters, Umami for analytics), prefer it over SaaS. We have a Mac Mini server with a fixed IP available for hosting.
6. **SaaS for deliverability/infra only** — Use managed services only for hard infrastructure problems (email deliverability, CDN, DNS) where self-hosting is impractical. Example: use Resend as SMTP relay, but manage subscriber data ourselves.

### Current service decisions

| Need | Service | Why |
|------|---------|-----|
| Email delivery | Resend (SMTP relay) | Free tier 3K/month, full API, high deliverability |
| Subscriber management | TBD (Listmonk or Resend Audiences) | Evaluating self-hosted vs managed |
| Static hosting | GitHub Pages | Free, deploys from repo |
| Analytics | Google Analytics | Already configured |

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
