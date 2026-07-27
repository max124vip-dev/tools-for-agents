# Architecture overview

High-level view of **Tools for Agents** — enough to understand the product, without server implementation details.

## Core idea

Most agent platforms offer a **flat tool list**. Tools for Agents adds a **decision layer**:

1. **Discover** — manifests tell agents what exists
2. **Advise** — Agent Advisor proposes a workflow before spending units
3. **Remember** — Commons recalls tips from prior agent runs
4. **Execute** — 58+ tools run against live web, files, and GPU where needed
5. **Feedback** — optional signals improve recommendations over time

## Entry points

| Client | Typical flow |
|--------|----------------|
| Autonomous agent | `onboarding` → `advisor` → `register` → tool calls |
| MCP client (Cursor) | Remote MCP `/mcp` with API key or x402 wallet |
| Human developer | Swagger docs + examples in this repo |

## Authentication modes

| Mode | Best for |
|------|----------|
| **Free API key** | Development, light production (100 units/day) |
| **x402 wallet** | Agents that pay per call in USDC, no account |
| **Paid plans** | Higher limits (see pricing page) |

## Tool categories (conceptual)

- **Content** — extract, pdf, html→markdown, screenshot, crawl
- **Search & RAG** — search, embed, rerank, chunk, retrieve
- **Validation** — email, url, phone
- **Trust & quality** — source credibility, fact verify, bias signals
- **Agent platform** — advisor, dry-run, commons, memory, workflows
- **Crypto / x402** — wallet helpers for agent payments

## Discovery files

Agents should read these **before** browsing HTML marketing pages:

- `GET /v1/onboarding` — step-by-step playbook
- `/.well-known/tool-index.json` — compact tool list
- `/.well-known/capability-intelligence.json` — rich manifest
- `https://toolsforagents.tools/llms.txt` — LLM-oriented index

## Trust properties

- HTTPS production API with public OpenAPI
- Self-register without human in the loop
- Dry-run at 0 units before committing to a plan
- Public examples that run against the live API

## What is not in this repository

The hosted API server (routing, quotas, billing, admin, GPU workers, production deploy) is **proprietary** and runs only on `api.toolsforagents.tools`.

This repo contains **integration docs and examples** so you can connect your agent in minutes.
