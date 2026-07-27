#!/usr/bin/env python3
"""Demo: AgentTools SDK v0.2 — A2A helpers, typed methods, self-healing."""

from __future__ import annotations

import asyncio
import os
import sys

from agenttools_client import AsyncAgentToolsClient


async def main() -> None:
    base = os.getenv("AGENTTOOLS_API_URL", "https://api.toolsforagents.tools")
    async with AsyncAgentToolsClient(base_url=base) as client:
        playbook = await client.onboarding()
        print("Rule:", playbook.get("critical_rule", "")[:72], "...")

        plan = await client.advisor("Extract title from example.com", include_dry_run=False)
        print("Advisor tool:", plan.get("primary_tool") or plan.get("recommended_tool"))

        page = await client.extract("https://example.com", format="markdown")
        print("Extract:", page.get("title"), "| words:", page.get("word_count"))

        if os.getenv("SDK_DEMO_A2A"):
            skills = await client.a2a.list_skills()
            print("A2A skills:", skills.get("count"))
            advice = await client.a2a.advisor("Plan a PDF → summary pipeline")
            print("A2A advisor status:", advice.get("status"))

        if os.getenv("SDK_DEMO_CHAIN"):
            chain = await client.run_chain("article_read", {"url": "https://example.com"})
            print("Chain:", chain.get("status"))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
