# Registry publishing

Where **Tools for Agents** is listed so AI agents and MCP clients can discover the service.

**Full reference (private repo):** `docs/AGENT_DISCOVERY_REGISTRIES.md` in the main project at `D:\Web4`.

---

## Published registries

| Registry | Status | ID / link | Connect |
|----------|--------|-----------|---------|
| [MCP Registry](https://registry.modelcontextprotocol.io) | ✅ v0.1.0 | `io.github.max124vip-dev/tools-for-agents` | MCP `https://api.toolsforagents.tools/mcp` + `Authorization: Bearer {key}` |
| [Smithery](https://smithery.ai/servers/max124vip/toolsforagents) | ✅ Public | `max124vip/toolsforagents` | **44 MCP tools** · REST 58+ · [MCP configs](../mcp-configs/) · free 5,000 req/day |
| [GitHub](https://github.com/max124vip-dev/tools-for-agents) | ✅ Live | `max124vip-dev/tools-for-agents` | This repo — docs, examples, manifests (no server source) |

### Get a free API key (for MCP auth)

```bash
curl -X POST https://api.toolsforagents.tools/v1/register \
  -H "Content-Type: application/json" \
  -d "{}"
```

---

## Live discovery (no registry needed)

Agents can find the service directly:

| URL | Purpose |
|-----|---------|
| https://api.toolsforagents.tools/v1/onboarding | Start here — playbook + smithery/github links |
| https://api.toolsforagents.tools/v1/discover | Discovery hub |
| https://api.toolsforagents.tools/.well-known/mcp.json | MCP manifest |
| https://api.toolsforagents.tools/.well-known/oauth-protected-resource | MCP OAuth (RFC 9728) |
| https://api.toolsforagents.tools/.well-known/oauth-authorization-server | OAuth server metadata |
| https://api.toolsforagents.tools/.well-known/ucp.json | Commerce hints (UCP) |
| https://api.toolsforagents.tools/.well-known/ap2.json | Payment hints (AP2/x402) |
| https://api.toolsforagents.tools/v1/auth/siwe/nonce | SIWE wallet login |
| https://api.toolsforagents.tools/v1/trust/verify-handshake | Public trust + reputation |
| https://api.toolsforagents.tools/.well-known/tool-index.json | ~58 tools |
| https://toolsforagents.tools/llms.txt | LLM-friendly index |
| https://toolsforagents.tools/agent.txt | Short agent manifest |
| https://toolsforagents.tools/.well-known/agent-discovery.json | Site → API pointers |

---

## MCP Registry (republish)

In the private/full repo (`D:\Web4`):

```powershell
11_setup_mcp_registry.bat
13_login_mcp_registry.bat
12_publish_mcp_registry.bat
```

Manifest: [`discovery/mcp-server.json`](./discovery/mcp-server.json) (copy of `deploy/discovery/server.json`)

Verify:

```bash
curl "https://registry.modelcontextprotocol.io/v0.1/servers?search=tools-for-agents"
```

---

## Smithery

- **Catalog:** https://smithery.ai/servers/max124vip/toolsforagents
- **MCP URL:** `https://api.toolsforagents.tools/mcp`
- **Auth:** `Authorization: Bearer sk_live_...` or `X-API-Key`
- **Public listing:** Smithery → Settings → General → uncheck **Unlisted** → Save

Copy-paste texts: `deploy/discovery/SMITHERY_SUBMIT.txt` in the main repo.

---

## Not yet listed

Glama, RapidAPI, LangChain docs, Google Search Console — see `docs/DISCOVERY_GROWTH.txt` in the main repo.
