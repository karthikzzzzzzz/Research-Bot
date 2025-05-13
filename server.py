from mcp.server.fastmcp import FastMCP
from mcp.server import Server
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server.sse import SseServerTransport
import uvicorn
import requests
import json


mcp = FastMCP("Researcher")

url = "https://api.langsearch.com/v1/web-search"

@mcp.tool()
def research_tool(query: str) -> dict:
    
    payload = json.dumps({
  "query": query,
  "freshness": "noLimit",
  "summary": True,
  "count": 10
})
    headers = {
  'Authorization': 'Bearer sk-9df71fa395e24559a69fcdf11026ab5d',
  'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    
    return response.text

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


if __name__ == "__main__":
    mcp_server = mcp._mcp_server
    
    starlette_app = create_starlette_app(mcp_server, debug=True)
    port = 9090
    print(f"Starting MCP server with SSE transport on port {port}...")
    print(f"SSE endpoint available at: http://localhost:{port}/sse")
    
    uvicorn.run(starlette_app, host="0.0.0.0", port=port)