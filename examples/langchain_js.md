# AgentTools + LangChain (JavaScript)

Use the OpenAI SDK or LangChain.js with a custom tool that calls AgentTools REST API.

```javascript
const API_URL = process.env.AGENTTOOLS_API_URL || "http://127.0.0.1:8000";
const API_KEY = process.env.AGENTTOOLS_API_KEY;

async function extractUrl(url) {
  const res = await fetch(`${API_URL}/v1/extract`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ url, format: "markdown" }),
  });
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  return data.markdown || data.text;
}

// LangChain.js dynamic tool (v0.3+)
import { tool } from "@langchain/core/tools";
import { z } from "zod";

export const extractWebpage = tool(
  async ({ url }) => extractUrl(url),
  {
    name: "extract_webpage",
    description: "Extract markdown from a URL via AgentTools API",
    schema: z.object({ url: z.string().url() }),
  }
);
```

See also: [Python example](./langchain_extract.py)
