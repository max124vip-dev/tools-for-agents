"""HTTP client for MCP — API key or x402 agent wallet."""

from __future__ import annotations

import hashlib
import os
from typing import Any

import httpx

try:
    from request_context import get_request_api_key, get_request_x402_key
except ImportError:
    def get_request_api_key() -> str | None:
        return None

    def get_request_x402_key() -> str | None:
        return None

API_URL = os.environ.get("AGENTTOOLS_API_URL", "http://127.0.0.1:8000").rstrip("/")
API_KEY = os.environ.get("AGENTTOOLS_API_KEY", "")
X402_PRIVATE_KEY = os.environ.get("X402_PRIVATE_KEY") or os.environ.get(
    "AGENTTOOLS_X402_PRIVATE_KEY", ""
)
X402_NETWORK = os.environ.get("X402_NETWORK", "eip155:84532")
MCP_USE_SERVER_CREDENTIALS = os.environ.get("MCP_USE_SERVER_CREDENTIALS")
if MCP_USE_SERVER_CREDENTIALS is None:
    # Stdio MCP (Cursor): use env credentials by default when configured.
    MCP_USE_SERVER_CREDENTIALS = bool(API_KEY or X402_PRIVATE_KEY)
else:
    MCP_USE_SERVER_CREDENTIALS = MCP_USE_SERVER_CREDENTIALS.lower() in (
        "1",
        "true",
        "yes",
    )

_client: httpx.AsyncClient | None = None
_auth_mode: str | None = None
_auth_fingerprint: str | None = None


def _effective_api_key() -> str:
    per_request = get_request_api_key()
    if per_request:
        return per_request
    if MCP_USE_SERVER_CREDENTIALS:
        return API_KEY
    return ""


def _effective_x402_key() -> str:
    per_request = get_request_x402_key()
    if per_request:
        return per_request
    if MCP_USE_SERVER_CREDENTIALS:
        return X402_PRIVATE_KEY
    return ""


def auth_mode() -> str:
    """Return active auth: api_key | x402 | none."""
    if _effective_api_key():
        return "api_key"
    if _effective_x402_key():
        return "x402"
    return "none"


def _credential_fingerprint(value: str) -> str:
    if not value:
        return ""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _build_x402_client(base_url: str, private_key: str, network: str) -> httpx.AsyncClient:
    from eth_account import Account
    from x402 import x402Client
    from x402.http.clients.httpx import wrapHttpxWithPayment
    from x402.mechanisms.evm.exact import ExactEvmClientScheme

    account = Account.from_key(private_key)
    x402 = x402Client()
    x402.register(network, ExactEvmClientScheme(signer=account))
    return wrapHttpxWithPayment(x402, base_url=base_url, timeout=120.0)


def get_client() -> httpx.AsyncClient:
    """Return a shared AsyncClient with API key or x402 payment handling."""
    global _client, _auth_mode, _auth_fingerprint

    mode = auth_mode()
    api_key = _effective_api_key()
    x402_key = _effective_x402_key()
    fingerprint = (
        f"{mode}:"
        f"{_credential_fingerprint(api_key)}:"
        f"{_credential_fingerprint(x402_key)}"
    )
    if _client is not None and _auth_mode == mode and _auth_fingerprint == fingerprint:
        return _client

    if mode == "api_key":
        _client = httpx.AsyncClient(
            base_url=API_URL,
            timeout=120.0,
            headers={"Authorization": f"Bearer {api_key}"},
        )
    elif mode == "x402":
        _client = _build_x402_client(API_URL, x402_key, X402_NETWORK)
    else:
        _client = httpx.AsyncClient(base_url=API_URL, timeout=120.0)

    _auth_mode = mode
    _auth_fingerprint = fingerprint
    return _client


async def api_request(method: str, path: str, **kwargs: Any) -> httpx.Response:
    """Execute API request with configured auth."""
    client = get_client()
    return await client.request(method, path, **kwargs)


def auth_help() -> str:
    if auth_mode() == "api_key":
        return "Using per-request or server AGENTTOOLS_API_KEY (Bearer auth)."
    if auth_mode() == "x402":
        return f"Using x402 wallet on {X402_NETWORK} (auto PAYMENT-SIGNATURE on 402)."
    return (
        "No auth configured. Pass Authorization / X-API-Key / X402-Private-Key on remote MCP, "
        "or set AGENTTOOLS_API_KEY / X402_PRIVATE_KEY for stdio MCP."
    )
