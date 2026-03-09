Review the blog post at $ARGUMENTS using the multi-LLM review pipeline.

## Instructions

The review pipeline sends specific tasks to each LLM based on their strengths (5 calls), then runs a synthesis step to produce a decision-ready summary with an interactive viewer.

### Step 1: Determine output directory

1. Extract the post basename from `$ARGUMENTS` (e.g., `content/posts/20260307_chardet_ai_clean_room.md` → `chardet_ai_clean_room`)
2. Get today's date as `YYYYMMDD`
3. Scan `reports/` for today's date prefix to determine the next available order ID
4. The output directory will be: `reports/YYYYMMDD_<id>_<post_basename>/`
5. All reports go into this single folder, with filenames: `<model>_<task>.md`

### Step 1.5: Pre-process the post with paragraph IDs

Inject `<!-- ¶N -->` markers into the post for paragraph-level annotation tracking:

```bash
cd tool_scripts/call_llm && uv run inject_paragraph_ids.py \
  <abs_post_path> \
  <abs_report_dir>/_annotated.md \
  --id-map <abs_report_dir>/_id_map.json
```

Use `_annotated.md` as the input for all subsequent LLM calls (not the original post).

### Step 2: Run the 5 review calls

Each call:

```bash
cd tool_scripts/call_llm && uv run call_llm.py <model> prompt_templates/<task>.md <abs_annotated_path> <abs_output_path>
```

Output file naming: `reports/YYYYMMDD_<id>_<post_basename>/<model>_<task>.md`

Task assignments per model:

| Model | Tasks | Output files |
|-------|-------|-------------|
| **claude** | `title`, `ai_slop` | `claude_title.md`, `claude_ai_slop.md` |
| **gemini** | `title`, `tone`, `arrangement` | `gemini_title.md`, `gemini_tone.md`, `gemini_arrangement.md` |

Run all 5 calls in parallel. Each call is independent.

**Important**: Use absolute paths for `<abs_annotated_path>` and `<abs_output_path>`.

### Step 2.5: Extract JSON annotations

After all 5 LLM calls complete, extract structured annotations from the reports:

```bash
cd tool_scripts/call_llm && uv run extract_annotations.py <abs_report_dir>
```

This produces:
- Per-file sidecar `.json` files (e.g., `claude_ai_slop.json`)
- `_annotations.json` — merged annotations grouped by ¶ ID
- `_summary.json` — top action and annotation count per ¶ ID

### Step 3: Synthesis

After JSON extraction completes:

1. Concatenate all report `.md` files into a single temp file with clear headers:

   ```
   === CLAUDE: title ===
   <content of claude_title.md>

   === CLAUDE: ai_slop ===
   <content of claude_ai_slop.md>

   === GEMINI: title ===
   ...
   ```

   Write this concatenated file to: `reports/YYYYMMDD_<id>_<post_basename>/_raw_inputs.md`

2. Run the synthesis call:

   ```bash
   cd tool_scripts/call_llm && uv run call_llm.py claude prompt_templates/synthesis.md <abs_raw_inputs_path> <abs_synthesis_output_path>
   ```

   Output to: `reports/YYYYMMDD_<id>_<post_basename>/synthesis.md`

3. Re-run JSON extraction to include synthesis annotations:

   ```bash
   cd tool_scripts/call_llm && uv run extract_annotations.py <abs_report_dir>
   ```

### Step 4: Render and report

After synthesis completes:
1. List all generated report files with sizes
2. Display the synthesis report content directly to the user — this is the primary output
3. Start the report viewer:
   ```bash
   cd tool_scripts/report_renderer && uv run render.py
   ```
   Run this in the background, then tell the user:
   - Tabbed view: http://localhost:8899/report/<folder_name>
   - **Interactive view**: http://localhost:8899/report/<folder_name>/interactive
