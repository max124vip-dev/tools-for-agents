#!/usr/bin/env python3
"""
Agent flow demo — Tools for Agents (Decision Layer)

  goal → advisor → remember → examples → (optional) invoke → feedback

No API key required for advisor, tool-index, commons recall.
Set AGENTTOOLS_API_KEY to run the invoke step.

Usage:
  pip install httpx
  python examples/advisor_flow.py
  python examples/advisor_flow.py "OCR a scanned invoice PDF"
  AGENTTOOLS_API_KEY=sk_live_... python examples/advisor_flow.py "Read https://example.com"

Production API by default. Override:
  AGENTTOOLS_API_URL=https://api.toolsforagents.tools
"""

from __future__ import annotations

import json
import os
import sys

import httpx

API_URL = os.environ.get("AGENTTOOLS_API_URL", "https://api.toolsforagents.tools").rstrip("/")
API_KEY = os.environ.get("AGENTTOOLS_API_KEY", "")
DEFAULT_GOAL = "Extract text from a scanned scientific PDF"


def _client() -> httpx.Client:
    return httpx.Client(timeout=60.0, base_url=API_URL)


def step_discover(client: httpx.Client) -> dict:
    print("\n=== 1. Discover ===")
    r = client.get("/v1/discover")
    r.raise_for_status()
    data = r.json()
    print(f"  service: {data.get('service')} | tools: {data.get('tools_count')}")
    files = data.get("discovery_files") or {}
    if files:
        print(f"  tool-index: {files.get('tool_index', '—')}")
    return data


def step_tool_index(client: httpx.Client, tool: str) -> dict | None:
    print("\n=== 2. Tool index (compact) ===")
    r = client.get("/.well-known/tool-index.json")
    r.raise_for_status()
    index = r.json()
    match = next((t for t in index.get("tools", []) if t.get("name") == tool), None)
    if match:
        print(f"  {tool}: tier={match.get('latency_tier')} | units={match.get('units')} | ms~{match.get('typical_ms')}")
    else:
        print(f"  (tool {tool!r} not in index sample)")
    return match


def step_commons(client: httpx.Client, query: str) -> list:
    print("\n=== 3. Commons recall (network memory) ===")
    r = client.post("/v1/commons/recall", json={"query": query, "limit": 3})
    r.raise_for_status()
    results = r.json().get("results") or []
    for item in results[:3]:
        print(f"  · [{item.get('topic')}] {(item.get('finding') or '')[:90]}...")
    if not results:
        print("  (no matches)")
    return results


def step_advisor(client: httpx.Client, goal: str) -> dict:
    print("\n=== 4. Advisor (0 units, no key) ===")
    r = client.post("/v1/advisor", json={"goal": goal})
    r.raise_for_status()
    data = r.json()
    tool = data.get("recommended_tool")
    print(f"  recommended: {tool}()")
    print(f"  confidence: {data.get('confidence')} | success~{data.get('success_probability')}")
    print(f"  workflow: {' -> '.join(data.get('recommended_workflow') or [])}")
    print(f"  time/cost: {data.get('estimated_time')} | {data.get('estimated_cost')}")
    remember = data.get("remember") or {}
    if remember:
        print(f"  remember.tool: {remember.get('tool')}")
        print(f"  remember.reason: {remember.get('reason')}")
        if remember.get("network_tip"):
            print(f"  remember.network_tip: {str(remember.get('network_tip'))[:100]}...")
    alts = data.get("alternatives") or []
    if alts:
        parts = []
        for a in alts[:3]:
            name = a.get("tool") or "workflow"
            tags = ",".join(a.get("tradeoffs") or [])
            parts.append(f"{name}({tags})" if tags else name)
        print(f"  alternatives: {' | '.join(parts)}")
    return data


def step_examples(client: httpx.Client, tool: str) -> dict:
    print(f"\n=== 5. Examples for {tool} ===")
    r = client.get(f"/v1/tools/{tool}/examples")
    r.raise_for_status()
    data = r.json()
    examples = data.get("examples") or []
    print(f"  {len(examples)} example(s) — first request shape:")
    if examples:
        ex = examples[0]
        print(f"  title: {ex.get('title')}")
        print(json.dumps(ex.get("request"), indent=2)[:500])
    return data


def step_invoke(client: httpx.Client, tool: str, goal: str, advisor: dict) -> dict | None:
    print(f"\n=== 6. Invoke {tool} (optional, needs API key) ===")
    if not API_KEY:
        print("  skipped — set AGENTTOOLS_API_KEY to invoke")
        return None

    headers = {"Authorization": f"Bearer {API_KEY}"}

    if tool == "extract" and "http" in goal.lower():
        # naive URL pick for demo
        url = next((w for w in goal.split() if w.startswith("http")), "https://example.com")
        r = client.post("/v1/extract", headers=headers, json={"url": url, "format": "markdown", "mode": "fast"})
    elif tool == "pdf":
        print("  skipped — pdf demo needs a PDF URL in goal or edit script")
        return None
    else:
        print(f"  skipped — add invoke body for {tool} in script or use examples above")
        return None

    r.raise_for_status()
    data = r.json()
    preview = (data.get("markdown") or data.get("text") or "")[:200]
    cache = data.get("cache")
    print(f"  request_id: {data.get('request_id')}")
    if cache:
        print(f"  cache: hit={cache.get('hit')} age={cache.get('age_human')}")
    if preview:
        print(f"  preview: {preview!r}...")
    return data


def step_feedback(client: httpx.Client, tool: str, goal: str, request_id: str | None) -> None:
    print("\n=== 7. Feedback (optional, no key) ===")
    r = client.post(
        "/v1/feedback",
        json={
            "tool": tool,
            "goal": goal,
            "solved": True,
            "helpful": 5,
            "comment": f"advisor_flow.py demo — {tool} plan was useful for: {goal[:120]}",
            "request_id": request_id,
            "write_to_commons": False,
        },
    )
    if r.status_code == 201:
        print(f"  {r.json().get('message')}")
    else:
        print(f"  feedback status: {r.status_code}")


def main() -> int:
    goal = " ".join(sys.argv[1:]).strip() or DEFAULT_GOAL
    print("Tools for Agents — advisor_flow.py")
    print(f"API: {API_URL}")
    print(f"Goal: {goal}")

    with _client() as client:
        step_discover(client)
        step_commons(client, goal)
        advisor = step_advisor(client, goal)
        tool = advisor.get("recommended_tool") or "ingest"
        step_tool_index(client, tool)
        step_examples(client, tool)
        invoke_result = step_invoke(client, tool, goal, advisor)
        req_id = (invoke_result or {}).get("request_id")
        step_feedback(client, tool, goal, req_id)

    print("\nDone. Next: register agent → POST /v1/register/agent")
    print("Docs: https://toolsforagents.tools/docs · llms.txt: https://toolsforagents.tools/llms.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
