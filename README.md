# personal_mcp

Personal MCP server — **phase 0:** learn Cursor + stdio with one tool (`personal_ping`). More use cases (notes, GitHub, career tracker, Render) come later in separate feature branches.

## Why not GitHub Pages for MCP?

Pages is static HTML. MCP needs a process (your laptop or Render). Use `docs/` only as a **documentation** site if you enable GitHub Pages.

## Phases (planned)

| Phase | What |
|-------|------|
| **0 (now)** | `personal_ping` + stdio + Cursor |
| **1+** | Notes, GitHub read, career metadata, Render HTTP — add when you choose |

## Git workflow

- `feature/*` → PR → **`dev`**
- Stable work → PR **`dev`** → **`main`**

## Setup

```bash
cd personal_mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Cursor

Edit `.cursor/mcp.json` (see `.cursor/mcp.json.example`): venv Python + absolute path to `server.py`. No secrets in that file. Reload MCP.

## Test

```bash
.venv/bin/python -c "import asyncio; from server import mcp; print(asyncio.run(mcp.call_tool('personal_ping', {})))"
```

In Cursor: ask the agent to call **`personal_ping`**.

`python server.py` with stdio will wait for input — Cursor starts the server for you.

## Security

Never commit `.env`.

## GitHub Pages (docs)

Settings → Pages → branch `main`, folder `/docs`.
