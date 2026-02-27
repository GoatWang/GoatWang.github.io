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
