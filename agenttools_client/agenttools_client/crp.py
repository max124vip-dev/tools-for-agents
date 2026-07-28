"""CRP — Quality Capability Discovery helpers for the Python SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from agenttools_client._errors import AgentToolsClientError

if TYPE_CHECKING:
    from agenttools_client.client import AsyncAgentToolsClient


class CRPClient:
    """
    Quality Capability Discovery — resolve intent to ranked routes, feedback, provenance chaining.

    Free endpoints (no API key required for resolve/list). Execution of routes is paid.
    """

    def __init__(self, parent: AsyncAgentToolsClient) -> None:
        self._parent = parent

    @staticmethod
    def extract_provenance(response: dict[str, Any]) -> dict[str, Any] | None:
        """Pull provenance from CRP/advisor/chain/A2A/MCP responses."""
        if not response:
            return None
        prov = response.get("provenance")
        if prov:
            return prov
        meta = response.get("_meta")
        if isinstance(meta, dict) and meta.get("crp_provenance"):
            return meta["crp_provenance"]
        data = response.get("data")
        if isinstance(data, dict) and data.get("provenance"):
            return data["provenance"]
        return None

    @staticmethod
    def with_provenance(response: dict[str, Any]) -> dict[str, Any]:
        """Build context for the next resolve/advisor/chain call."""
        prov = CRPClient.extract_provenance(response)
        if not prov:
            return {}
        return {"crp_provenance": prov}

    @staticmethod
    def context_from_provenance(provenance: dict[str, Any] | None) -> dict[str, Any]:
        if not provenance:
            return {}
        return {"crp_provenance": provenance}

    async def resolve(
        self,
        goal: str,
        *,
        capability: str | None = None,
        inputs: dict | None = None,
        constraints: dict | None = None,
        context: dict | None = None,
        parent_provenance: dict | None = None,
        parent_response: dict | None = None,
        use_a2a: bool = False,
    ) -> dict[str, Any]:
        """POST /v1/crp/resolve — ranked routes + invocation JSON (free)."""
        if use_a2a:
            payload: dict[str, Any] = {"goal": goal}
            if capability:
                payload["capability"] = capability
            if inputs:
                payload["inputs"] = inputs
            if constraints:
                payload["constraints"] = constraints
            ctx = dict(context or {})
            prov = parent_provenance or (
                self.extract_provenance(parent_response) if parent_response else None
            )
            if prov:
                ctx["crp_provenance"] = prov
            if ctx:
                payload["context"] = ctx
            return await self._parent.a2a.invoke("resolve-capability", payload)

        ctx = dict(context or {})
        prov = parent_provenance or (
            self.extract_provenance(parent_response) if parent_response else None
        )
        if prov:
            ctx["crp_provenance"] = prov

        payload = {"goal": goal}
        if capability:
            payload["capability"] = capability
        if inputs:
            payload["inputs"] = inputs
        if constraints:
            payload["constraints"] = constraints
        if ctx:
            payload["context"] = ctx
        return await self._parent.json("POST", "/v1/crp/resolve", json=payload, auth=False)

    async def feedback(
        self,
        resolution_id: str,
        capability_id: str,
        executor_id: str,
        outcome: str,
        *,
        latency_ms: int | None = None,
        cost_usd: float | None = None,
        error_code: str | None = None,
        retry_count: int = 0,
        agent_id: str | None = None,
        notes: str | None = None,
    ) -> dict[str, Any]:
        """POST /v1/crp/feedback — improve ranking (free, optional auth)."""
        body: dict[str, Any] = {
            "resolution_id": resolution_id,
            "capability_id": capability_id,
            "executor_id": executor_id,
            "outcome": outcome,
            "retry_count": retry_count,
        }
        if latency_ms is not None:
            body["latency_ms"] = latency_ms
        if cost_usd is not None:
            body["cost_usd"] = cost_usd
        if error_code:
            body["error_code"] = error_code
        if agent_id:
            body["agent_id"] = agent_id
        if notes:
            body["notes"] = notes
        return await self._parent.json("POST", "/v1/crp/feedback", json=body, auth=False)

    async def list_capabilities(self, *, domain: str | None = None) -> dict[str, Any]:
        path = "/v1/crp/capabilities"
        if domain:
            return await self._parent.json("GET", path, params={"domain": domain}, auth=False)
        return await self._parent.json("GET", path, auth=False)

    async def get_capability(self, capability_id: str) -> dict[str, Any]:
        return await self._parent.json("GET", f"/v1/crp/capabilities/{capability_id}", auth=False)

    async def execute_best_route(
        self,
        resolution: dict[str, Any],
        *,
        use_a2a: bool = False,
    ) -> dict[str, Any]:
        """Execute best_route from a resolve response (paid — requires API key)."""
        route = resolution.get("best_route")
        if not route:
            raise AgentToolsClientError("Resolution has no best_route")

        prov = self.extract_provenance(resolution)
        inv = route.get("invocation") or {}
        path = inv.get("path") or route.get("endpoint", "").split(" ", 1)[-1]
        method = (inv.get("method") or "POST").upper()

        if path == "/v1/chains/run" or route.get("executor_type") == "internal_chain":
            body = inv.get("body") or {}
            chain_id = body.get("chain_id") or route.get("executor_id")
            inputs = body.get("inputs") or {}
            return await self._parent.run_chain(
                chain_id,
                inputs,
                crp_provenance=prov,
                use_a2a=use_a2a,
            )

        if method == "GET":
            return await self._parent.json(
                "GET",
                path,
                params=inv.get("query") or inv.get("body"),
                auth=True,
            )

        body = inv.get("body") or {}
        if path.startswith("/v1/extended/"):
            return await self._parent.json("POST", path, json={"args": body.get("args", body)}, auth=True)
        return await self._parent.json(method, path, json=body, auth=True)

    async def resolve_and_execute(
        self,
        goal: str,
        *,
        inputs: dict | None = None,
        use_a2a: bool = False,
        **resolve_kwargs: Any,
    ) -> dict[str, Any]:
        """Resolve then execute best route — returns {resolution, result}."""
        resolution = await self.resolve(goal, inputs=inputs, use_a2a=use_a2a, **resolve_kwargs)
        result = await self.execute_best_route(resolution, use_a2a=use_a2a)
        return {"resolution": resolution, "result": result}


__all__ = ["CRPClient"]
