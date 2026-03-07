# Subscribe Server

HTTP proxy server that handles newsletter subscribe requests from the blog and forwards them to Resend API.

## Usage

```bash
uv run --with requests subscribe_server.py --port 8900
```

The server exposes `POST /api/subscribe` which accepts `{"email": "..."}` and adds the contact to the Resend audience.

## Configuration

Reads `config.local.json` from the repo root (default path: `../../config.local.json`). Required fields:

```json
{
  "resend": {
    "api_key": "re_...",
    "audience_id": "..."
  }
}
```

## Deployment

Run on the Mac Mini behind Tailscale. The blog's subscribe form sends requests to `https://goatwang.tail5cb21.ts.net/api/subscribe`.

You'll need a reverse proxy (e.g., Caddy or nginx) to route `/api/subscribe` on port 443 to this server on port 8900.
