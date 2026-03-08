Convert the markdown file at $ARGUMENTS to PDF.

## Instructions

1. Determine the output filename:
   - Extract the base filename from the input path (e.g., `20260307_chardet_ai_clean_room` from `content/posts/20260307_chardet_ai_clean_room.md`)
   - Follow the CLAUDE.md naming convention for the `prompts/` folder: scan for today's date prefix to determine the next ID
   - Output to `prompts/YYYYMMDD_ID_<base_filename>.pdf`

2. Run the conversion:
   ```bash
   uv run --with "markdown,weasyprint,pygments" tool_scripts/md2pdf/md2pdf.py <input_path> <output_path>
   ```

3. Report the output file path and size to the user.
