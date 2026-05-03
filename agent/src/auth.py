"""OpenRouter OAuth PKCE authentication flow.

Sources:
- https://openrouter.ai/docs/guides/overview/auth/oauth
- https://openrouter.ai/docs/api-reference/o-auth/exchange-auth-code-for-api-key
"""

import base64
import hashlib
import secrets
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

import requests

CALLBACK_PORT = 5180
AUTH_URL = "https://openrouter.ai/auth"
TOKEN_URL = "https://openrouter.ai/api/v1/auth/keys"
TIMEOUT = 120


def _base64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def generate_pkce() -> tuple[str, str]:
    """Generate PKCE code_verifier and code_challenge.

    Returns:
        (code_verifier, code_challenge) both base64url encoded.
    """
    code_verifier = _base64url(secrets.token_bytes(64))
    code_challenge = _base64url(hashlib.sha256(code_verifier.encode()).digest())
    return code_verifier, code_challenge


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler that captures the OAuth callback code."""

    code: str | None = None
    error: str | None = None

    def log_message(self, format: str, *args: Any) -> None:
        pass  # Suppress default logging

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path == "/callback" and "code" in params:
            OAuthCallbackHandler.code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<html><body><h1>Authentication successful!</h1>"
                b"<p>You can close this tab and return to the terminal.</p></body></html>"
            )
        elif "error" in params:
            OAuthCallbackHandler.error = params.get("error_description", ["Unknown error"])[0]
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<html><body><h1>Authentication failed</h1><p>"
                + OAuthCallbackHandler.error.encode()
                + b"</p></body></html>"
            )
        else:
            self.send_response(404)
            self.end_headers()


def _start_callback_server() -> HTTPServer:
    server = HTTPServer(("127.0.0.1", CALLBACK_PORT), OAuthCallbackHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def authenticate() -> str:
    """Run the full OAuth PKCE flow and return the API key.

    Flow:
    1. Generate PKCE code_verifier + code_challenge
    2. Open browser to OpenRouter auth page
    3. Wait for callback with authorization code
    4. Exchange code for API key

    Returns:
        API key string.

    Raises:
        RuntimeError: If authentication fails or times out.
    """
    code_verifier, code_challenge = generate_pkce()

    callback_url = f"http://localhost:{CALLBACK_PORT}/callback"
    auth_url = (
        f"{AUTH_URL}?callback_url={callback_url}"
        f"&code_challenge={code_challenge}"
        f"&code_challenge_method=S256"
        f"&spawn_agent=fury"
    )

    print("Attempting OAuth authentication...")
    print(f"OAuth server listening on port {CALLBACK_PORT}")
    print("Opening browser to authenticate with OpenRouter...")
    print()
    print("Please open:")
    print(f"  {auth_url}")
    print()

    try:
        webbrowser.open(auth_url)
    except Exception:
        print("Could not open browser automatically.")

    server = _start_callback_server()
    print(f"Waiting for authentication in browser (timeout: {TIMEOUT}s)...")

    deadline = time.time() + TIMEOUT
    while time.time() < deadline:
        if OAuthCallbackHandler.code:
            break
        if OAuthCallbackHandler.error:
            server.shutdown()
            raise RuntimeError(f"OAuth error: {OAuthCallbackHandler.error}")
        time.sleep(0.5)

    server.shutdown()

    if not OAuthCallbackHandler.code:
        raise RuntimeError(
            f"OAuth authentication timed out after {TIMEOUT}s. "
            "Please try again or manually create a key at https://openrouter.ai/keys"
        )

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
        print("Successfully obtained OpenRouter API key via OAuth!")
        return api_key

    except requests.RequestException as e:
        raise RuntimeError(f"Failed to exchange OAuth code: {e}")
