import json
import random
from fastmcp import FastMCP

mcp = FastMCP("simple calculator server")


@mcp.tool()
def add(a: float, b: float) -> float:
    """add two numbers together"""
    return a + b


@mcp.tool()
def random_number(min_val: int = 1, max_val: int = 100) -> int:
    """generate a random value between given range"""
    return random.randint(min_val, max_val)


@mcp.resource("info://server")
def server_into() -> str:
    """get server information"""
    info = {
        "name": "simple calculator server",
        "version": "2.0.0.1",
        "description": "A basic mcp server with math tools",
        "author": "greatest mahesh kumar jangid",
    }
    return json.dumps(info, indent=2)


if __name__ == "__main__":
    # HTTP/SSE transport ke liye:
    mcp.run(transport="sse", host="0.0.0.0", port=8000)