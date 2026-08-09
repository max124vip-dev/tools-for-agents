# CRP Roadmap — Quality Capability Discovery

Tools for Agents is evolving from a flat tool catalog to **Quality Capability Discovery**:

```
resolve intent → ranked routes → paid execution → feedback
```

## Phase 0 — Language & docs ✅

- [x] `CRP_SPEC_v0.md` — API contract
- [x] `CAPABILITY_TAXONOMY_v0.md` — 31 capability IDs
- [x] `CRP_ROADMAP.md` — this file
- [x] `AGENT_PASSPORT_SPEC_v0.md`

## Phase 1 — CRP v0 resolver ✅

- [x] `POST /v1/crp/resolve` — internal tools + chains
- [x] `GET /v1/crp/capabilities` — catalog
- [x] `POST /v1/crp/feedback` — DB-backed store
- [x] MCP tool `crp_resolve`
- [x] Ranking from telemetry feedback loop (≥3 samples)

## Phase 2 — Agent Passport + feedback DB ✅

- [x] DB models + passport API
- [x] Feedback aggregates affect CRP ranking
- [x] `register/agent` returns `passport_url` + `crp_resolve_url`

## Phase 3 — Provenance propagation ✅

- [x] Provenance in advisor, chains, A2A, MCP
- [x] A2A skill `resolve-capability`

## Phase 4 — SDK & MCP polish ✅

- [x] Python SDK `client.crp.*` v0.3.0
- [x] MCP `crp_resolve` + `crp_feedback`
- [x] `examples/crp_flow.py`

## Phase 5 — DB-backed Capability Registry ✅

- [x] DB registry + admin CRUD + seed script

## Phase 6 — Self-learning feedback loop ✅

- [x] Auto-telemetry, trust score v0, anti-gaming

## Phase 7 — Commons integration ✅

- [x] Feedback notes → Commons promotion
- [x] `commons_hints` in resolve responses

## North star

**Best Capability Discovery for agents** — free resolve, paid execute, measurable conversion from resolve → successful invoke.

See [CRP_SPEC_v0.md](./CRP_SPEC_v0.md) for the API contract.
