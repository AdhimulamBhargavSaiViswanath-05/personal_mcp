"""Read-only GitHub REST API helpers using httpx."""

import httpx

GITHUB_API = "https://api.github.com"


def _headers(token: str) -> dict[str, str]:
    """Build authorization headers without logging the token."""
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _check_response(response: httpx.Response) -> None:
    """Raise readable errors for auth, permission, and rate-limit failures."""
    if response.status_code == 401:
        raise RuntimeError(
            "GitHub returned 401: invalid or expired GITHUB_TOKEN. "
            "Set a fine-grained PAT in .env with read access to your repos."
        )
    if response.status_code == 403:
        msg = response.json().get("message", response.text)
        if "rate limit" in msg.lower():
            raise RuntimeError(f"GitHub rate limit: {msg}")
        raise RuntimeError(f"GitHub forbidden (403): {msg}")
    if response.status_code >= 400:
        raise RuntimeError(f"GitHub API error {response.status_code}: {response.text[:500]}")


def github_whoami(token: str) -> dict:
    """Return the authenticated user's login and profile URL."""
    with httpx.Client(timeout=30.0) as client:
        response = client.get(f"{GITHUB_API}/user", headers=_headers(token))
        _check_response(response)
        data = response.json()
    return {"login": data.get("login"), "html_url": data.get("html_url")}


def github_list_repos(token: str, limit: int = 20) -> list[dict]:
    """List repositories for the authenticated user."""
    limit = max(1, min(limit, 100))
    with httpx.Client(timeout=30.0) as client:
        response = client.get(
            f"{GITHUB_API}/user/repos",
            headers=_headers(token),
            params={
                "sort": "updated",
                "per_page": limit,
                "affiliation": "owner,collaborator,organization_member",
            },
        )
        _check_response(response)
        data = response.json()
    return [
        {
            "name": r.get("name"),
            "private": r.get("private"),
            "html_url": r.get("html_url"),
            "updated_at": r.get("updated_at"),
        }
        for r in data
    ]


def github_list_issues(token: str, state: str = "open", limit: int = 20) -> list[dict]:
    """List issues assigned to the authenticated user (GET /issues, filter=assigned)."""
    limit = max(1, min(limit, 100))
    state = state if state in ("open", "closed", "all") else "open"
    with httpx.Client(timeout=30.0) as client:
        response = client.get(
            f"{GITHUB_API}/issues",
            headers=_headers(token),
            params={"filter": "assigned", "state": state, "per_page": limit},
        )
        _check_response(response)
        data = response.json()
    results = []
    for item in data:
        if "pull_request" in item:
            continue
        results.append(
            {
                "number": item.get("number"),
                "title": item.get("title"),
                "state": item.get("state"),
                "html_url": item.get("html_url"),
                "repository": item.get("repository", {}).get("full_name"),
            }
        )
    return results[:limit]


def github_list_prs(token: str, state: str = "open", limit: int = 20) -> list[dict]:
    """Search for pull requests that involve the authenticated user."""
    limit = max(1, min(limit, 100))
    state = state if state in ("open", "closed", "all") else "open"
    query = f"is:pr is:{state} involves:@me"
    with httpx.Client(timeout=30.0) as client:
        response = client.get(
            f"{GITHUB_API}/search/issues",
            headers=_headers(token),
            params={"q": query, "per_page": limit, "sort": "updated"},
        )
        _check_response(response)
        data = response.json()
    items = data.get("items", [])
    return [
        {
            "number": item.get("number"),
            "title": item.get("title"),
            "state": item.get("state"),
            "html_url": item.get("html_url"),
            "repository": item.get("repository_url", "").replace(
                "https://api.github.com/repos/", ""
            ),
        }
        for item in items[:limit]
    ]
