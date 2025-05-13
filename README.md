# 🧠 Research Bot

A conversational research assistant built with [MCP Tools], `langchain-mcp-adapters`, and Redis. This bot helps retrieve and summarize information using web search, with support for streaming interactions and short-term memory.

---

## 🚀 Features

* ✅ Uses MCP tools for structured conversation flows
* 🔌 Integrates `langchain-mcp-adapters` for enhanced LLM tooling
* 🧠 Implements Redis-backed short-term memory checkpointer
* 📊 Tracks session logs and metrics with [Langfuse](https://www.langfuse.com/)
* 🔍 Web search powered via LangSearch API
* 🔀 Real-time interaction using SSE (Server-Sent Events) and Starlette

---

## 🛠️ Tech Stack

* **Python** with `FastMCP`, `uvicorn`, `Starlette`
* **Redis** as the memory store (short-term memory)
* **Langfuse** for observability
* **LangChain MCP Adapters** for custom tooling
* **LangSearch API** for research queries

---

## 📦 Setup

1. **Clone the repo:**

```bash
git clone git@github.com:karthikzzzzzzz/Research-Bot.git
cd Research-Bot
```

2. **Install dependencies:**

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Environment Variables:**

Create a `.env` file and add:

```env
REDIS_URI=redis://localhost:6379
LANGSEARCH_API_KEY=your_api_key
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
```

4. **Run the server:**

```bash
uvicorn main:app --reload
```

The bot will be available at:
📍 `http://localhost:8000/sse`

---

## 📁 Project Structure

```bash
.
├── main.py               # Entry point for the app
├── server.py             # SSE and MCP server setup
├── services.py           # Tool/service integration
├── schema.py             # Schemas for tool input/output
├── .env                  # Environment variables
├── requirements.txt
└── README.md
```

---

## 📊 Monitoring with Langfuse

All tool usage and LLM traces are logged via Langfuse.

* Visit [Langfuse dashboard](https://cloud.langfuse.com/) to monitor the sessions.
* Supports linking user IDs and session metadata.

---

## 🧹 MCP Tooling

Custom research tools are registered using MCP decorators:

```python
@mcp.tool()
def research_tool(query: str) -> str:
    ...
```

---

## 🧠 Memory

Memory is powered by Redis using:

* **Checkpointer**: to resume short-term memory between sessions
* Easy to swap with `InMemoryCheckpointer` or database-backed persistence

---

## 🧪 Coming Soon

* 🔐 Auth and User Profiles
* 🗃️ Long-Term Vector Memory Store
* 🔎 Citation-based web results

---

## 📄 License

MIT © [karthikzzzzzzz](https://github.com/karthikzzzzzzz)
