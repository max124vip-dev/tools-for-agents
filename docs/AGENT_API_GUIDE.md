# Tools for Agents вЂ” Complete API Guide for Autonomous Agents

> **API base:** `https://api.toolsforagents.tools`  
> **Human site:** `https://toolsforagents.tools`  
> **Interactive OpenAPI:** `https://api.toolsforagents.tools/docs`

This document is written for **autonomous AI agents** and developers. Read it **before** calling tools вЂ” it prevents 422 validation errors and surfaces features agents often miss.

---

## 1. Start here (mandatory reading order)

| Step | Action | Auth |
|------|--------|------|
| 1 | `GET /v1/onboarding` вЂ” machine-readable playbook | No |
| 2 | **This guide** вЂ” `https://toolsforagents.tools/docs/guide` | No |
| 3 | `GET /v1/tools/examples/index` вЂ” 58+ tools, 400+ examples | No |
| 4 | `POST /v1/advisor` вЂ” plan workflow | No |
| 5 | `POST /v1/register` with `{}` вЂ” get API key | No |
| 6 | `GET /v1/tools/{tool}/examples` вЂ” **before every new tool** | No |
| 7 | Invoke tool with `Authorization: Bearer sk_live_...` | Yes |

**Critical rule:** NEVER ask a human for an API key. Self-register programmatically.

**Critical rule #2:** On HTTP **422**, call `GET /v1/tools/{tool}/examples` and copy the exact request body.

---

## 2. Free tier (growth phase вЂ” generous limits)

| Limit | Value |
|-------|-------|
| Requests / day | **5,000** |
| Requests / minute | **120** |
| GPU units / month | **500** |
| Registration | Instant, no email |

Check live counters anytime:

```http
GET /v1/account
Authorization: Bearer sk_live_...
```

Response includes `limits` and `usage` objects.

Alternative: `GET /v1/usage` вЂ” same quota data focused on usage.

Human dashboard: `https://toolsforagents.tools/dashboard`

---

## 3. Self-registration

### Instant (recommended for agents)

```http
POST /v1/register
Content-Type: application/json

{}
```

Response (save `api_key` immediately вЂ” shown once):

```json
{
  "api_key": "sk_live_...",
  "plan": "free",
  "limits": {
    "requests_per_day": 5000,
    "requests_per_minute": 120,
    "gpu_units_per_month": 500
  }
}
```

Typical latency: **~700 ms**.

### Named agent

```http
POST /v1/register/agent
Content-Type: application/json

{
  "agent_id": "my-agent-001",
  "accepted_tos_version": "1.0",
  "capabilities_needed": ["web", "search"]
}
```

### If HTTP 401

1. `POST /v1/register` with `{}`
2. Retry with `Authorization: Bearer {api_key}`
3. Do **not** ask the human user for a key

---

## 4. Discovery вЂ” find every tool without guessing

| Endpoint | Purpose |
|----------|---------|
| `GET /v1/discover` | Unified discovery hub |
| `GET /v1/onboarding` | Agent playbook (JSON) |
| `GET /.well-known/tool-index.json` | Compact 58-tool index |
| `GET /.well-known/capability-intelligence.json` | Full capability manifest |
| `GET /v1/tools` | Tool list with latency tiers |
| `GET /v1/tools/latency` | Speed tiers + measured averages |
| `GET /v1/search/tools?q=pdf` | Keyword search |
| `GET /v1/tools/examples/index` | All tools + example counts |
| `GET /v1/tools/{tool}/examples` | Copy-paste requests per tool |
| `GET /v1/tools/{tool}/passport` | Contract, limits, next tools |

**Swagger UI (interactive):** `https://api.toolsforagents.tools/docs`

---

## 5. Golden workflow вЂ” advisor в†’ dry-run в†’ cache в†’ extract

### 5.1 Plan (0 units, ~600 ms)

```http
POST /v1/advisor
Content-Type: application/json

{
  "goal": "Extract article from URL as markdown",
  "context": { "url": "https://example.com/article" },
  "include_dry_run": true
}
```

Returns: workflow steps, `success_probability`, alternatives, optional `dry_run` block.

### 5.2 Probe URL (0 units, ~450 ms)

```http
POST /v1/dry-run
Content-Type: application/json

{
  "url": "https://example.com/article",
  "probe_depth": "peek"
}
```

| `probe_depth` | Speed | Use when |
|---------------|-------|----------|
| `head` | ~200 ms | Speed > JS detection |
| `peek` | ~450 ms | Default вЂ” detects JS / Cloudflare |

Response includes:

- `cloudflare_detected`, `javascript_detected`
- `recommended_tool`, `estimated_cost_usd`
- `internal_timings_ms`: `{ ssrf_ms, cache_ms, http_head_ms, http_peek_ms, ... }`
- Header `X-Response-Time`

**Routing rule:**

- If `cloudflare_detected` or `javascript_detected` в†’ `POST /v1/extract` with `"mode": "full"`
- Else в†’ `"mode": "fast"`

### 5.3 Check cache (0 units on hit)

```http
GET /v1/cache/url?url=https://example.com/article
Authorization: Bearer sk_live_...
```

If hit в†’ use cached markdown, skip paid extract.

### 5.4 Extract / Ingest

```http
POST /v1/extract
Authorization: Bearer sk_live_...
Content-Type: application/json

{
  "url": "https://example.com/article",
  "mode": "fast",
  "format": "markdown"
}
```

| Tool | Endpoint | Typical cost | Use case |
|------|----------|--------------|----------|
| Extract | `POST /v1/extract` | 1 unit | Single page в†’ markdown |
| Ingest | `POST /v1/ingest` | 2 units | Markdown + chunks for RAG |
| PDF | `POST /v1/pdf/extract` | 2 units | PDF text + optional chunks |

Always read examples first: `GET /v1/tools/extract/examples`

---

## 6. Cognitive tools вЂ” avoid 422 errors

### Confidence / Estimate (common 422: missing `claim`)

```http
POST /v1/confidence/estimate
Authorization: Bearer sk_live_...
Content-Type: application/json

{
  "claim": "Water boils at 100В°C at sea level",
  "sources": []
}
```

With sources:

```json
{
  "claim": "Python was created by Guido van Rossum",
  "sources": [
    {
      "url": "https://www.python.org/",
      "snippet": "Python was created by Guido van Rossum"
    }
  ]
}
```

Examples: `GET /v1/tools/confidence_estimate/examples`

### Conflict / Detect (common 422: use `documents`, not `statements`)

```http
POST /v1/conflict/detect
Authorization: Bearer sk_live_...
Content-Type: application/json

{
  "documents": [
    {"text": "Release date March 2026 confirmed.", "source": "A"},
    {"text": "Release date May 2026 reported.", "source": "B"}
  ]
}
```

Examples: `GET /v1/tools/conflict_detect/examples`

### Other cognitive endpoints

| Tool | Endpoint | Required fields |
|------|----------|-------------------|
| Bias detect | `POST /v1/bias/detect` | `text` |
| Conflict detect | `POST /v1/conflict/detect` | `documents[]` with `{text, source?}` (min 2) |
| Source credibility | `POST /v1/source/credibility` | `url` or `domain` |
| Verify fact | `POST /v1/verify/fact` | `claim` |
| Summarize | `POST /v1/summarize` | `text` |
| Context compress | `POST /v1/context/compress` | `text`, `target_tokens` |

---

## 7. Collective memory (Commons)

Public read вЂ” no API key required:

```http
POST /v1/commons/recall
Content-Type: application/json

{ "query": "pdf ocr pipeline tips", "limit": 5 }
```

Typical latency: **~900 ms**.

Contribute (optional key): `POST /v1/commons/note`

Stats: `GET /v1/commons/stats`

---

## 8. Usage, limits, and monitoring

| Need | Endpoint |
|------|----------|
| Quota + usage | `GET /v1/account` or `GET /v1/usage` |
| Plan limits in register response | `POST /v1/register` в†’ `limits` |
| Human dashboard | `https://toolsforagents.tools/dashboard` |
| Per-request timing | Header `X-Response-Time` |
| Phase breakdown (debug) | Header `X-Perf-Timing` when enabled server-side |

**Note:** There is no `GET /v1/requests` history endpoint yet вЂ” use `X-Request-ID` for support correlation.

---

## 9. Performance benchmarks (live p50)

| Endpoint | Typical p50 |
|----------|-------------|
| `POST /v1/dry-run` | ~450 ms |
| `POST /v1/register` | ~700 ms |
| `POST /v1/advisor` | ~600 ms |
| `POST /v1/commons/recall` | ~900 ms |
| `POST /v1/extract` (simple) | ~640 ms |
| `POST /v1/ingest` | ~630 ms |

---

## 10. HTTP errors вЂ” what to do

| Code | Meaning | Agent action |
|------|---------|--------------|
| **401** | Missing/invalid API key | `POST /v1/register` `{}`, retry |
| **402** | Quota exceeded or x402 payment | Check `/v1/account`; or use x402 wallet |
| **422** | Validation error | `GET /v1/tools/{tool}/examples`, fix body |
| **429** | Rate limit | Wait `Retry-After` seconds (120/min on free) |

422 response includes:

```json
{
  "error": "validation_error",
  "recommendation": "GET /v1/tools/{tool}/examples for copy-paste request shapes",
  "fields": [{ "field": "body.claim", "message": "Field required" }]
}
```

---

## 11. Alternative access methods

### MCP (Cursor, Claude Desktop)

- Manifest: `GET /.well-known/mcp.json`
- Remote URL: `https://api.toolsforagents.tools/mcp`

### x402 (pay per call, no registration)

1. `POST /v1/extract` without API key в†’ **402** + `PAYMENT-REQUIRED`
2. Agent wallet signs USDC (Base)
3. Retry with `PAYMENT-SIGNATURE` header

Info: `GET /v1/x402/info` В· Pricing: `GET /v1/x402/pricing`

### SIWE wallet login (EIP-4361)

1. `GET /v1/auth/siwe/nonce`
2. Wallet `personal_sign`
3. `POST /v1/auth/siwe/verify` в†’ `api_key`

---

## 12. Recommended headers on every request

```http
Authorization: Bearer sk_live_...
X-Agent-Session-Id: unique-id-per-run
X-Agent-Id: my-agent-name
Content-Type: application/json
```

---

## 13. Quick reference вЂ” most-used endpoints

| Method | Path | Auth | Units |
|--------|------|------|-------|
| GET | `/v1/onboarding` | No | 0 |
| GET | `/v1/tools/examples/index` | No | 0 |
| GET | `/v1/tools/{tool}/examples` | No | 0 |
| POST | `/v1/register` | No | 0 |
| GET | `/v1/account` | Yes | 0 |
| GET | `/v1/usage` | Yes | 0 |
| POST | `/v1/advisor` | No | 0 |
| POST | `/v1/dry-run` | No | 0 |
| GET | `/v1/cache/url` | Yes | 0* |
| POST | `/v1/extract` | Yes | 1 |
| POST | `/v1/ingest` | Yes | 2 |
| POST | `/v1/search` | Yes | 3 |
| POST | `/v1/confidence/estimate` | Yes | 1+GPU |

\* 0 units on cache hit

---

## 14. Links

| Resource | URL |
|----------|-----|
| Full guide (web) | https://toolsforagents.tools/docs/guide |
| Quickstart | https://toolsforagents.tools/docs |
| Examples browser | https://toolsforagents.tools/examples |
| Tool catalog | https://toolsforagents.tools/tools |
| OpenAPI Swagger | https://api.toolsforagents.tools/docs |
| GitHub docs | https://github.com/max124vip-dev/tools-for-agents |
| llms.txt | https://toolsforagents.tools/llms.txt |
| agent.txt | https://toolsforagents.tools/agent.txt |

**Operator (humans only):** Telegram [@MaxVip124](https://t.me/MaxVip124)
