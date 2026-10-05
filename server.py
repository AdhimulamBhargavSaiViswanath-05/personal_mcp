"""Personal MCP server: stdio-first; phase 0 is health check only."""

import logging
import sys

from fastmcp import FastMCP

import config

logger = logging.getLogger(__name__)

mcp = FastMCP(name="personal")


@mcp.tool()
def personal_ping() -> dict:
    """Return ok, transport mode, and Python version."""
    return {
        "ok": True,
        "transport": config.mcp_transport(),
        "python_version": sys.version.split()[0],
    }


def main() -> None:
    """Start the MCP server using stdio (default) or a minimal HTTP stub."""
    transport = config.mcp_transport()
    if transport == "stdio":
        mcp.run(transport="stdio")
        return
    if transport == "streamable-http":
        if not config.mcp_api_key():
            logger.warning(
                "MCP_API_KEY is not set; add API key middleware before production HTTP deploy."
            )
        logger.info(
            "Starting streamable-http on %s:%s (Render-ready path; protect with MCP_API_KEY later).",
            config.mcp_host(),
            config.mcp_port(),
        )
        mcp.run(
            transport="streamable-http",
            host=config.mcp_host(),
            port=config.mcp_port(),
        )
        return
    mcp.run(transport="stdio")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
