"""LangChain example — AgentTools extract tool.

Install:
  pip install langchain langchain-openai httpx

Set:
  AGENTTOOLS_API_KEY=sk_live_...
  AGENTTOOLS_API_URL=http://127.0.0.1:8000  (optional)
  OPENAI_API_KEY=...  (for the agent LLM)
"""

from __future__ import annotations

import os

import httpx
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

API_URL = os.environ.get("AGENTTOOLS_API_URL", "http://127.0.0.1:8000").rstrip("/")
API_KEY = os.environ.get("AGENTTOOLS_API_KEY", "")


@tool
def extract_webpage(url: str) -> str:
    """Extract clean markdown text from a webpage URL using AgentTools API."""
    if not API_KEY:
        return "Error: set AGENTTOOLS_API_KEY"
    with httpx.Client(timeout=60) as client:
        response = client.post(
            f"{API_URL}/v1/extract",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"url": url, "format": "markdown"},
        )
        response.raise_for_status()
        data = response.json()
        return data.get("markdown") or data.get("text") or ""


@tool
def validate_email_address(email: str) -> str:
    """Validate an email address (MX records, disposable check)."""
    if not API_KEY:
        return "Error: set AGENTTOOLS_API_KEY"
    with httpx.Client(timeout=30) as client:
        response = client.post(
            f"{API_URL}/v1/validate/email",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"email": email},
        )
        response.raise_for_status()
        return str(response.json())


def main() -> None:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    tools = [extract_webpage, validate_email_address]
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a research assistant with web extract tools."),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )
    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    result = executor.invoke(
        {"input": "Extract the main text from https://example.com and summarize it."}
    )
    print(result["output"])


if __name__ == "__main__":
    main()
