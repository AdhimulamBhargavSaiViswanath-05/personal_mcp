# personal_mcp

Personal [Model Context Protocol](https://modelcontextprotocol.io) server you can grow over time: local notes, a simple job-application tracker, and read-only GitHub tools.

Personal project — learn MCP with Cursor first, deploy to Render later.

## Why not GitHub Pages for MCP?

GitHub Pages serves **static files** (HTML). An MCP server is a **long-running process** that speaks MCP over stdio or HTTP. Pages cannot host that.

You **can** use Pages for this repo’s **docs** (`docs/index.md` → enable Pages from `/docs` in repo settings) so you have a public “what is this?” page. The real server runs on your laptop or on Render.

## Phases

| Phase | What |
|-------|------|
| **1** | `MCP_TRANSPORT=stdio` + Cursor (this repo) |
| **2** | `GITHUB_TOKEN` in `.env` for `personal_github_*` tools |
| **3** | Same code on Render as `streamable-http` + `MCP_API_KEY` (not deployed yet) |

## Career tracker — what it is (and why)

This is **not** Naukri/LinkedIn automation. It is a **small SQLite notebook** on your machine:

- You see a job on Naukri or LinkedIn in the browser.
- You **copy the URL** and tell the MCP: company, role, `source` (`naukri` / `linkedin` / …), `status` (`applied`, `interview`, …).
- Later you can ask Cursor to list or update statuses.

Useful when you want the AI to help with follow-ups or summaries **without** giving it your passwords or scraping those sites.

## Git workflow

- `feature/*` → PR → **`dev`**
- When stable → PR **`dev`** → **`main`** (no direct commits on `main`)

## Setup

```bash
cd personal_mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# optional: add GITHUB_TOKEN to .env
```

## Cursor MCP config

Copy `.cursor/mcp.json.example` to `.cursor/mcp.json` (or use the generated file if paths match your machine). Replace:

- venv Python path
- absolute path to `server.py`

**Never put tokens in `mcp.json`.** Only env vars in `.env`.

Reload MCP in Cursor (restart or MCP refresh).

## Test without Cursor

```bash
python server.py
```

With stdio, the process waits for input — that is normal. **Cursor** starts the server when you use tools.

## Verify in Cursor

1. Ask the agent to call **`personal_ping`**.
2. **`personal_add_note`** then **`personal_list_notes`**.
3. **`personal_add_application`** with a fake Naukri URL (metadata only).
4. With PAT in `.env`: **`personal_github_whoami`**.

## GitHub PAT (read-only first)

1. GitHub → **Settings → Developer settings → Personal access tokens** (fine-grained recommended).
2. Repository access: your repos (or public only).
3. Permissions: **Contents** / metadata read, **Issues** read, **Pull requests** read as needed.
4. Put the token in `.env` as `GITHUB_TOKEN=` — never commit `.env`.

## Tools

| Name | Needs token? |
|------|----------------|
| `personal_ping` | No |
| `personal_add_note`, `personal_list_notes` | No |
| `personal_add_application`, `personal_list_applications`, `personal_update_application_status` | No |
| `personal_github_whoami`, `personal_github_list_repos` | Yes |
| `personal_github_list_issues` | Yes — uses `GET /issues?filter=assigned` |
| `personal_github_list_prs` | Yes — search `is:pr is:<state> involves:@me` |

## Render (future)

- Web service, start command runs `python server.py` with `MCP_TRANSPORT=streamable-http`.
- Set `GITHUB_TOKEN`, `MCP_API_KEY`, `MCP_HOST`, `MCP_PORT` in Render env.
- Add API-key middleware before exposing publicly (stub logs a warning today).

## Security

- Do not commit `.env`, PATs, or `MCP_API_KEY`.
- `data/*.db` and notes stay local (gitignored).

## GitHub Pages (docs only)

Repo → **Settings → Pages** → Build from branch `main`, folder **`/docs`**.
