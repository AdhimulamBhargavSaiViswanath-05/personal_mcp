# Personal MCP v0

Static site for [personal_mcp](https://github.com/AdhimulamBhargavSaiViswanath-05/personal_mcp). **GitHub Pages does not run MCP** — it only shows status and links.

## Live endpoints

| Surface | URL | Role |
|---------|-----|------|
| **GitHub Pages (this site)** | `https://adhimulambhargavsaiviswanath-05.github.io/personal_mcp/` | Docs + deploy status |
| **Render (MCP HTTP)** | _Add your service URL after deploy_, e.g. `https://personal-mcp.onrender.com` | `streamable-http` MCP (`/mcp`) |
| **Health check** | `{RENDER_URL}/health` | JSON ok for Render probes |
| **Cursor (local)** | stdio via `.cursor/mcp.json` | Day-to-day dev |

After you deploy on Render, edit this file (or README) with the real Render URL.

## v0 tools

| Tool | Notes |
|------|--------|
| `personal_ping` | Health: version `v0`, transport, Python version |

More tools come in later feature branches.

## Render quick check

```bash
curl -sS "https://YOUR-SERVICE.onrender.com/health"
```

MCP clients must send `MCP_API_KEY` as `X-API-Key` (or `Authorization: Bearer`) on HTTP routes except `/health`.

## Owner

[AdhimulamBhargavSaiViswanath-05](https://github.com/AdhimulamBhargavSaiViswanath-05)
