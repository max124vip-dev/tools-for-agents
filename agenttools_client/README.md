# AgentTools Python Client

Self-healing **reference SDK** for [Tools for Agents](https://toolsforagents.tools) — M2M / A2A.

## Install

```bash
pip install agenttools-client
# or from repo:
pip install -e ./agenttools_client
```

Requires Python 3.10+ and `httpx`.

## Features

| Feature | Description |
|---------|-------------|
| Auto auth | `AGENTTOOLS_API_KEY` or `POST /v1/register {}` |
| 422 self-heal | Matches `/v1/tools/{tool}/examples` by missing `fields[]` |
| 5xx retry | Honors `Retry-After` / `retry_after_sec` |
| A2A-first | `client.a2a.advisor()`, `run_chain()`, `run_mission()` |
| **CRP Discovery** | `client.crp.resolve()`, `feedback()`, `execute_best_route()` |
| Provenance chaining | `CRPClient.with_provenance(response)` |
| Typed helpers | `extract()`, `ingest()`, `dry_run()`, `advisor()` |

## Quick start

```python
import asyncio
from agenttools_client import AsyncAgentToolsClient

async def main():
    async with AsyncAgentToolsClient() as client:
        plan = await client.advisor("Extract markdown from a blog URL")
        page = await client.extract("https://example.com")
        chain = await client.run_chain("article_read", {"url": "https://example.com"})
        # A2A orchestrators:
        skill = await client.a2a.advisor("Summarize a PDF for RAG")

asyncio.run(main())
```

## A2A (preferred for multi-agent orchestrators)

```python
async with AsyncAgentToolsClient() as client:
    skills = await client.a2a.list_skills()
    result = await client.a2a.run_chain("pdf_summary", {"url": "https://example.com/x.pdf"})
    mission = await client.a2a.run_mission("Research solid-state batteries")
```

Agent Card: `GET https://api.toolsforagents.tools/.well-known/agent-card.json`

## CRP — Quality Capability Discovery

```python
from agenttools_client import AsyncAgentToolsClient, CRPClient

async with AsyncAgentToolsClient() as client:
    # Free: resolve intent → ranked routes + invocation JSON
    resolution = await client.crp.resolve(
        "Summarize this PDF",
        inputs={"url": "https://example.com/paper.pdf"},
    )
    print(resolution["capability_id"], resolution["best_route"]["executor_id"])

    # Paid: execute best route (needs API key)
    result = await client.crp.execute_best_route(resolution)

    # Free: feedback improves ranking
    await client.crp.feedback(
        resolution["request_id"],
        resolution["capability_id"],
        resolution["best_route"]["executor_id"],
        "success",
        latency_ms=result.get("duration_ms"),
    )

    # Chain provenance to next call
    ctx = CRPClient.with_provenance(resolution)
    plan = await client.advisor("Next step", context=ctx)
```

See `examples/crp_flow.py` and [CRP spec](https://github.com/max124vip-dev/tools-for-agents/blob/main/docs/CRP_SPEC_v0.md).

## Self-healing 422

Wrong body → SDK fetches examples, picks best match for missing fields, retries once:

```python
await client.json("POST", "/v1/conflict/detect", json={})  # auto-fixes to documents[]
```

## Environment

| Variable | Default |
|----------|---------|
| `AGENTTOOLS_API_KEY` | — |
| `AGENTTOOLS_API_URL` | `https://api.toolsforagents.tools` |

## Publish (maintainers)

See [PUBLISH.md](./PUBLISH.md).

## License

MIT
