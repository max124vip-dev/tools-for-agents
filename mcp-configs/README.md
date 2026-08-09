# MCP client configs — copy-paste for Cursor, Claude Desktop, Windsurf, Cline

Ready-to-use snippets for **Tools for Agents** remote MCP.

**Endpoint:** `https://api.toolsforagents.tools/mcp`  
**Get API key (free, ~0.7s):**

```bash
curl -X POST https://api.toolsforagents.tools/v1/register \
  -H "Content-Type: application/json" -d '{}'
```

**Free tier:** 5,000 req/day · 120 req/min · 500 GPU units/month

Replace `sk_live_YOUR_KEY` in every file below.

| File | Platform |
|------|----------|
| [cursor-remote-http.json](./cursor-remote-http.json) | **Cursor** (recommended — no local Python) |
| [cursor-stdio-local.json.example](./cursor-stdio-local.json.example) | Cursor dev (local API + `mcp/server.py`) |
| [claude-desktop-remote-http.json](./claude-desktop-remote-http.json) | Claude Desktop (streamable HTTP) |
| [claude-desktop-smithery.json](./claude-desktop-smithery.json) | Claude Desktop via Smithery proxy |
| [windsurf.json](./windsurf.json) | Windsurf |
| [cline.json](./cline.json) | Cline (VS Code) |

Full guide: [docs/MCP_QUICKSTART.md](../docs/MCP_QUICKSTART.md)

## Tool counts (important)

| Layer | Count | Notes |
|-------|-------|-------|
| **Remote MCP** | **44 tools** | What Smithery scans at `/mcp` |
| **REST API** | **58+ tools** | Full platform — `GET /v1/tools` |
| **Request examples** | **400+** | `GET /v1/tools/examples/index` |

Use MCP for common agent workflows; use REST for advisor, dry-run, confidence/estimate, and other tools not yet on MCP.

## Smithery (optional)

Catalog: https://smithery.ai/servers/max124vip/toolsforagents

```bash
npx -y @smithery/cli@latest mcp add max124vip/toolsforagents
```

Direct remote MCP (no Smithery CLI) is usually simpler — see `cursor-remote-http.json`.
