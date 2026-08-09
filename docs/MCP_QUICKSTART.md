# MCP Server Quick Start

Connect **Tools for Agents** to Cursor, Claude Desktop, Windsurf, or Cline in under 2 minutes.

| | |
|---|---|
| **MCP URL** | `https://api.toolsforagents.tools/mcp` |
| **MCP tools** | 44 (curated agent workflows) |
| **Full REST API** | 58+ tools — [OpenAPI](https://api.toolsforagents.tools/docs) |
| **Free tier** | **5,000 req/day** · 120/min · 500 GPU units/month |
| **API key** | `POST /v1/register` with `{}` — no email (~0.7s) |

Copy-paste configs: [`mcp-configs/`](../mcp-configs/)

---

## Step 1 — Get a free API key

```bash
curl -X POST https://api.toolsforagents.tools/v1/register \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## Option 1: Remote MCP (recommended)

File: `~/.cursor/mcp.json` or `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "tools-for-agents": {
      "type": "streamable-http",
      "url": "https://api.toolsforagents.tools/mcp",
      "headers": {
        "Authorization": "Bearer sk_live_YOUR_KEY"
      }
    }
  }
}
```

See [mcp-configs/](../mcp-configs/) for Windsurf, Cline, Smithery variants.

---

## Tool counts

- **44 MCP tools** at `/mcp` (Smithery scans this)
- **58+ REST tools** — advisor, dry-run, cognitive tools via REST

Full guide: [AGENT_API_GUIDE.md](./AGENT_API_GUIDE.md)
