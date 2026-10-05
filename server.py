"""Personal MCP server: stdio locally; streamable-http on Render (v0 = personal_ping)."""

import logging
import sys

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

import config
import http_security

logger = logging.getLogger(__name__)

mcp = FastMCP(name="personal")

V0_LABEL = "v0"


@mcp.custom_route("/health", methods=["GET"])
async def health_check(_request: Request) -> JSONResponse:
    """Return a simple JSON health payload for Render and manual checks."""
    return JSONResponse(
        {
            "ok": True,
            "service": "personal-mcp",
            "version": V0_LABEL,
            "transport": config.mcp_transport(),
        }
    )


@mcp.tool()
def personal_ping() -> dict:
    """Return ok, transport mode, Python version, and deploy label."""
    return {
        "ok": True,
        "version": V0_LABEL,
        "transport": config.mcp_transport(),
        "python_version": sys.version.split()[0],
    }


def main() -> None:
    """Start the MCP server using stdio (default) or streamable-http on Render."""
    transport = config.mcp_transport()
    if transport == "stdio":
        mcp.run(transport="stdio")
        return
    if transport == "streamable-http":
        if not config.mcp_api_key():
            logger.warning(
                "MCP_API_KEY is not set; HTTP is open except on platforms that inject a key."
            )
        logger.info(
            "Starting streamable-http on %s:%s (MCP path /mcp; GET /health for probes).",
            config.mcp_host(),
            config.mcp_port(),
        )
        mcp.run(
            transport="streamable-http",
            host=config.mcp_host(),
            port=config.mcp_port(),
            middleware=http_security.http_middleware_stack(),
        )
        return
    mcp.run(transport="stdio")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
