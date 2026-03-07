/**
 * Cloudflare Worker: Subscribe proxy for Resend API
 * Accepts POST /api/subscribe { email: "..." } and adds the contact to a Resend audience.
 *
 * Environment variables (set via wrangler secret):
 *   RESEND_API_KEY   - Resend API key
 *   AUDIENCE_ID      - Resend audience ID
 */

import welcomeHtml from "../../templates/email_welcome.html";

export default {
  async fetch(request, env) {
    // CORS preflight
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 200, headers: corsHeaders() });
    }

    // Only accept POST /api/subscribe
    const url = new URL(request.url);
    if (request.method !== "POST" || url.pathname !== "/api/subscribe") {
      return jsonResponse(404, { ok: false, error: "Not found" });
    }

    let body;
    try {
      body = await request.json();
    } catch {
      return jsonResponse(400, { ok: false, error: "Invalid JSON" });
    }

    const email = (body.email || "").trim();
    if (!email || !email.includes("@")) {
      return jsonResponse(400, { ok: false, error: "Invalid email" });
    }

    const resp = await fetch(
      `https://api.resend.com/audiences/${env.AUDIENCE_ID}/contacts`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${env.RESEND_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      }
    );

    if (resp.ok) {
      // Send welcome email (fire-and-forget)
      fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${env.RESEND_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          from: "GoatWang's Blog <onboarding@resend.dev>",
          to: email,
          subject: "You're subscribed to GoatWang's Blog!",
          html: welcomeHtml,
        }),
      }).catch(() => {});
      return jsonResponse(200, { ok: true });
    }

    const data = await resp.json().catch(() => ({}));
    return jsonResponse(resp.status, {
      ok: false,
      error: data.message || "Failed to subscribe",
    });
  },
};

function jsonResponse(status, data) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      ...corsHeaders(),
    },
  });
}

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };
}
