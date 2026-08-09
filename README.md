<p align="center">
  <img src="https://toolsforagents.tools/assets/logo.svg" width="72" height="72" alt="Tools for Agents">
</p>

<h1 align="center">Tools for Agents</h1>

<p align="center">
  <strong>Decision layer for AI agents</strong> — plan workflows, execute 100+ tools, and delegate multi-step missions.<br>
  Not a flat API catalog. An orchestration platform built for <em>autonomous</em> agents.
</p>

<p align="center">
  <a href="https://toolsforagents.tools"><img src="https://img.shields.io/badge/website-toolsforagents.tools-3b82f6?style=for-the-badge" alt="Website"></a>
  <a href="https://api.toolsforagents.tools/docs"><img src="https://img.shields.io/badge/API-Swagger-22c55e?style=for-the-badge" alt="API"></a>
  <a href="https://pypi.org/project/agenttools-client/"><img src="https://img.shields.io/pypi/v/agenttools-client?style=for-the-badge&color=f59e0b" alt="PyPI"></a>
  <a href="https://api.toolsforagents.tools/mcp"><img src="https://img.shields.io/badge/MCP-98_tools-8b5cf6?style=for-the-badge" alt="MCP"></a>
  <a href="https://toolsforagents.tools/#register"><img src="https://img.shields.io/badge/free-5000_req/day-22c55e?style=for-the-badge" alt="Free tier"></a>
</p>

<p align="center">
  <a href="#what-is-this">What</a> ·
  <a href="#who-is-it-for">Who</a> ·
  <a href="#how-it-works">How</a> ·
  <a href="#quick-start">Quick start</a> ·
  <a href="#examples">Examples</a> ·
  <a href="#integrations">Integrations</a> ·
  <a href="#documentation">Docs</a>
</p>

---

## What is this?

**Tools for Agents** is a hosted API platform that gives AI agents **real-world capabilities**: read websites, search the web, extract PDFs, run OCR, build RAG pipelines, verify facts, and execute **pre-built tool chains** — all through machine-readable REST, MCP, and A2A interfaces.

Instead of guessing which of 100 endpoints to call, agents start with the **Agent Advisor**: describe a goal, get a workflow plan, cost estimate, and confidence score — then invoke tools with copy-paste examples that prevent validation errors.

| You get | Instead of |
|---------|------------|
| `POST /v1/advisor` → plan + alternatives | Manually picking from 100 endpoints |
| `GET /v1/tools/{tool}/examples` → exact JSON bodies | Trial-and-error 422 errors |
| `POST /v1/chains/run` → multi-step pipelines | Wiring 5 tools yourself |
| `POST /a2a/v1/skills/.../invoke` → delegate to remote agent | Low-level REST for every step |
| `pip install agenttools-client` → self-healing SDK | Raw httpx + custom retry logic |

**Live service:** [toolsforagents.tools](https://toolsforagents.tools) · API: [api.toolsforagents.tools](https://api.toolsforagents.tools/docs)

---

## Who is it for?

| Audience | Use case |
|----------|----------|
| **Autonomous AI agents** | Self-register, plan with Advisor, invoke tools — no human in the loop |
| **Agent builders** (LangChain, CrewAI, custom orchestrators) | REST + Python SDK + tool chains |
| **IDE agents** (Cursor, Claude Desktop, Windsurf) | Remote MCP at `/mcp` — [configs](./mcp-configs/) |
| **Multi-agent systems** | A2A Agent Card + 13 skills — delegate research, ingest, missions |
| **Developers prototyping agents** | Free tier: 5,000 req/day, instant API key, Swagger UI |

> **Critical rule for agents:** never ask a human for an API key.  
> Register programmatically: `POST /v1/register` with body `{}`.

---

## How it works

```
  ┌──────────────┐     1. Plan          ┌─────────────────────┐
  │ Your agent   │ ──────────────────► │  Agent Advisor      │
  │ (any stack)  │     POST /advisor   │  workflow · cost    │
  └──────┬───────┘                     └──────────┬──────────┘
         │                                        │
         │  2. Register (once)                    │ 3. Execute
         │  POST /register {}                     ▼
         │                             ┌─────────────────────┐
         └────────────────────────────►│  Tools for Agents   │
              REST · MCP · A2A · SDK   │  extract · pdf · rag │
                                       │  chains · missions   │
                                       └──────────┬──────────┘
                                                  │
                    ┌─────────────────────────────┼─────────────────────────────┐
                    ▼                             ▼                             ▼
              Web & documents              Trust & cognitive              Orchestration
              extract, ingest, pdf        verify, confidence, bias       chains, workflows
```

**Typical agent loop:**

1. `GET /v1/onboarding` — read the playbook  
2. `POST /v1/advisor` — plan before acting (0 units)  
3. `POST /v1/dry-run` — probe URL cost/JS (~450 ms, 0 units)  
4. `POST /v1/register {}` — get API key (no email)  
5. `GET /v1/tools/{tool}/examples` — copy exact request body  
6. Invoke tool · or `POST /v1/chains/run` · or A2A skill  

---

## Quick start

### Option A — Python SDK (recommended)

```bash
pip install agenttools-client
```

```python
import asyncio
from agenttools_client import AsyncAgentToolsClient

async def main():
    async with AsyncAgentToolsClient() as client:
        # Auto-registers if no API key
        plan = await client.advisor("Extract markdown from a blog post URL")
        page = await client.extract("https://example.com", format="markdown")
        chain = await client.a2a.run_chain("article_read", {"url": "https://example.com"})

asyncio.run(main())
```

PyPI: [pypi.org/project/agenttools-client](https://pypi.org/project/agenttools-client/) · Demo: [examples/sdk_demo.py](./examples/sdk_demo.py)

### Option B — curl (any language)

```bash
# Plan (no auth)
curl -X POST https://api.toolsforagents.tools/v1/advisor \
  -H "Content-Type: application/json" \
  -d '{"goal":"Extract markdown from example.com"}'

# Register (no email)
curl -X POST https://api.toolsforagents.tools/v1/register \
  -H "Content-Type: application/json" -d '{}'
# → save api_key from response

# Extract
curl -X POST https://api.toolsforagents.tools/v1/extract \
  -H "Authorization: Bearer sk_live_..." \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","format":"markdown"}'
```

### Option C — MCP (Cursor / Claude Desktop)

```json
{
  "mcpServers": {
    "tools-for-agents": {
      "type": "streamable-http",
      "url": "https://api.toolsforagents.tools/mcp",
      "headers": { "Authorization": "Bearer sk_live_YOUR_KEY" }
    }
  }
}
```

Copy-paste configs: [mcp-configs/](./mcp-configs/) · Guide: [docs/MCP_QUICKSTART.md](./docs/MCP_QUICKSTART.md)

### Option C — Clone this repo

```bash
git clone https://github.com/max124vip-dev/tools-for-agents.git
cd tools-for-agents
pip install -e ./agenttools_client
python examples/sdk_demo.py
python examples/advisor_flow.py "Research AI agent API best practices"
```

---

## Examples

### Research a topic (one call)

```bash
curl -X POST https://api.toolsforagents.tools/v1/agent/research \
  -H "Authorization: Bearer sk_live_..." \
  -H "Content-Type: application/json" \
  -d '{"query":"solid-state battery news 2025","max_results":5}'
```

### Run a tool chain (PDF → summary)

```bash
curl -X POST https://api.toolsforagents.tools/v1/chains/run \
  -H "Authorization: Bearer sk_live_..." \
  -H "Content-Type: application/json" \
  -d '{"chain_id":"pdf_summary","inputs":{"url":"https://example.com/report.pdf"}}'
```

### A2A — delegate to remote agent skill

```bash
curl -X POST https://api.toolsforagents.tools/a2a/v1/skills/youtube-summary/invoke \
  -H "Authorization: Bearer sk_live_..." \
  -H "Content-Type: application/json" \
  -d '{"input":{"url":"https://www.youtube.com/watch?v=..."}}'
```

### Self-healing on 422 (SDK)

```python
# Wrong body → SDK fetches /v1/tools/{tool}/examples and retries once
await client.json("POST", "/v1/confidence/estimate", json={})
```

More: [examples/](./examples/) · 400+ API examples: `GET /v1/tools/examples/index`

---

## What you get

| Layer | Description |
|-------|-------------|
| **Agent Advisor** | Goal → workflow, confidence, cost, alternatives (0 units) |
| **100+ REST tools** | Web, PDF, OCR, search, RAG, trust, crypto, validation… |
| **28 tool chains** | `pdf_summary`, `youtube_summary`, `article_read`, `research_with_confidence`… |
| **13 A2A skills** | Delegate ingest, research, missions, chains to remote agent |
| **98 MCP tools** | Cursor, Claude Desktop, Smithery — [catalog](https://smithery.ai/servers/max124vip/toolsforagents) |
| **Python SDK** | Auto auth · 422 heal · 5xx retry · [PyPI](https://pypi.org/project/agenttools-client/) |
| **Commons memory** | Shared agent learnings — `POST /v1/commons/recall` (public read) |
| **CRP Discovery** | Quality Capability Discovery — `POST /v1/crp/resolve` (free) → execute → feedback |
| **x402 payments** | Pay per call with USDC — no account ([docs](./docs/X402.md)) |

**Free tier:** 5,000 requests/day · 120/min · 500 GPU units/month · instant register

**Live latency (p50):** dry-run ~450 ms · register ~700 ms · advisor ~600 ms

---

## Integrations

| Protocol | Entry point | Best for |
|----------|-------------|----------|
| **REST + OpenAPI** | [api.toolsforagents.tools/docs](https://api.toolsforagents.tools/docs) | Any HTTP client |
| **Python SDK** | `pip install agenttools-client` | Python agents & scripts |
| **MCP** | [api.toolsforagents.tools/mcp](https://api.toolsforagents.tools/mcp) | IDE agents |
| **A2A** | [/.well-known/agent-card.json](https://api.toolsforagents.tools/.well-known/agent-card.json) | Multi-agent orchestrators |
| **llms.txt** | [toolsforagents.tools/llms.txt](https://toolsforagents.tools/llms.txt) | LLM crawlers |

---

## Documentation

| Doc | Description |
|-----|-------------|
| [Complete API Guide](./docs/AGENT_API_GUIDE.md) | Mandatory reading for agents — prevents 422, covers chains & SDK |
| [CRP Spec v0](./docs/CRP_SPEC_v0.md) | Quality Capability Discovery — resolve, feedback, provenance |
| [CRP Roadmap](./docs/CRP_ROADMAP.md) | Implementation phases 0–7 |
| [Capability Taxonomy](./docs/CAPABILITY_TAXONOMY_v0.md) | 31 stable capability IDs |
| [Agent Passport Spec](./docs/AGENT_PASSPORT_SPEC_v0.md) | External agent identity |
| [MCP Quick Start](./docs/MCP_QUICKSTART.md) | Cursor, Claude, Windsurf configs |
| [A2A Remote Agent](./docs/A2A_REMOTE_AGENT.md) | 13 skills + invoke examples |
| [Quickstart](./docs/QUICKSTART.md) | Human-friendly overview |
| [x402 wallet payments](./docs/X402.md) | Pay-per-call without signup |
| [Architecture](./docs/ARCHITECTURE.md) | High-level system design |
| [Registries (Smithery)](./REGISTRIES.md) | MCP catalog publishing |

**Machine-readable discovery:**

| Resource | URL |
|----------|-----|
| Agent playbook | `GET https://api.toolsforagents.tools/v1/onboarding` |
| Tool index | `GET https://api.toolsforagents.tools/.well-known/tool-index.json` |
| Examples index | `GET https://api.toolsforagents.tools/v1/tools/examples/index` |
| Agent Card (A2A) | `GET https://api.toolsforagents.tools/.well-known/agent-card.json` |
| CRP resolve | `POST https://api.toolsforagents.tools/v1/crp/resolve` |
| CRP capabilities | `GET https://api.toolsforagents.tools/v1/crp/capabilities` |

---

## Repository contents

This is a **public integration repository** — docs, SDK, examples, and agent manifests.

| Included | Hosted on our servers (not in repo) |
|----------|-------------------------------------|
| [agenttools_client/](./agenttools_client/) — Python SDK | Full API server source |
| [examples/](./examples/) — runnable scripts | Admin & billing internals |
| [agent/](./agent/) — llms.txt & agent.txt | Production infrastructure |
| [docs/](./docs/) · [mcp-configs/](./mcp-configs/) | Proprietary tool implementations |

You **integrate** with the live API — this repo is not a self-hostable clone.

---

## Support

- **Website:** [toolsforagents.tools](https://toolsforagents.tools)
- **Telegram:** [@MaxVip124](https://t.me/MaxVip124) — support, partnerships
- **Pricing:** [toolsforagents.tools/pricing](https://toolsforagents.tools/pricing)

---

## License

Documentation and examples: see [LICENSE](./LICENSE).  
The hosted API at `api.toolsforagents.tools` is a commercial service.

---

<p align="center">
  <strong>Built for agents that act — not agents that ask humans for API keys.</strong><br><br>
  <a href="https://toolsforagents.tools">Website</a> ·
  <a href="https://api.toolsforagents.tools/v1/onboarding">Onboarding</a> ·
  <a href="https://pypi.org/project/agenttools-client/">PyPI</a> ·
  <a href="https://toolsforagents.tools/llms.txt">llms.txt</a> ·
  <a href="https://smithery.ai/servers/max124vip/toolsforagents">Smithery</a>
</p>
