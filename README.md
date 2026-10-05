# personal_mcp

Personal MCP server — **v0:** `personal_ping` only. Learn stdio in Cursor, publish docs on **GitHub Pages**, run HTTP on **Render**.

## Two deploy surfaces (same repo, different jobs)

| Platform | Runs MCP? | v0 purpose |
|----------|-----------|------------|
| **GitHub Pages** (`/docs`) | No — static site | “What is v0?” + links |
| **Render** (`render.yaml`) | Yes — `streamable-http` | Test remote MCP + `/health` |
| **Your Mac + Cursor** | Yes — stdio | Daily development |

## Phases

| Phase | What |
|-------|------|
| **v0 (now)** | Deploy Pages + Render skeleton; one tool |
| **v1+** | Notes, GitHub, career tracker — separate feature branches |

## Local setup

```bash
cd personal_mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Cursor (stdio)

`.cursor/mcp.json`: venv Python + absolute `server.py`. No secrets. Reload MCP → call **`personal_ping`**.

## Test locally

```bash
.venv/bin/python -c "import asyncio; from server import mcp; print(asyncio.run(mcp.call_tool('personal_ping', {})).structured_content)"
```

### HTTP smoke test (optional)

```bash
export MCP_TRANSPORT=streamable-http MCP_API_KEY=dev-secret MCP_PORT=8008
python server.py &
curl -sS http://127.0.0.1:8008/health
curl -sS -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8008/mcp   # expect 401 without key
curl -sS -o /dev/null -w "%{http_code}\n" -H "X-API-Key: dev-secret" http://127.0.0.1:8008/mcp
kill %1
```

## GitHub Pages

1. Merge v0 to **`main`**.
2. Repo → **Settings → Pages** → Source: branch **`main`**, folder **`/docs`**.
3. Open `https://<user>.github.io/personal_mcp/` (see `docs/index.md`).

## Render

1. Merge v0 to **`main`** (Render blueprint uses `branch: main`).
2. [Render Dashboard](https://dashboard.render.com) → **New** → **Blueprint** → connect `personal_mcp` (or **Web Service** with same settings as `render.yaml`).
3. Env (blueprint sets these): `MCP_TRANSPORT=streamable-http`, `MCP_API_KEY` (generated), `PYTHON_VERSION=3.12.8`. Render injects **`PORT`** automatically.
4. After deploy: copy service URL into `docs/index.md`, enable Pages if not already.
5. `curl https://YOUR-SERVICE.onrender.com/health`

MCP endpoint path: **`/mcp`** (FastMCP default). Protect with `X-API-Key` from Render env.

## Git workflow

- `feature/*` → PR → **`dev`** → PR → **`main`** for releases / deploy

## Security

Never commit `.env`. Store `MCP_API_KEY` and future tokens only in Render env or local `.env`.
