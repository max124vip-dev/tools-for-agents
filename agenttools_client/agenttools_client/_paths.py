"""Map REST paths to tool names for examples lookup."""

from __future__ import annotations

import re

# Known multi-segment paths → tool name (longest match first)
_PATH_TO_TOOL: dict[str, str] = {
    "confidence/estimate": "confidence_estimate",
    "conflict/detect": "conflict_detect",
    "bias/detect": "bias_detect",
    "source/credibility": "source_credibility",
    "verify/fact": "verify_fact",
    "context/compress": "context_compress",
    "search/read": "search_read",
    "agent/research": "agent_research",
    "pdf/extract": "pdf",
    "pdf/metadata": "pdf_metadata",
    "youtube/transcript": "youtube_transcript",
    "cache/url": "cache_url",
    "recommend/tool": "recommend_tool",
    "commons/recall": "commons_recall",
    "commons/note": "commons_note",
    "workflow/run": "workflow_run",
    "workflow/stateful": "workflow_stateful",
    "fallback/chain": "fallback_chain",
    "chains/run": "chains_run",
    "extract/tables": "table_extract",
    "diff/url": "diff_url",
    "sitemap/parse": "sitemap_parse",
    "feed/parse": "feed_parse",
    "crypto/invoke": "crypto",
    "base64/encode": "base64_encode",
    "base64/decode": "base64_decode",
}

_EXTENDED_RE = re.compile(r"^extended/([a-z0-9_/-]+)$", re.I)


def infer_tool_from_path(path: str) -> str | None:
    """Best-effort tool name from POST path, e.g. /v1/extract → extract."""
    p = path.split("?", 1)[0].strip("/")
    if p.startswith("v1/"):
        p = p[3:]
    if not p:
        return None

    if p in _PATH_TO_TOOL:
        return _PATH_TO_TOOL[p]

    m = _EXTENDED_RE.match(p)
    if m:
        return m.group(1).replace("-", "_").replace("/", "_")

    for key, tool in sorted(_PATH_TO_TOOL.items(), key=lambda x: -len(x[0])):
        if p == key or p.endswith("/" + key):
            return tool

    parts = p.split("/")
    if len(parts) == 1:
        return parts[0].replace("-", "_")
    return "_".join(parts).replace("-", "_")
