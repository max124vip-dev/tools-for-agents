# Tools for Agents — Examples

**Decision Layer for AI Agents** — don't pick from 58 tools manually. Call **Advisor** first.

Production API: `https://api.toolsforagents.tools`  
Docs: https://toolsforagents.tools/docs  
LLM file: https://toolsforagents.tools/llms.txt

## Quick start (no API key)

```bash
pip install -r examples/requirements.txt
python examples/advisor_flow.py
python examples/advisor_flow.py "Need OCR for a scanned invoice"
```

Flow:

```
discover → commons recall → advisor → remember → examples → (optional) invoke → feedback
```

## With API key (invoke step)

```bash
export AGENTTOOLS_API_KEY=sk_live_...
python examples/advisor_flow.py "Read https://example.com as markdown"
```

Register free key: https://toolsforagents.tools/#register  
Or autonomous agent:

```bash
curl -X POST https://api.toolsforagents.tools/v1/register/agent \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"my-bot-001","accepted_tos_version":"1.0"}'
```

## Files

| File | Description |
|------|-------------|
| `advisor_flow.py` | End-to-end agent flow (recommended start) |
| `sdk_demo.py` | Reference Python SDK demo (`pip install agenttools-client`) |
| `langchain_extract.py` | LangChain + extract tool |
| `langchain_js.md` | JavaScript / LangChain notes |

## Machine-readable discovery

| URL | Purpose |
|-----|---------|
| `GET /.well-known/tool-index.json` | Compact 58-tool index |
| `GET /.well-known/capability-intelligence.json` | Full onboarding |
| `POST /v1/advisor` | Plan + `remember{}` block |
| `POST /v1/commons/recall` | Collective memory |
| `GET /v1/platform/stats` | Success rate, latency |

## Local API

```bash
export AGENTTOOLS_API_URL=http://127.0.0.1:8000
python examples/advisor_flow.py
```

## MCP

Remote MCP: `https://api.toolsforagents.tools/mcp`  
Manifest: `deploy/discovery/mcp-server.json`

## Feedback

After a run, the script sends optional feedback (`POST /v1/feedback`) so the platform can learn. Disable by editing `advisor_flow.py`.

## License

Same as main repository.
