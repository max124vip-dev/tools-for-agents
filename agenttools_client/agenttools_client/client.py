"""Async and sync HTTP clients for Tools for Agents API."""

from __future__ import annotations

import asyncio
import os
from typing import Any

import httpx

from agenttools_client.a2a import A2AClient
from agenttools_client._errors import AgentToolsHTTPError, AgentToolsRetryExhausted
from agenttools_client._heal import is_retryable_status, pick_example_body, retry_after_seconds
from agenttools_client._paths import infer_tool_from_path

DEFAULT_BASE_URL = "https://api.toolsforagents.tools"
DEFAULT_USER_AGENT = "AgentToolsClient/0.2.0 (+https://toolsforagents.tools)"


class AsyncAgentToolsClient:
    """
    Lightweight reference client for autonomous agents.

    - Auto Bearer auth (env AGENTTOOLS_API_KEY or POST /v1/register)
    - 422 → fetch /v1/tools/{tool}/examples and retry once with best-matching body
    - 502/503/504 → wait Retry-After / retry_after_sec and retry
    - A2A-first: client.a2a.advisor(), client.a2a.run_chain(), …
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        *,
        auto_register: bool = True,
        max_retries: int = 3,
        fix_422: bool = True,
        timeout: float = 120.0,
        user_agent: str = DEFAULT_USER_AGENT,
    ) -> None:
        self.base_url = (base_url or os.getenv("AGENTTOOLS_API_URL") or DEFAULT_BASE_URL).rstrip("/")
        self._api_key = api_key or os.getenv("AGENTTOOLS_API_KEY")
        self.auto_register = auto_register
        self.max_retries = max(0, max_retries)
        self.fix_422 = fix_422
        self.user_agent = user_agent
        self._a2a = A2AClient(self)
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={
                "User-Agent": user_agent,
                "Accept": "application/json",
            },
        )

    @property
    def a2a(self) -> A2AClient:
        """A2A remote agent — skills, chains, missions (preferred for orchestrators)."""
        return self._a2a

    async def __aenter__(self) -> AsyncAgentToolsClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()

    async def close(self) -> None:
        await self._client.aclose()

    @property
    def api_key(self) -> str | None:
        return self._api_key

    def _auth_headers(self, headers: dict[str, str] | None) -> dict[str, str]:
        out = dict(headers or {})
        if self._api_key and "Authorization" not in out:
            out["Authorization"] = f"Bearer {self._api_key}"
        return out

    async def ensure_api_key(self) -> str:
        if self._api_key:
            return self._api_key
        if not self.auto_register:
            raise AgentToolsHTTPError("No API key — set AGENTTOOLS_API_KEY or call register()")
        self._api_key = await self.register()
        return self._api_key

    async def register(self) -> str:
        resp = await self._client.post("/v1/register", json={})
        resp.raise_for_status()
        key = resp.json().get("api_key")
        if not key:
            raise AgentToolsHTTPError("Register response missing api_key", status_code=resp.status_code)
        self._api_key = key
        return key

    async def register_agent(
        self,
        agent_id: str,
        *,
        accepted_tos_version: str = "1.0",
        label: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "agent_id": agent_id,
            "accepted_tos_version": accepted_tos_version,
        }
        if label:
            body["label"] = label
        data = await self.json("POST", "/v1/register/agent", json=body, auth=False)
        key = data.get("api_key")
        if key:
            self._api_key = key
        return data

    async def get(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self.request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self.request("POST", path, **kwargs)

    async def request(
        self,
        method: str,
        path: str,
        *,
        auth: bool = True,
        json: dict | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        if auth:
            await self.ensure_api_key()
        headers = self._auth_headers(kwargs.pop("headers", None))
        attempt = 0
        fixed_422 = False
        last_resp: httpx.Response | None = None

        while True:
            resp = await self._client.request(method, path, json=json, headers=headers, **kwargs)
            last_resp = resp

            if resp.status_code == 422 and self.fix_422 and not fixed_422 and method.upper() == "POST":
                fixed = await self._heal_422(path, json, resp)
                if fixed is not None:
                    json = fixed
                    fixed_422 = True
                    continue

            if resp.status_code in (502, 503, 504) and attempt < self.max_retries:
                data = _safe_json(resp)
                if is_retryable_status(resp.status_code, data):
                    delay = retry_after_seconds(data, dict(resp.headers))
                    attempt += 1
                    await asyncio.sleep(delay)
                    continue

            if resp.is_success:
                return resp

            if attempt >= self.max_retries and resp.status_code in (502, 503, 504):
                raise AgentToolsRetryExhausted(
                    f"Retries exhausted for {method} {path}",
                    status_code=resp.status_code,
                    detail=_safe_json(resp),
                )

            raise AgentToolsHTTPError(
                f"HTTP {resp.status_code} for {method} {path}",
                status_code=resp.status_code,
                detail=_safe_json(resp),
            )

        raise AgentToolsRetryExhausted(
            f"Retries exhausted for {method} {path}",
            status_code=last_resp.status_code if last_resp else None,
        )

    async def _heal_422(
        self,
        path: str,
        partial: dict | None,
        response: httpx.Response,
    ) -> dict | None:
        tool = infer_tool_from_path(path)
        if not tool:
            return None
        ex_resp = await self._client.get(
            f"/v1/tools/{tool}/examples",
            headers=self._auth_headers(None),
        )
        if ex_resp.status_code != 200:
            return None
        detail = _safe_json(response) or {}
        examples = ex_resp.json().get("examples") or []
        return pick_example_body(examples, partial, detail.get("fields"))

    async def json(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        resp = await self.request(method, path, **kwargs)
        return resp.json()

    async def onboarding(self) -> dict[str, Any]:
        return await self.json("GET", "/v1/onboarding", auth=False)

    async def advisor(
        self,
        goal: str,
        *,
        context: dict | None = None,
        inputs: dict | None = None,
        include_dry_run: bool = False,
        max_latency_ms: int | None = None,
        use_a2a: bool = False,
    ) -> dict[str, Any]:
        if use_a2a:
            return await self.a2a.advisor(
                goal,
                context=context,
                inputs=inputs,
                include_dry_run=include_dry_run,
                max_latency_ms=max_latency_ms,
            )
        payload: dict[str, Any] = {"goal": goal}
        if context:
            payload["context"] = context
        if inputs:
            payload["inputs"] = inputs
        if include_dry_run:
            payload["include_dry_run"] = True
        if max_latency_ms is not None:
            payload["max_latency_ms"] = max_latency_ms
        return await self.json("POST", "/v1/advisor", json=payload, auth=False)

    async def dry_run(
        self,
        url: str,
        *,
        probe_depth: str = "peek",
        intent: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"url": url, "probe_depth": probe_depth}
        if intent:
            body["intent"] = intent
        return await self.json("POST", "/v1/dry-run", json=body, auth=False)

    async def extract(
        self,
        url: str,
        *,
        mode: str | None = None,
        format: str | None = None,
        **extra: Any,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"url": url, **extra}
        if mode:
            body["mode"] = mode
        if format:
            body["format"] = format
        return await self.json("POST", "/v1/extract", json=body)

    async def ingest(self, url: str, **kwargs: Any) -> dict[str, Any]:
        return await self.json("POST", "/v1/ingest", json={"url": url, **kwargs})

    async def tool(self, tool: str, body: dict | None = None) -> dict[str, Any]:
        """Resolve endpoint via GET /v1/tools/{tool}, then invoke."""
        meta = await self.json("GET", f"/v1/tools/{tool}", auth=False)
        endpoint = meta.get("endpoint", "")
        method, _, path = endpoint.partition(" ")
        path = path.strip() or f"/v1/{tool}"
        if method.upper() != "POST":
            return await self.json(method.upper(), path, auth=True)
        payload = body or {}
        if path.startswith("/v1/extended/"):
            return await self.json("POST", path, json={"args": payload})
        return await self.json("POST", path, json=payload)

    async def run_chain(
        self,
        chain_id: str,
        inputs: dict | None = None,
        *,
        use_a2a: bool = False,
    ) -> dict[str, Any]:
        if use_a2a:
            return await self.a2a.run_chain(chain_id, inputs)
        return await self.json(
            "POST",
            "/v1/chains/run",
            json={"chain_id": chain_id, "inputs": inputs or {}},
        )

    async def invoke_skill(self, skill_id: str, input: dict | None = None) -> dict[str, Any]:
        return await self.json(
            "POST",
            f"/a2a/v1/skills/{skill_id}/invoke",
            json={"input": input or {}},
        )


class AgentToolsClient:
    """Sync wrapper around AsyncAgentToolsClient."""

    _DELEGATE = (
        "register",
        "register_agent",
        "ensure_api_key",
        "request",
        "get",
        "post",
        "json",
        "onboarding",
        "advisor",
        "dry_run",
        "extract",
        "ingest",
        "tool",
        "run_chain",
        "invoke_skill",
        "close",
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._async = AsyncAgentToolsClient(*args, **kwargs)

    def __enter__(self) -> AgentToolsClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    @property
    def api_key(self) -> str | None:
        return self._async.api_key

    @property
    def a2a(self) -> _SyncA2AClient:
        return _SyncA2AClient(self._async.a2a)

    def __getattr__(self, name: str) -> Any:
        if name not in self._DELEGATE:
            raise AttributeError(name)
        return _sync(getattr(self._async, name))


class _SyncA2AClient:
    def __init__(self, inner: A2AClient) -> None:
        self._inner = inner

    def __getattr__(self, name: str) -> Any:
        return _sync(getattr(self._inner, name))


def _sync(coro_fn: Any) -> Any:
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return asyncio.run(coro_fn(*args, **kwargs))

    return wrapper


def _safe_json(resp: httpx.Response) -> dict | None:
    try:
        data = resp.json()
        return data if isinstance(data, dict) else None
    except Exception:
        return None
