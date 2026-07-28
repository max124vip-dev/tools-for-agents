#!/usr/bin/env python3
"""
CRP flow demo — Quality Capability Discovery (SDK)

  goal → crp.resolve → execute best route → crp.feedback

Resolve is free. Execution requires AGENTTOOLS_API_KEY.

Usage:
  pip install -e ./agenttools_client
  python examples/crp_flow.py
  python examples/crp_flow.py "Summarize PDF https://example.com/paper.pdf"
  AGENTTOOLS_API_KEY=... python examples/crp_flow.py "OCR screenshot image"
"""

from __future__ import annotations

import asyncio
import os
import sys

from agenttools_client import AsyncAgentToolsClient, CRPClient

DEFAULT_GOAL = "Extract text from this PDF and summarize it"
DEFAULT_INPUTS = {"url": "https://example.com/file.pdf"}


async def main() -> int:
    goal = " ".join(sys.argv[1:]).strip() or DEFAULT_GOAL
    api_url = os.environ.get("AGENTTOOLS_API_URL", "http://127.0.0.1:8000")

    print("Tools for Agents — crp_flow.py (SDK)")
    print(f"API: {api_url}")
    print(f"Goal: {goal}\n")

    async with AsyncAgentToolsClient(base_url=api_url) as client:
        search = await client.crp.resolve("Search web for Python asyncio tutorials")
        print(f"1. Search resolve → {search['capability_id']} (confidence {search['confidence']})")

        resolution = await client.crp.resolve(
            goal,
            inputs=DEFAULT_INPUTS if "pdf" in goal.lower() else None,
            parent_response=search,
        )
        route = resolution["best_route"]
        print(f"2. CRP resolve → {resolution['capability_id']}")
        print(f"   best_route: {route['executor_type']}:{route['executor_id']}")
        print(f"   why: {route.get('why', [])[:2]}")
        if resolution.get("provenance", {}).get("parent"):
            print(f"   provenance chain: {resolution['provenance'].get('chain')}")

        if not client.api_key and not os.environ.get("AGENTTOOLS_API_KEY"):
            await client.ensure_api_key()
        try:
            result = await client.crp.execute_best_route(resolution)
            print(f"3. Executed chain/tool — status keys: {list(result.keys())[:6]}")
        except Exception as exc:
            print(f"3. Execute skipped/failed: {exc}")
            result = None

        fb = await client.crp.feedback(
            resolution_id=resolution["request_id"],
            capability_id=resolution["capability_id"],
            executor_id=route["executor_id"],
            outcome="success" if result else "skipped",
            latency_ms=result.get("duration_ms") if isinstance(result, dict) else None,
        )
        print(f"4. Feedback stored: {fb.get('id')}")

        ctx = CRPClient.with_provenance(resolution)
        print(f"5. Next-call context keys: {list(ctx.keys())}")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
