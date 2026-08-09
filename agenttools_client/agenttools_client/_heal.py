"""Self-healing helpers for 422 validation errors."""

from __future__ import annotations

from typing import Any


def _field_paths(fields: list[dict] | None) -> list[str]:
    paths: list[str] = []
    for f in fields or []:
        name = str(f.get("field") or "").strip()
        if not name or name == "body":
            continue
        if name.startswith("body."):
            name = name[5:]
        paths.append(name)
    return paths


def _top_level_keys(paths: list[str]) -> set[str]:
    return {p.split(".")[0] for p in paths if p}


def _has_path(obj: Any, path: str) -> bool:
    cur = obj
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return False
        cur = cur[part]
    if path.endswith("]"):
        return True
    return cur is not None and cur != ""


def _score_example(body: dict, missing_paths: list[str], partial: dict | None) -> int:
    if not missing_paths:
        return len(body)

    score = 0
    tops = _top_level_keys(missing_paths)
    for key in tops:
        if key in body and body[key] not in (None, "", []):
            score += 5

    for path in missing_paths:
        if "." in path and _has_path(body, path):
            score += 3

    if partial:
        for key, value in partial.items():
            if value is not None and value != "" and key in body:
                score += 1

    # Prefer examples that cover all missing top-level keys
    if tops and tops.issubset(set(body.keys())):
        score += 10

    return score


def pick_example_body(
    examples: list[dict],
    partial: dict | None,
    validation_fields: list[dict] | None,
) -> dict | None:
    """Pick the best-matching example body for missing validation fields."""
    missing_paths = _field_paths(validation_fields)
    scored: list[tuple[int, dict]] = []

    for ex in examples:
        req = ex.get("request") or {}
        body = req.get("body")
        if not isinstance(body, dict):
            continue
        score = _score_example(body, missing_paths, partial)
        scored.append((score, body))

    if not scored:
        return None

    scored.sort(key=lambda x: -x[0])
    best_score, best_body = scored[0]
    if missing_paths and best_score <= 0:
        return None

    merged = dict(best_body)
    if partial:
        for key, value in partial.items():
            if value is not None and value != "":
                merged[key] = value
    return merged


def retry_after_seconds(response_json: dict | None, headers: dict[str, str]) -> int:
    if response_json and response_json.get("retry_after_sec") is not None:
        try:
            return max(0, int(response_json["retry_after_sec"]))
        except (TypeError, ValueError):
            pass
    raw = headers.get("Retry-After") or headers.get("retry-after")
    if raw:
        try:
            return max(0, int(raw))
        except ValueError:
            pass
    return 60


def is_retryable_status(status_code: int, response_json: dict | None) -> bool:
    if status_code in (502, 503, 504):
        return True
    if response_json and response_json.get("retryable") is True:
        return True
    return False
