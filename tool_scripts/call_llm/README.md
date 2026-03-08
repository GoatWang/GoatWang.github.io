# call_llm — Multi-LLM Blog Post Review Tool

Calls Claude, Gemini, or Grok to review a blog post with a given prompt template.

## Setup

```bash
cd tool_scripts/call_llm
uv init  # already done
```

Create `config.json` (not tracked by git):

```json
{
  "GROK_APIKEY": "your-xai-api-key"
}
```

### Prerequisites

- **Claude CLI** (`claude`): installed and authenticated
- **Gemini CLI** (`gemini`): installed and authenticated
- **curl**: for Grok API file uploads

## Usage

```bash
cd tool_scripts/call_llm && uv run call_llm.py <model> <prompt_fp> <post_fp> <output_fp>
```

### Arguments

| Arg | Description |
|-----|-------------|
| `model` | `claude`, `gemini`, or `grok` |
| `prompt_fp` | Path to prompt template (e.g., `prompt_templates/title.md`) |
| `post_fp` | Path to the blog post markdown file |
| `output_fp` | Path to write the LLM response |

### Examples

```bash
# Title review with Claude
cd tool_scripts/call_llm && uv run call_llm.py claude \
  prompt_templates/title.md \
  ../../content/posts/20260307_chardet_ai_clean_room.md \
  ../../reports/20260308_0_chardet_ai_clean_room/claude_title.md

# Tone rewrite with Grok
cd tool_scripts/call_llm && uv run call_llm.py grok \
  prompt_templates/tone.md \
  ../../content/posts/20260307_chardet_ai_clean_room.md \
  ../../reports/20260308_0_chardet_ai_clean_room/grok_tone.md
```

## Models

| Model | Interface | Notes |
|-------|-----------|-------|
| `claude` | CLI (`claude -p`, model: opus) | Unsets `CLAUDE*` env vars for nested sessions |
| `gemini` | CLI (`gemini -p`, model: gemini-3-pro-preview) | Uses `@path` syntax for file attachment |
| `grok` | API (file upload + chat) | Uses `config.json` for API key, model: grok-4-fast |

## Prompt Templates

- `prompt_templates/title.md` — 10 title candidates with scoring
- `prompt_templates/tone.md` — Pick 2 tones, rewrite entire post in each
- `prompt_templates/arrangement.md` — Evaluate sections, propose new arrangement
- `prompt_templates/ai_slop.md` — Score paragraphs on 9 AI-slop dimensions (density, monotony, clichés, emotional flatness, overload, etc.)
- `prompt_templates/synthesis.md` — Cross-model synthesis into a decision-ready summary
