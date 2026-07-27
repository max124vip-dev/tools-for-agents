# Quickstart

## For autonomous AI agents — read in order

1. **Full guide (mandatory):** [AGENT_API_GUIDE.md](./AGENT_API_GUIDE.md) or https://toolsforagents.tools/docs/guide
2. Playbook: `GET https://api.toolsforagents.tools/v1/onboarding`
3. Examples index: `GET /v1/tools/examples/index` — **call before every new POST**
4. Plan: `POST /v1/advisor` with `{"goal":"..."}`
5. Register: `POST /v1/register` with `{}`
6. Swagger: https://api.toolsforagents.tools/docs

**Never ask a human for an API key.**

**On 422:** `GET /v1/tools/{tool}/examples` and copy the exact body.

## Free tier (growth phase)

| Limit | Value |
|-------|-------|
| Requests / day | **5,000** |
| Requests / minute | **120** |
| GPU units / month | **500** |

Check usage: `GET /v1/account` with Bearer token.

## For developers (Python)

```bash
pip install -r examples/requirements.txt
python examples/agent_onboarding.py
```

```bash
export AGENTTOOLS_API_KEY=sk_live_...
python examples/advisor_flow.py "Extract text from https://example.com"
```

Instant key:

```bash
curl -X POST https://api.toolsforagents.tools/v1/register \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Key endpoints agents miss

| Need | Endpoint |
|------|----------|
| Swagger / OpenAPI | https://api.toolsforagents.tools/docs |
| Usage & limits | `GET /v1/account` |
| Cached extract (0 units) | `GET /v1/cache/url?url=...` |
| Examples per tool | `GET /v1/tools/{tool}/examples` |
| Dry-run probe | `POST /v1/dry-run` |

## MCP & x402

- MCP: [MCP.md](./MCP.md) — remote `https://api.toolsforagents.tools/mcp`
- x402: [X402.md](./X402.md) — pay per call without registration

## Next steps

- [Complete API Guide](./AGENT_API_GUIDE.md)
- [API reference](./API.md)
- [Examples](../examples/README.md)
