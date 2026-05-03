"""OpenRouter OAuth PKCE authentication flow.

Sources:
- https://openrouter.ai/docs/guides/overview/auth/oauth
- https://openrouter.ai/docs/api-reference/o-auth/exchange-auth-code-for-api-key
"""

import base64
import hashlib
import secrets
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

import requests

CALLBACK_PORT = 3000
AUTH_URL = "https://openrouter.ai/auth"
TOKEN_URL = "https://openrouter.ai/api/v1/auth/keys"
TIMEOUT = 180


def _base64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def generate_pkce() -> tuple[str, str]:
    code_verifier = _base64url(secrets.token_bytes(64))
    code_challenge = _base64url(hashlib.sha256(code_verifier.encode()).digest())
    return code_verifier, code_challenge


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    code: str | None = None
    error: str | None = None
    event = threading.Event()

    def log_message(self, format: str, *args: Any) -> None:
        pass

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path == "/callback" and "code" in params:
            OAuthCallbackHandler.code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<!DOCTYPE html><html><head><style>"
                b"body{background:#0a0a0a;color:#00ff41;font-family:monospace;"
                b"display:flex;align-items:center;justify-content:center;height:100vh;margin:0}"
                b".box{border:2px solid #00ff41;padding:40px;text-align:center}"
                b"h1{margin:0 0 10px}p{margin:0;color:#888}"
                b"</style></head><body><div class='box'>"
                b"<h1>[+] Authentication successful!</h1>"
                b"<p>You can close this tab and return to the terminal.</p>"
                b"</div></body></html>"
            )
            OAuthCallbackHandler.event.set()
        elif "error" in params:
            OAuthCallbackHandler.error = params.get("error_description", ["Unknown error"])[0]
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(f"<html><body>Auth failed: {OAuthCallbackHandler.error}</body></html>".encode())
            OAuthCallbackHandler.event.set()
        else:
            self.send_response(404)
            self.end_headers()


def authenticate() -> str:
    code_verifier, code_challenge = generate_pkce()

    callback_url = f"http://localhost:{CALLBACK_PORT}/callback"
    auth_url = (
        f"{AUTH_URL}?callback_url={callback_url}"
        f"&code_challenge={code_challenge}"
        f"&code_challenge_method=S256"
        f"&spawn_agent=fury"
    )

    server = HTTPServer(("127.0.0.1", CALLBACK_PORT), OAuthCallbackHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    print("Opening browser to authenticate with OpenRouter...")
    print(f"URL: {auth_url}")
    print()

    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    print("Waiting for authentication in browser...")
    print(f"Timeout: {TIMEOUT}s")
    print()

    got_event = OAuthCallbackHandler.event.wait(timeout=TIMEOUT)

    server.shutdown()

    if not got_event:
        raise RuntimeError(
            f"OAuth authentication timed out after {TIMEOUT}s.\n"
            "Please try again or manually create a key at https://openrouter.ai/keys"
        )

    if OAuthCallbackHandler.error:
        raise RuntimeError(f"OAuth error: {OAuthCallbackHandler.error}")

    print("Exchanging OAuth code for API key...")

    try:
        resp = requests.post(
            TOKEN_URL,
            json={
                "code": OAuthCallbackHandler.code,
                "code_verifier": code_verifier,
                "code_challenge_method": "S256",
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        api_key = str(data["key"])
        return api_key
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to exchange OAuth code: {e}")
