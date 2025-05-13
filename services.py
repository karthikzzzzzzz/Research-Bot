from langgraph.checkpoint.redis import AsyncRedisSaver
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from schema import State
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from mcp.client.sse import sse_client
from mcp import ClientSession
from langgraph.pregel import RetryPolicy
from langfuse.callback import CallbackHandler
from langchain_mcp_adapters.tools import load_mcp_tools
import os
import redis
from dotenv import load_dotenv
import uuid


load_dotenv()

RetryPolicy()

# Initialize Langfuse callback handler for tracing and lineage tracking
langfuse_handler = CallbackHandler(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    host=os.getenv("LANGFUSE_HOST"),
    session_id=str(uuid.uuid4()), # Generate a new session id
    metadata={
        "agent_id": "research_agent"
    }
)

# Predefined run id for tracing
predefined_run_id = str(uuid.uuid4())

# Redis client for short-term memory storage
print(os.getenv("REDIS_URI"))
redis_client = redis.Redis.from_url("redis://localhost:6379", decode_responses=True)

# Define the main DataAcquisition agent class
class Research:
    def __init__(self):
        # Initialize OpenAI LLM
        self.llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("MODEL"),
            base_url=os.getenv("OPENAI_BASE_URL")
        )
        self.timeout = 3600 # 1 hour timeout

    # Core processing function: Build the agent, load tools, process user query
    async def process(self, session: ClientSession, request: str, user_id: int, realm_id: str, lead_id: int):
        async with MultiServerMCPClient({
            "server": {
                "url": "http://127.0.0.1:9090/sse",
                "transport": "sse",
            }
        }) as client:
            
            # Use Redis-based checkpointing
            async with AsyncRedisSaver.from_conn_string(os.getenv("REDIS_URI")) as checkpointer:
                await checkpointer.checkpoints_index.create(overwrite=False)
                await checkpointer.checkpoint_blobs_index.create(overwrite=False)
                await checkpointer.checkpoint_writes_index.create(overwrite=False)

                # Load available tools dynamically from MCP
                tools = await load_mcp_tools(session)
                graph_builder = StateGraph(State)

                # Create ReAct-style agent
                agent = create_react_agent(self.llm, tools=tools, checkpointer=checkpointer)

                graph_builder.add_node("research-agent", agent, retry=RetryPolicy(max_attempts=5))
                graph_builder.add_edge(START, "research-agent")

                # Add tool node
                tool_node = ToolNode(tools=client.get_tools())
                graph_builder.add_node("tools", tool_node.ainvoke)

                graph_builder.add_conditional_edges("research-agent", tools_condition)
                graph_builder.add_edge("tools", "research-agent")
                graph_builder.add_edge("research-agent", END)

                graph = graph_builder.compile(checkpointer=checkpointer)
                graph.name = "research-agent"

                try:
                
                    # Invoke the graph with the user request
                    response = await graph.ainvoke(
                        {"messages": [{"role": "user", "content": request}]},
                        config={
                            "configurable": {"thread_id": "1"},
                            "callbacks": [langfuse_handler],
                            "run_id": predefined_run_id
                        }
                    )

                    return {
                        "agent_response": response["messages"][-1].content,
                        "trace_id": predefined_run_id,
                        "session_id": langfuse_handler.session_id,
                        "span_id": langfuse_handler.metadata.get("agent_id")
                    }
                except Exception as e:
                    print(e)

    # Entry point for running queries
    async def run_query(self, query: str, user_id: int, realm_id: str, lead_id: int) -> dict:
        server_url = os.getenv("SSE_SERVER_URL")
        async with sse_client(url=server_url) as streams:
            async with ClientSession(*streams) as session:
                try:
                    await session.initialize()
                    return await self.process(session, query,user_id, realm_id, lead_id)
                except Exception as e:
                    print("Error during process_query:", str(e))

chat = Research()