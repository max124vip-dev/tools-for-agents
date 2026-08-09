#!/usr/bin/env python3
"""Minimal autonomous agent onboarding — discover, self-register, invoke."""

from __future__ import annotations

import httpx

API = "https://api.toolsforagents.tools"


def main() -> None:
    with httpx.Client(base_url=API, timeout=60.0) as client:
        playbook = client.get("/v1/onboarding").json()
        print("Rule:", playbook["critical_rule"])

        advisor = client.post("/v1/advisor", json={"goal": "Extract title from example.com"}).json()
        print("Advisor primary tool:", advisor.get("primary_tool") or advisor.get("recommended_tool"))

        reg = client.post("/v1/register", json={})
        reg.raise_for_status()
        key = reg.json()["api_key"]
        print("Registered. plan:", reg.json()["plan"])

        extract = client.post(
            "/v1/extract",
            headers={"Authorization": f"Bearer {key}"},
            json={"url": "https://example.com", "format": "markdown"},
        )
        extract.raise_for_status()
        data = extract.json()
        print("Extract:", data.get("title"), "words:", data.get("word_count"))


if __name__ == "__main__":
    main()
