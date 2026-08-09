# Agent Protocols — OAuth MCP, SIWE, Commerce, Trust

Updated: 2026-07-26

Machine-readable discovery for autonomous agents and MCP scanners (Smithery, Glama, registry fuzzers).

**Production base:** `https://api.toolsforagents.tools`

---

## Will scanners "see" the service?

| What | Before | After (2026-07-26) |
|------|--------|---------------------|
| `GET /.well-known/oauth-protected-resource` | 404 | **200** — RFC 9728 JSON |
| `GET /.well-known/oauth-authorization-server` | 404 | **200** — RFC 8414 JSON |
| `GET /.well-known/glama.json` | 404 | **200** |
| MCP `/mcp/` trailing slash | 405/500 | **406** (valid MCP) |
| Glama / PulseMCP catalog listing | manual | **manual** — submit still required |

**Summary:** technical scanners stop getting 404 on OAuth/MCP metadata and can read auth flows (instant register, SIWE, x402). **Catalog listing** is a separate step — see main repo `docs/DISCOVERY_SUBMIT_GUIDE.md`.

Verify after deploy:

```bash
curl -s https://api.toolsforagents.tools/.well-known/oauth-protected-resource
curl -s https://api.toolsforagents.tools/.well-known/oauth-authorization-server
curl -s https://api.toolsforagents.tools/v1/discover
```

---

## 1. OAuth 2.1 for MCP

| Endpoint | Standard | Purpose |
|----------|----------|---------|
| `GET /.well-known/oauth-protected-resource` | RFC 9728 | MCP resource + scopes + alternative auth |
| `GET /.well-known/oauth-protected-resource/mcp` | RFC 9728 | Same, resource = `/mcp` |
| `GET /.well-known/oauth-authorization-server` | RFC 8414 | Issuer, registration, SIWE hints |

**Auth paths:**

1. **Instant API key** — `POST /v1/register` `{}` → `Authorization: Bearer sk_live_...`
2. **SIWE (EIP-4361)** — wallet sign-in → `api_key`
3. **x402** — pay-per-call USDC

**MCP endpoint:** `https://api.toolsforagents.tools/mcp`

---

## 2. SIWE (EIP-4361)

| Step | Method | URL |
|------|--------|-----|
| Nonce | GET | `/v1/auth/siwe/nonce` |
| Sign | wallet | `personal_sign` |
| Login | POST | `/v1/auth/siwe/verify` |
| Handshake | POST | `/v1/auth/siwe/verify-handshake` |

`SIWE_RPC_URL` on server — only for EIP-1271 smart wallets (Safe, Coinbase Smart Wallet). Read-only RPC, no gas.

---

## 3. Agent Trust

```http
POST /v1/trust/verify-handshake
{ "message": "<SIWE>", "signature": "0x..." }
```

Returns wallet reputation (`score`, `tier`, tool call history). Public — no auth.

---

## 4. Commerce hints

- `GET /.well-known/ucp.json` — UCP hints
- `GET /.well-known/ap2.json` — AP2 / x402 hints

---

## Machine-readable index

```text
GET  /.well-known/oauth-protected-resource
GET  /.well-known/oauth-authorization-server
GET  /.well-known/mcp.json
GET  /.well-known/ucp.json
GET  /.well-known/ap2.json
GET  /v1/onboarding
POST /v1/register {}
GET  /v1/auth/siwe/nonce
POST /v1/auth/siwe/verify
POST /v1/trust/verify-handshake
```

Site: `https://toolsforagents.tools/llms.txt` · `agent.txt` · `/.well-known/agent-discovery.json`
