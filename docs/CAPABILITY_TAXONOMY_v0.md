# Capability Taxonomy v0

Stable capability IDs for Tools for Agents CRP Quality Discovery.

See live catalog: `GET /v1/crp/capabilities`

**Rules:** lowercase · dot-separated · intent-first · not vendor-specific · stable across releases

## Domains

| Domain | Scope |
|--------|-------|
| `web.*` | URLs, pages, search, feeds, sitemaps |
| `pdf.*` | PDF extract, summarize, RAG, Q&A |
| `image.*` | OCR, vision, tables |
| `audio.*` | Transcription |
| `video.*` | YouTube / video captions |
| `text.*` | Summarize, translate, chunk, embed |
| `data.*` | CSV, JSON parsing |
| `trust.*` | Fact check, source credibility |
| `agent.*` | Multi-step research agents |

## Examples

| ID | Intent |
|----|--------|
| `pdf.summarize` | Extract PDF and summarize |
| `image.ocr` | OCR text from image URL |
| `web.search` | Web search results |
| `claim.verify` | Multi-source fact verification |
| `agent.research` | Deep research pipeline |

Full list (31 IDs): `GET /v1/crp/capabilities` · Spec: [CRP_SPEC_v0.md](./CRP_SPEC_v0.md)
