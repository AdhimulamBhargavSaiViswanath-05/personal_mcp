"""Load settings from environment and .env in the project root."""

from pathlib import Path

from dotenv import load_dotenv
import os

_PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(_PROJECT_ROOT / ".env")


def _str(name: str, default: str) -> str:
    """Return an environment variable as a string with a default."""
    return os.getenv(name, default).strip()


def project_root() -> Path:
    """Return the repository root directory."""
    return _PROJECT_ROOT


def data_dir() -> Path:
    """Return the data directory, creating it if needed."""
    path = Path(_str("DATA_DIR", "./data"))
    if not path.is_absolute():
        path = _PROJECT_ROOT / path
    path.mkdir(parents=True, exist_ok=True)
    return path


def mcp_transport() -> str:
    """Return MCP transport mode: stdio or streamable-http."""
    value = _str("MCP_TRANSPORT", "stdio").lower()
    if value not in ("stdio", "streamable-http"):
        return "stdio"
    return value


def mcp_host() -> str:
    """Return bind host for HTTP transport."""
    return _str("MCP_HOST", "0.0.0.0")


def mcp_port() -> int:
    """Return bind port for HTTP transport (Render sets PORT)."""
    port = os.getenv("PORT", "").strip() or _str("MCP_PORT", "8008")
    return int(port)


def mcp_api_key() -> str | None:
    """Return API key for future HTTP auth, if configured."""
    key = _str("MCP_API_KEY", "")
    return key or None
