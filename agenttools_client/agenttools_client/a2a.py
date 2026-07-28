"""A2A-first helpers — delegate high-level tasks to remote agent skills."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agenttools_client.client import AsyncAgentToolsClient


class A2AClient:
    """Invoke Tools for Agents as an A2A remote agent (skills + Agent Card)."""

    def __init__(self, parent: AsyncAgentToolsClient) -> None:
        self._parent = parent

    async def list_skills(self) -> dict[str, Any]:
        return await self._parent.json("GET", "/a2a/v1/skills", auth=False)

    async def invoke(self, skill_id: str, input: dict | None = None) -> dict[str, Any]:
        return await self._parent.invoke_skill(skill_id, input)

    async def advisor(
        self,
        goal: str,
        *,
        context: dict | None = None,
        inputs: dict | None = None,
        include_dry_run: bool = False,
        max_latency_ms: int | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"goal": goal}
        if context:
            payload["context"] = context
        if inputs:
            payload["inputs"] = inputs
        if include_dry_run:
            payload["include_dry_run"] = True
        if max_latency_ms is not None:
            payload["max_latency_ms"] = max_latency_ms
        return await self.invoke("advisor", payload)

    async def run_chain(
        self,
        chain_id: str,
        inputs: dict | None = None,
        *,
        crp_provenance: dict | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"chain_id": chain_id, "inputs": inputs or {}}
        if crp_provenance:
            payload["crp_provenance"] = crp_provenance
        return await self.invoke("run-chain", payload)

    async def resolve_capability(
        self,
        goal: str,
        *,
        capability: str | None = None,
        inputs: dict | None = None,
        context: dict | None = None,
        crp_provenance: dict | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"goal": goal}
        if capability:
            payload["capability"] = capability
        if inputs:
            payload["inputs"] = inputs
        ctx = dict(context or {})
        if crp_provenance:
            ctx["crp_provenance"] = crp_provenance
        if ctx:
            payload["context"] = ctx
        return await self.invoke("resolve-capability", payload)

    async def run_mission(self, goal: str, *, template: str | None = None, async_job: bool = False) -> dict[str, Any]:
        payload: dict[str, Any] = {"goal": goal}
        if template:
            payload["template"] = template
        if async_job:
            payload["async"] = True
        return await self.invoke("run-mission", payload)

    async def web_ingest(self, url: str, **kwargs: Any) -> dict[str, Any]:
        return await self.invoke("web-ingest", {"url": url, **kwargs})

    async def research(self, query: str, **kwargs: Any) -> dict[str, Any]:
        return await self.invoke("agent-research", {"query": query, **kwargs})

    async def verify_claim(self, claim: str, **kwargs: Any) -> dict[str, Any]:
        return await self.invoke("verify-claim", {"claim": claim, **kwargs})
