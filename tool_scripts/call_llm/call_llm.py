#!/usr/bin/env python3
"""
Unified LLM caller for blog post review tasks.

Usage:
    cd tool_scripts/call_llm/ && uv run call_llm.py <model> <prompt_fp> <post_fp> <output_fp>

Models: claude, gemini, grok
- claude: calls `claude -p` CLI (model: opus), unsets CLAUDECODE env var
- gemini: calls `gemini -p` CLI (model: gemini-3-pro-preview)
- grok: calls Grok API with file upload (model: grok-4)

The prompt file is read and sent as the prompt.
The post file (markdown) is attached/included depending on the model.
The output is written to output_fp.
"""

import sys
import os
import json
import subprocess
import urllib.request
import pathlib


SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()


def load_config():
    config_path = SCRIPT_DIR / "config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    with open(config_path) as f:
        return json.load(f)


def call_claude(prompt: str, post_path: str) -> str:
    """Call Claude CLI with opus model. Unsets CLAUDECODE to allow nested sessions."""
    env = os.environ.copy()
    # Remove all CLAUDECODE-related env vars to avoid nested session errors
    for key in list(env.keys()):
        if key.startswith("CLAUDE"):
            del env[key]

    abs_post_path = str(pathlib.Path(post_path).resolve())

    full_prompt = f"Read the file at {abs_post_path} and follow the instructions below.\n\n{prompt}\n\nWrite your full response to stdout."

    result = subprocess.run(
        ["claude", "-p", full_prompt, "--model", "opus", "--allowedTools", "Read", "Write"],
        capture_output=True,
        text=True,
        env=env,
        timeout=600,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Claude CLI failed (exit {result.returncode}):\n{result.stderr}")
    return result.stdout


def call_gemini(prompt: str, post_path: str) -> str:
    """Call Gemini CLI. Uses @ syntax to attach the file."""
    abs_post_path = str(pathlib.Path(post_path).resolve())

    full_prompt = f"@{abs_post_path}\n\n{prompt}"

    result = subprocess.run(
        ["gemini", "-p", full_prompt, "--model", "gemini-3-pro-preview", "-s", "false", "--include-directories", str(pathlib.Path(post_path).resolve().parent)],
        capture_output=True,
        text=True,
        timeout=600,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Gemini CLI failed (exit {result.returncode}):\n{result.stderr}")
    return result.stdout


def call_grok(prompt: str, post_path: str, api_key: str) -> str:
    """Call Grok API with post content inlined in prompt."""
    abs_post_path = str(pathlib.Path(post_path).resolve())

    with open(abs_post_path) as f:
        post_content = f.read()

    full_prompt = f"以下是要分析的部落格文章內容：\n\n---\n{post_content}\n---\n\n{prompt}"

    payload = {
        "model": "grok-4",
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": full_prompt},
                ],
            }
        ],
    }

    payload_chat = {
        "model": "grok-4",
        "messages": [
            {"role": "user", "content": full_prompt},
        ],
    }

    req = urllib.request.Request(
        "https://api.x.ai/v1/chat/completions",
        data=json.dumps(payload_chat).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "call_llm/1.0",
        },
    )
    try:
        resp = urllib.request.urlopen(req, timeout=600)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Grok API failed ({e.code}):\n{body}") from e
    result = json.loads(resp.read().decode("utf-8"))

    # Extract text from chat completions response
    try:
        return result["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise RuntimeError(f"Could not extract text from Grok response:\n{json.dumps(result, indent=2)}")


def main():
    if len(sys.argv) != 5:
        print(f"Usage: {sys.argv[0]} <model> <prompt_fp> <post_fp> <output_fp>", file=sys.stderr)
        print("Models: claude, gemini, grok", file=sys.stderr)
        sys.exit(1)

    model = sys.argv[1]
    prompt_fp = sys.argv[2]
    post_fp = sys.argv[3]
    output_fp = sys.argv[4]

    # Read prompt
    with open(prompt_fp) as f:
        prompt = f.read()

    # Call LLM
    print(f"Calling {model}...")

    if model == "claude":
        result = call_claude(prompt, post_fp)
    elif model == "gemini":
        result = call_gemini(prompt, post_fp)
    elif model == "grok":
        config = load_config()
        api_key = config["GROK_APIKEY"]
        result = call_grok(prompt, post_fp, api_key)
    else:
        print(f"Unknown model: {model}. Use: claude, gemini, grok", file=sys.stderr)
        sys.exit(1)

    # Write output
    output_path = pathlib.Path(output_fp)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(result)

    print(f"Done. Output written to {output_fp}")


if __name__ == "__main__":
    main()
