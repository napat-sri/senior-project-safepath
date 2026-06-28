# SafePath — VPN & Network Architecture

_Last updated: 2026-06-28_

## Goal

Expose a single **public** entry point (the frontend) and keep everything else
**private** (backend, OSM tiles, Langflow, Postgres). A **WireGuard VPN** gives
admins direct access to the private services. The public app works for everyone
**without** a VPN; the VPN is only for administration.

## High-level design

```
                        Internet
                           |
            +--------------+--------------------+
            |                                   |
   HTTPS (Caddy)                        UDP 51820 (WireGuard)
   safepath.duckdns.org                 wg-easy gateway
            |                                   |
        FRONTEND  (public gateway)        VPN clients (admins)
            |  reverse-proxies:                 |
            |   /api/*      -> backend:9000     | reach private services
            |   /tile/*     -> openstreetmap:80 | over the tunnel:
            |   /langflow/* -> langflow:7860    |   backend     172.28.0.10:9000
            |                                   |   langflow    172.28.0.30:7860
   +--------+--------+--------+---------+       |   portainer   (when added)
   |        |        |        |         |       |
 backend   OSM    langflow  postgres  (mcp)  <--+
  (private, internal docker networks; no public domains/ports)
```

## Public vs. private

| Service        | Exposure | How it is reached |
|----------------|----------|-------------------|
| Frontend       | Public   | `https://safepath.duckdns.org` (Caddy, HTTPS) |
| Backend (API)  | Private  | Gateway `/api/*`; admin via VPN `172.28.0.10:9000` |
| OSM tiles      | Private  | Gateway `/tile/*` |
| Langflow       | Private  | Chat via gateway `/langflow/*`; admin UI via VPN `172.28.0.30:7860` |
| Postgres       | Private  | Internal only (`langflow-net`); no ports published |
| Portainer      | Private  | VPN only (to be added) |
| wg-easy (VPN)  | Public   | UDP `51820` (tunnel), TCP `51821` (admin UI) |

## Why a gateway instead of exposing each service

A public **HTTPS** page cannot call a private **HTTP** service directly — the
browser blocks it as *mixed content* (and Private Network Access). So the
public frontend (Caddy) reverse-proxies all browser-facing dependencies on its
own HTTPS origin. The browser only ever talks to one origin; Caddy forwards
inward over the internal docker network. This also removes the need for CORS on
those calls (they are same-origin).

## Internal vs. public URLs (important)

The same service is addressed differently depending on **who calls it**:

- **Browser (outside the network):** public URL, e.g.
  `https://safepath.duckdns.org/langflow`.
- **Container-to-container (inside the network):** internal service name, e.g.
  `http://langflow:7860`.

Example: the backend calls Langflow at `http://langflow:7860` (one hop on the
shared docker network) — not the public URL, which would hairpin out to the
internet, through Caddy (TLS + prefix strip), and back in.

## WireGuard (wg-easy)

- Image `ghcr.io/wg-easy/wg-easy:14`; only UDP `51820` and TCP `51821` public.
- Admin UI login uses a **bcrypt** `PASSWORD_HASH`. In docker-compose every `$`
  must be doubled to `$$`, e.g. `$2a$12$...` becomes `$$2a$$12$$...`.
- Private docker network `vpn` = `172.28.0.0/24`; clients get routes to both
  `10.8.0.0/24` and `172.28.0.0/24` so they can reach private services.
- Admin UI is `http://<host>:51821` — **not** the tunnel port `51820`
  (that one never serves a web page).

## Frontend gateway routing (Caddy labels)

```
caddy: safepath.duckdns.org
caddy.1_handle: /api/*
caddy.1_handle.reverse_proxy: backend:9000
caddy.2_handle: /tile/*
caddy.2_handle.reverse_proxy: openstreetmap:80
caddy.3_handle_path: /langflow/*          # strips the /langflow prefix
caddy.3_handle_path.reverse_proxy: langflow:7860
caddy.4_handle: /*
caddy.4_handle.reverse_proxy: {{upstreams 8080}}
```

## Docker networks

- `caddy` (external) — shared by frontend, backend, OSM, Langflow; lets the
  gateway reach services by name.
- `vpn` (`172.28.0.0/24`) — private; backend `.10`, Langflow `.30`, wg-easy.
- `langflow-net` — private link between Langflow and Postgres only.

## Relevant environment variables

```dotenv
# Frontend (browser) — same-origin via the gateway
VUE_APP_API_URL=/api
VUE_APP_TILE_URL=https://safepath.duckdns.org/tile/{z}/{x}/{y}.png
VUE_APP_LANGFLOW_HOST=https://safepath.duckdns.org/langflow

# Server-side (compose) — NOT exposed to the browser
LANGFLOW_SECRET_KEY=<long-random-string>   # keep stable across restarts
```

- Public app: `https://safepath.duckdns.org` (no VPN).
- Admin (VPN connected): backend `http://172.28.0.10:9000`,
  Langflow builder `http://172.28.0.30:7860`.

## Notes / follow-ups

- The Langflow **builder UI** is reached over the VPN (root domain), not the
  `/langflow` subpath, which only serves the chat API the widget needs.
- Reconcile Langflow flow-ID env vars with what the code reads
  (`VUE_APP_LANGFLOW_CHATBOT_FLOW_ID`, `VUE_APP_LANGFLOW_ROUTE_AGENT_FLOW_ID`).
- Add Portainer as a VPN-only service when ready.
- **Line endings:** files were truncated/converted to CRLF on save several
  times. Consider a `.gitattributes` forcing LF and a pre-commit sanity check,
  and glance at `git diff` before committing.

## Troubleshooting log (issues hit & fixes)

- **wg-easy "unauthorized":** recreate the container after changing
  `PASSWORD_HASH`; confirm the password matches the hash; verify the value
  reached the container (`docker compose exec wg-easy env | grep PASSWORD_HASH`).
- **`git pull` "insufficient permission for adding an object":** root-owned
  `.git/objects`; fix with `sudo chown -R $(whoami):$(whoami) .`.
- **Frontend constant refresh:** webpack HMR WebSocket couldn't negotiate over
  the VPN IP; fixed in `vue.config.js` (`client.webSocketURL`, or disable
  `hot`/`liveReload`).
- **Mixed content error:** HTTPS page calling an HTTP backend; solved by the
  same-origin gateway proxy.