# Subscribe Worker

Cloudflare Worker that proxies newsletter subscribe requests to Resend API.

## Setup

```bash
cd workers/subscribe
npx wrangler login
npx wrangler secret put RESEND_API_KEY    # paste your Resend API key
npx wrangler secret put AUDIENCE_ID       # paste your Resend audience ID
npx wrangler deploy
```

## Endpoint

`POST https://subscribe.jeremy455576.workers.dev/api/subscribe`

```json
{ "email": "user@example.com" }
```

Returns `{ "ok": true }` on success or `{ "ok": false, "error": "..." }` on failure.
