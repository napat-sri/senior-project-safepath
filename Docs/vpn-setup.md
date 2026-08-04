# SafePath — VPN & Network Architecture

_Last updated: 2026-08-04_

## Goal

One **public** entry point (the frontend app); every other service is
**private** and reachable only over a **WireGuard VPN**. Private services can be
reached over the VPN either by IP or by a friendly, VPN-guarded **subdomain**.

## Public vs. private

| Service     | Public URL (everyone)        | Private / VPN-only name (admins)         | Upstream        |
|-------------|------------------------------|------------------------------------------|-----------------|
| Frontend    | `https://safepath.duckdns.org` | —                                      | `frontend:8080` |
| Backend API | via gateway `/api/*`         | `https://backend.safepath.duckdns.org`   | `backend:9000`  |
| OSM tiles   | via gateway `/tile/*`        | `https://osm.safepath.duckdns.org`       | `openstreetmap:80` |
| Langflow    | chat via gateway `/langflow/*` | `https://langflow.safepath.duckdns.org` (builder UI) | `langflow:7860` |
| Portainer   | —                            | `https://portainer.safepath.duckdns.org` | `portainer:9000` |
| Postgres    | —                            | VPN by IP only (raw TCP, not HTTP)       | `postgres:5432` |
| wg-easy     | UDP `51820` (tunnel)         | admin UI `http://safepath.duckdns.org:51821`           | —               |
| Langfuse    | `https://langfuse.safepath.duckdns.org` (public, external) | — | *not part of this compose stack — see below* |

## Request flow

```
 Public user ── HTTPS ─▶ safepath.duckdns.org (Caddy) ──▶ handle:
                                                   /api/*      -> backend:9000
                                                   /tile/*     -> openstreetmap:80
                                                   /langflow/* -> langflow:7860
                                                   /*          -> frontend:8080

 Admin ── WireGuard ─▶ wg-easy (172.28.0.3) ─▶ Caddy (172.28.0.10) ─▶
                    <name>.safepath.duckdns.org, allowed only if source == 172.28.0.3
                    (public visitors to those names get 403)
```

## How "private but named" works

Each private service carries Caddy labels for its own subdomain plus a guard
that admits **only** WireGuard traffic (which is masqueraded through wg-easy, so
Caddy sees source `172.28.0.3`):

```yaml
labels:
  caddy: <name>.safepath.duckdns.org
  caddy.@vpn.remote_ip: "172.28.0.3"
  caddy.route.0_reverse_proxy: "@vpn {{upstreams <PORT>}}"
  caddy.route.1_respond: '"VPN access required. your ip is {http.request.remote.host}" 403'
```

- **DNS:** DuckDNS wildcards, so every `*.safepath.duckdns.org` resolves — to the
  public IP for the internet, and (via dnsmasq) to Caddy `172.28.0.10` for VPN
  clients.
- **TLS:** Caddy auto-issues a Let's Encrypt cert per subdomain; the ACME
  challenge is handled before the 403 route, so certs still issue. Cert validity
  is by hostname (SNI), so it's valid even when reached at an internal IP.
- **Routing:** Caddy reaches the upstream over the shared `caddy` network,
  independent of the VPN network.

## Split-horizon DNS (dnsmasq)

wg-easy pushes `WG_DEFAULT_DNS=172.28.0.53` (dnsmasq) to clients. dnsmasq
forwards normal queries upstream but overrides the app domain:

```
--address=/safepath.duckdns.org/172.28.0.10   # -> Caddy, for VPN clients
```

**Caution:** this override hijacks the hostname for *all* protocols, not just
web, and for **every** subdomain of `safepath.duckdns.org` — including ones
that aren't actually routed by this project's Caddy at all (see **Langfuse**
below). While connected to the VPN, `ssh safepath.duckdns.org` also resolves
to `172.28.0.10` — so **SSH by the server's public IP** (or disconnect the VPN
first). Don't lock yourself out.

## Langfuse (external — not part of this compose stack)

Langfuse (prompt management for `safepath-route-safety`, plus tracing/
observability — see `backend/langfuse_prompts.py` and `langfuse_monitor.py`)
is **not** one of the services this repo's `docker-compose*.yml` files
deploy. It's hosted separately, and just happens to sit under the same
`*.safepath.duckdns.org` wildcard for convenience. Its real public IP
(verified via a public DNS-over-HTTPS resolver, bypassing any local
overrides) is `84.247.178.45` — a normal internet-reachable host, nothing
VPN-gated about it by design.

Auth: `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` in `.env`. The effective
host comes from `LANGFUSE_BASE_URL` (`https://langfuse.safepath.duckdns.org`)
— the Langfuse SDK checks that env var before the `LANGFUSE_HOST` fallback
`backend/langfuse_monitor.py` passes in code, so `LANGFUSE_HOST`'s default
(`http://langfuse-web:3000`) is effectively dead code; harmless, just don't
rely on it.



## Internal vs. public URLs (rule of thumb)

- **Browser (outside):** public URL, e.g. `https://safepath.duckdns.org/langflow`.
- **Container-to-container (inside):** service name, e.g. `http://langflow:7860`.
  The backend calls Langflow this way — one hop, no hairpin out through Caddy.

## WireGuard (wg-easy)

- Image `ghcr.io/wg-easy/wg-easy:14`; only UDP `51820` + TCP `51821` public.
- Admin UI login uses a **bcrypt** `PASSWORD_HASH`; in compose every `$` must be
  doubled to `$$`. Admin UI is on port **51821**, not the tunnel port 51820.
- Recreate the container after changing `PASSWORD_HASH`
  (`docker compose up -d --force-recreate wg-easy`).

## Networks

- `caddy` (external) — Caddy ingress; shared by all HTTP services so Caddy can
  route by name.
- `app_vpn` / `vpn` (`172.28.0.0/24`) — the private VPN network: wg-easy
  `172.28.0.3`, Caddy `172.28.0.10`, dnsmasq `172.28.0.53`, plus the services.
  Keep this a **single** network across all compose files (don't run two
  different networks that merely share the subnet).
- `langflow-net` — private link between Langflow and Postgres only.

## Deploy / apply

```bash
# server "infra" stack (caddy, webhook, portainer, dnsmasq)
docker compose up -d

# project stack
docker compose up -d --build backend frontend
docker compose up -d openstreetmap wg-easy
docker compose -f docker-compose-langflow.yml up -d postgres langflow
```

Certs auto-issue on first request to each new subdomain (first hit is slower).

## Troubleshooting log (issues hit & fixes)

- **wg-easy "unauthorized":** recreate after changing `PASSWORD_HASH`; confirm
  the plaintext matches the hash; verify with
  `docker compose exec wg-easy env | grep PASSWORD_HASH`.
- **`git pull` "insufficient permission ... .git/objects":** root-owned objects;
  `sudo chown -R $(whoami):$(whoami) .`.
- **Frontend constant refresh:** webpack HMR WebSocket over the VPN IP; fixed in
  `vue.config.js` (`client.webSocketURL`, or disable `hot`/`liveReload`).
- **Mixed content:** HTTPS page calling an HTTP backend; solved by the
  same-origin gateway proxy.
- **Backend down:** `main.py` truncated mid-`return` on save; restored the final
  `return { "route_suggestions": route_suggestions }`.
- **HTTPS error on the app over VPN:** dnsmasq pointed the domain at an IP with
  no HTTPS server; fixed by putting Caddy on the VPN network at `172.28.0.10`
  (the dnsmasq target) so the domain resolves to the cert-terminating server.
- **SSH "Connection refused" over VPN:** the dnsmasq override sent the hostname
  to an internal IP; SSH by public IP or disconnect the VPN.

## Follow-ups

- Reconcile Langflow flow-ID env vars with what the code reads
  (`VUE_APP_LANGFLOW_CHATBOT_FLOW_ID`, `VUE_APP_LANGFLOW_ROUTE_AGENT_FLOW_ID`).
- Consider a `.gitattributes` forcing LF + a pre-commit check — files were
  truncated/CRLF-converted on save several times during this work.
- Optional: firewall the wg-easy admin UI (51821) to admin IPs.
