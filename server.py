from mcp.server.fastmcp import FastMCP
from mcp.server import Server
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server.sse import SseServerTransport
import uvicorn
import requests
mcp = FastMCP("Researcher")

@mcp.tool()
def research_tool(query: str) -> dict:
    payload = {
        "query": query,
        "freshness": "noLimit",
        "summary": True,
        "count": 10
    }

    headers = {
        "Authorization": "Bearer sk-9df71fa395e24559a69fcdf11026ab5d",
        "Content-Type": "application/json"
    }

    response = requests.post("https://api.langsearch.com/v1/web-search", headers=headers, json=payload)
    
    return response.text


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as (read_stream, write_stream):
            await mcp_server.run(read_stream, write_stream, mcp_server.create_initialization_options())

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

if __name__ == "__main__":
    mcp_server = mcp._mcp_server
    app = create_starlette_app(mcp_server, debug=True)
    uvicorn.run(app, host="0.0.0.0", port=9090)
