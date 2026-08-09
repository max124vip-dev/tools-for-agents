"""Client exceptions."""

from __future__ import annotations

from typing import Any


class AgentToolsClientError(Exception):
    """Base SDK error."""

    def __init__(self, message: str, *, status_code: int | None = None, detail: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail


class AgentToolsHTTPError(AgentToolsClientError):
    """Non-retryable HTTP error from the API."""


class AgentToolsRetryExhausted(AgentToolsClientError):
    """Retries exhausted for retryable errors."""
