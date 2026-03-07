#!/usr/bin/env python3
"""
HTTP server that proxies newsletter subscribe requests to Resend API.
Runs on Mac Mini behind Tailscale at https://goatwang.tail5cb21.ts.net/api/subscribe

Usage:
    uv run --with requests subscribe_server.py [--config ../../config.local.json] [--port 8900]
"""

import argparse
import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler


class SubscribeHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self._cors_headers()
        self.end_headers()

    def do_POST(self):
        if self.path != "/api/subscribe":
            self._json_response(404, {"ok": False, "error": "Not found"})
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length)) if length else {}
        except (json.JSONDecodeError, ValueError):
            self._json_response(400, {"ok": False, "error": "Invalid JSON"})
            return

        email = body.get("email", "").strip()
        if not email or "@" not in email:
            self._json_response(400, {"ok": False, "error": "Invalid email"})
            return

        import requests

        config = self.server.config
        api_key = config["resend"]["api_key"]
        audience_id = config["resend"]["audience_id"]

        resp = requests.post(
            f"https://api.resend.com/audiences/{audience_id}/contacts",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={"email": email},
            timeout=10,
        )

        if resp.status_code in (200, 201):
            self._json_response(200, {"ok": True})
        else:
            error = resp.json().get("message", "Failed to subscribe")
            self._json_response(resp.status_code, {"ok": False, "error": error})

    def _json_response(self, status, data):
        self.send_response(status)
        self._cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def log_message(self, format, *args):
        print(f"[subscribe] {args[0]}", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Newsletter subscribe proxy server")
    parser.add_argument("--config", default="../../config.local.json", help="Path to config file with Resend API key")
    parser.add_argument("--port", type=int, default=8900, help="Port to listen on")
    args = parser.parse_args()

    config_path = os.path.join(os.path.dirname(__file__), args.config)
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        sys.exit(1)

    with open(config_path) as f:
        config = json.load(f)

    if "api_key" not in config.get("resend", {}):
        print("Missing resend.api_key in config")
        sys.exit(1)

    server = HTTPServer(("0.0.0.0", args.port), SubscribeHandler)
    server.config = config
    print(f"Subscribe server listening on port {args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
