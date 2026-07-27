"""Reference Python client for Tools for Agents API."""

from agenttools_client.a2a import A2AClient
from agenttools_client.client import AgentToolsClient, AsyncAgentToolsClient
from agenttools_client._errors import (
    AgentToolsClientError,
    AgentToolsHTTPError,
    AgentToolsRetryExhausted,
)

__all__ = [
    "AgentToolsClient",
    "AsyncAgentToolsClient",
    "A2AClient",
    "AgentToolsClientError",
    "AgentToolsHTTPError",
    "AgentToolsRetryExhausted",
]

__version__ = "0.2.0"
