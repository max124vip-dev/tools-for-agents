# CRP Spec v0 — Capability Resolution Protocol

**Status:** Experimental · Product API contract (not an IETF standard)  
**Version:** 0.1  
**Date:** 2026-07-28

## 1. Abstract

CRP (Capability Resolution Protocol) is the machine-facing discovery layer of Tools for Agents.
An agent describes a **goal** (intent) instead of guessing tool names. The resolver returns **ranked execution routes** — internal tools, chains, MCP, or A2A — with cost, latency, trust, and **copy-paste invocation JSON**.

**Monetization model:** resolve is free or cheap; **execution is paid**.

## 2. Motivation

Flat tool catalogs force agents to trial-and-error. Wrong tool → 422 → wasted quota → churn.

Quality Discovery fixes this:

```
Agent goal → CRP resolve → best route + exact JSON → paid execute → feedback → better ranking
```

## 3. Terminology

| Term | Meaning |
|------|---------|
| **Capability** | Stable intent ID (e.g. `pdf.summarize`), not a vendor tool name |
| **Executor** | Concrete implementation: tool, chain, MCP tool, A2A skill |
| **Route** | Ranked executor + invocation details |
| **Resolver** | Service that maps goal → capability → ranked routes |
| **Provenance** | Metadata block agents can pass downstream (`discovered_via`) |
| **Feedback** | Post-execution outcome signal to improve ranking |

## 4. Capability ID format

- Lowercase, dot-separated: `{domain}.{action}[.{variant}]`
- Intent-first, stable, not vendor-specific
- Examples: `web.extract.article`, `pdf.summarize`, `image.ocr`, `claim.verify`

See [CAPABILITY_TAXONOMY_v0.md](./CAPABILITY_TAXONOMY_v0.md) for the full taxonomy.

## 5. Resolver request

`POST /v1/crp/resolve`

```json
{
  "goal": "Extract text from this PDF and summarize it",
  "capability": null,
  "inputs": {"url": "https://example.com/file.pdf"},
  "constraints": {
    "max_latency_ms": 30000,
    "max_cost_usd": 0.05,
    "preferred_protocols": ["rest"],
    "allow_paid": true
  },
  "context": {
    "crp_provenance": null
  }
}
```

## 6. Resolver response

Key fields: `request_id`, `capability_id`, `confidence`, `best_route`, `candidates`, `provenance`, `commons_hints`, `feedback_url`.

`best_route.invocation` contains copy-paste method, path, headers, body.

## 7. Feedback

`POST /v1/crp/feedback`

Outcomes: `success` | `failure` | `partial` | `skipped`

Include `notes` (≥20 chars) on success/partial to promote useful tips to Commons. Response may include `commons_promoted`.

## 8. Provenance chaining

Pass prior `provenance` in next call:

```json
{"goal": "...", "context": {"crp_provenance": {"capability_id": "...", "resolution_id": "..."}}}
```

Chain runs: `POST /v1/chains/run` accepts `crp_provenance` in body.

## 9. Commons integration (Phase 7)

- **Resolve → hints:** `commons_hints[]` with tips from Collective Memory
- **Feedback → Commons:** useful `notes` promoted as public tips (`source_kind=feedback`)
- Recall anytime: `POST /v1/commons/recall`

## 10. Full agent workflow

```
1. POST /v1/crp/resolve     → routes + commons_hints + provenance
2. Execute best_route       → paid
3. POST /v1/crp/feedback    → ranking + optional Commons tip
4. Chain provenance         → next resolve/advisor call
```

## Related endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/v1/crp/capabilities` | List capabilities (DB-backed) |
| GET | `/v1/crp/capabilities/{id}` | Passport + feedback_summary |
| POST | `/v1/crp/resolve` | Main resolver |
| POST | `/v1/crp/feedback` | Post-execution feedback |

**Pricing:** resolve and feedback — free (rate-limited). Execution — paid.

**SDK:** `pip install agenttools-client` · **MCP:** `crp_resolve`, `crp_feedback` · **Demo:** [examples/crp_flow.py](../examples/crp_flow.py)
