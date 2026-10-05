"""Personal MCP server: stdio-first tools for notes, career tracking, and GitHub read APIs."""

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from fastmcp import FastMCP

import career_db
import config
import github_client

logger = logging.getLogger(__name__)

mcp = FastMCP(name="personal")

_DATA = config.data_dir()
_NOTES_PATH = _DATA / "notes.md"
_CAREER_DB_PATH = _DATA / "career.db"
career_db.init_career_db(_CAREER_DB_PATH)


def _require_github_token() -> str:
    """Return GITHUB_TOKEN or raise a clear configuration error."""
    token = config.github_token()
    if not token:
        raise RuntimeError(
            "GITHUB_TOKEN is not set. Copy .env.example to .env and add a "
            "read-only fine-grained Personal Access Token."
        )
    return token


@mcp.tool()
def personal_ping() -> dict:
    """Return health info: transport, Python version, and whether GitHub token is configured."""
    return {
        "ok": True,
        "transport": config.mcp_transport(),
        "python_version": sys.version.split()[0],
        "github_token_set": config.github_token() is not None,
    }


@mcp.tool()
def personal_add_note(text: str) -> dict:
    """Append one timestamped line to data/notes.md."""
    line = f"- {datetime.now(timezone.utc).isoformat()} {text.strip()}\n"
    _NOTES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _NOTES_PATH.open("a", encoding="utf-8") as fh:
        fh.write(line)
    return {"ok": True, "path": str(_NOTES_PATH)}


@mcp.tool()
def personal_list_notes(limit: int = 20) -> dict:
    """Return the last N lines from data/notes.md."""
    limit = max(1, min(limit, 200))
    if not _NOTES_PATH.exists():
        return {"notes": [], "path": str(_NOTES_PATH)}
    lines = _NOTES_PATH.read_text(encoding="utf-8").splitlines()
    return {"notes": lines[-limit:], "path": str(_NOTES_PATH)}


@mcp.tool()
def personal_add_application(
    company: str,
    role: str,
    source: str,
    url: str = "",
    status: str = "applied",
    notes: str = "",
) -> dict:
    """Save one job application (you paste the job URL; no scraping or site login)."""
    record = career_db.add_application(
        _CAREER_DB_PATH,
        company=company,
        role=role,
        source=source,
        url=url,
        status=status,
        notes=notes,
    )
    return {"ok": True, "application": record}


@mcp.tool()
def personal_list_applications(
    source: str = "",
    status: str = "",
    limit: int = 50,
) -> dict:
    """List saved job applications with optional source/status filters."""
    rows = career_db.list_applications(
        _CAREER_DB_PATH, source=source, status=status, limit=limit
    )
    return {"applications": rows, "count": len(rows)}


@mcp.tool()
def personal_update_application_status(
    id: int,
    status: str,
    notes: str = "",
) -> dict:
    """Update workflow status for one application by database id."""
    record = career_db.update_application_status(
        _CAREER_DB_PATH, application_id=id, status=status, notes=notes
    )
    return {"ok": True, "application": record}


@mcp.tool()
def personal_github_whoami() -> dict:
    """Return GitHub login and profile URL for the configured token."""
    token = _require_github_token()
    return github_client.github_whoami(token)


@mcp.tool()
def personal_github_list_repos(limit: int = 20) -> dict:
    """List repositories visible to the authenticated GitHub user."""
    token = _require_github_token()
    repos = github_client.github_list_repos(token, limit=limit)
    return {"repos": repos, "count": len(repos)}


@mcp.tool()
def personal_github_list_issues(state: str = "open", limit: int = 20) -> dict:
    """List issues assigned to you (GitHub REST GET /issues?filter=assigned)."""
    token = _require_github_token()
    issues = github_client.github_list_issues(token, state=state, limit=limit)
    return {"issues": issues, "count": len(issues)}


@mcp.tool()
def personal_github_list_prs(state: str = "open", limit: int = 20) -> dict:
    """List PRs involving you (GitHub search: is:pr is:<state> involves:@me)."""
    token = _require_github_token()
    prs = github_client.github_list_prs(token, state=state, limit=limit)
    return {"pull_requests": prs, "count": len(prs)}


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
