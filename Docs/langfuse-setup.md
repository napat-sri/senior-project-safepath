# Langfuse Self-Hosted Setup (SafePath)

Self-hosted **Langfuse v3** for LLM observability, deployed on Contabo via
Portainer, served through Caddy, with login delegated to the existing
Keycloak (SSO). This document records the configuration and the operational
steps.

---

## 1. Architecture

| Component        | Role                                              |
| ---------------- | ------------------------------------------------- |
| `langfuse-web`   | Web UI + API (only service exposed externally)    |
| `langfuse-worker`| Background ingestion/processing                   |
| `postgres`       | Primary application database                      |
| `clickhouse`     | Analytics / trace storage                         |
| `minio`          | S3-compatible object storage (events, media)      |
| `redis`          | Queue / cache                                     |

- Deployed as a **Portainer stack** named `langfuse`.
- Files in repo: `langfuse/docker-compose.yml`, `langfuse/.env.example`.
- All datastores bind to `127.0.0.1` only. Just `langfuse-web` is reachable
  from outside, and only through Caddy.

---

## 2. Networking & Public Access

- **Public URL:** `https://langfuse.safepath.duckdns.org`
- **Reverse proxy:** existing `lucaslorentz/caddy-docker-proxy` (label-driven,
  no Caddyfile).
- `langfuse-web` is attached to the external `caddy` network and carries:

  ```yaml
  labels:
    caddy: langfuse.safepath.duckdns.org
    caddy.reverse_proxy: "{{upstreams 3000}}"
  ```

  Caddy auto-generates the site and Let's Encrypt certificate. No host port is
  published for the web UI.
- Set the external network name in the compose to the real Caddy network
  (`docker network ls`).

---

## 3. Secrets (set as Portainer stack environment variables)

Set in the stack's **Environment variables** section — never committed to the
compose file. Generate with:

- Passwords: alphanumeric, no special characters (avoids shell/`$` issues).
- `SALT`, `NEXTAUTH_SECRET`: `openssl rand -base64 32`
- `ENCRYPTION_KEY`: `openssl rand -hex 32` (must be exactly 64 hex chars)

| Variable              | Notes                                    |
| --------------------- | ---------------------------------------- |
| `NEXTAUTH_URL`        | `https://langfuse.safepath.duckdns.org`  |
| `POSTGRES_USER`       | `postgres`                               |
| `POSTGRES_DB`         | `postgres`                               |
| `POSTGRES_PASSWORD`   | strong password                          |
| `CLICKHOUSE_USER`     | `clickhouse`                             |
| `CLICKHOUSE_PASSWORD` | strong password                          |
| `REDIS_AUTH`          | strong password                          |
| `MINIO_ROOT_USER`     | `minio`                                  |
| `MINIO_ROOT_PASSWORD` | strong password                          |
| `SALT`                | base64, 32 bytes                         |
| `NEXTAUTH_SECRET`     | base64, 32 bytes                         |
| `ENCRYPTION_KEY`      | 64 hex chars — **back this up safely**   |

> Losing `ENCRYPTION_KEY` after data is written makes encrypted fields
> unrecoverable. Store it in a password manager.

---

## 4. Authentication — Keycloak SSO

Login is delegated to the existing Keycloak (`master` realm at
`login.safepath.duckdns.org`). This is separate from the Keycloak layer that
protects Portainer — same server, different client.

### Keycloak client

- **Clients → Create client**
  - Client ID: `langfuse`
  - Client authentication: **ON** (confidential)
  - Standard flow: enabled
- **Valid redirect URIs:**
  `https://langfuse.safepath.duckdns.org/api/auth/callback/keycloak`
- Copy the secret from the **Credentials** tab.
- Every Langfuse user must have an **email** set on their Keycloak profile
  (Langfuse identifies users by email).

### Langfuse env vars

```
AUTH_KEYCLOAK_CLIENT_ID=langfuse
AUTH_KEYCLOAK_CLIENT_SECRET=<from Keycloak Credentials tab>
AUTH_KEYCLOAK_ISSUER=https://login.safepath.duckdns.org/realms/master
AUTH_KEYCLOAK_ALLOW_ACCOUNT_LINKING=true
AUTH_DISABLE_USERNAME_PASSWORD=true
AUTH_DISABLE_SIGNUP=true
```

Verify the issuer resolves (must return JSON):
`https://login.safepath.duckdns.org/realms/master/.well-known/openid-configuration`

### First-login chicken-and-egg

`AUTH_DISABLE_SIGNUP=true` blocks creating the *first* user. To bootstrap:

1. Temporarily set `AUTH_DISABLE_SIGNUP=false` and redeploy.
2. Log in via the **Keycloak** button — this creates your Langfuse account.
3. Set `AUTH_DISABLE_SIGNUP=true` again and redeploy to re-lock signup.

Log in via the **Keycloak** button on the Langfuse login page (not the local
email/password form).

---

## 5. Deploy / Redeploy (Portainer)

1. **Stacks → Add stack**, name `langfuse`.
2. **Web editor:** paste `docker-compose.yml`; set the real Caddy network name.
3. **Environment variables → advanced mode:** paste all values from section 3
   and 4.
4. **Deploy the stack.**

> Deploy **only** through Portainer. Running `docker compose up` on the host
> directly causes Portainer to show "created outside of Portainer" and lock
> editing. If that happens: remove the stack + leftover containers, then
> recreate via Portainer.

First deploy pulls six images and runs migrations — `langfuse-web` may restart
a few times until Postgres and Redis report **healthy**. This is normal.

---

## 6. Troubleshooting (issues we hit)

| Symptom                                             | Cause / Fix                                                                 |
| --------------------------------------------------- | --------------------------------------------------------------------------- |
| Redis `FATAL CONFIG ... requirepass wrong args`     | `REDIS_AUTH` was empty. Set it to a real password.                          |
| `web`/`worker` stuck in `created`                   | Waiting on Postgres/Redis to become `healthy`. Fix the datastore first.     |
| `ERR_SSL_PROTOCOL_ERROR` in browser                 | No Caddy label/site for the host. Add labels + ensure it's on caddy network.|
| Keycloak `OAuthSignin` / `HTTP 404`                 | Wrong `AUTH_KEYCLOAK_ISSUER` (placeholder / wrong path). Fix to realm URL.  |
| Keycloak `Invalid parameter: redirect_uri`          | Add the callback URL to the client's Valid redirect URIs.                   |
| Langfuse `Sign up is disabled`                      | `AUTH_DISABLE_SIGNUP=true` blocks first user — bootstrap per section 4.     |
| "Invalid credentials" on Langfuse form              | Using the local email/password form — click the **Keycloak** button.       |

---

## 7. Langflow Integration (tracing) — WORKING

Langflow sends a trace to Langfuse for every flow run. Connection is via three
environment variables on the Langflow container plus a Langfuse project's API
keys. **No changes inside the flows themselves.**

### Langfuse side

1. In Langfuse: create an **Organization** → a **Project**.
2. **Project Settings → API Keys → Create new API key.** Copy the public key
   (`pk-lf-…`) and secret key (`sk-lf-…`).

### Langflow side (env vars, kept in shared `.env`)

```
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_BASE_URL=https://langfuse.safepath.duckdns.org
LANGFLOW_LOG_LEVEL=DEBUG
```

- `LANGFUSE_BASE_URL` uses the internal service name because Langflow and
  `langfuse-web` share the external `caddy` network (faster, no public
  round-trip). Fallback if it can't resolve:
  `https://langfuse.safepath.duckdns.org`.
- `LANGFUSE_BASE_URL` is the current preferred var (`LANGFUSE_HOST` is
  deprecated — don't set both).
- Loaded via `env_file: .env`; no need to also list them under `environment:`.

### Critical: Python 3.14 / langfuse version incompatibility

Langflow's tracer imports the **langfuse v3** API
(`from langfuse.langchain import CallbackHandler`, `langfuse._client`,
`langfuse.types`). Two traps:

- The `langflowai/langflow:latest` image runs **Python 3.14** (since Langflow
  release **1.9.3**). langfuse v3 **fails to import on Python 3.14** due to a
  Pydantic V1 incompatibility (`ConfigError: unable to infer type`).
- langfuse **v4** loads on 3.14 but has a different API, so Langflow can't use
  it (`Could not import langfuse` in the logs).

**Fix — pin Langflow to the last Python-3.13 release and install langfuse v3.**

`Dockerfile.langflow` (repo root):

```dockerfile
FROM langflowai/langflow:1.9.2
RUN uv pip install "langfuse>=3,<4"
```

`docker-compose-langflow.yml` — replace the `image:` line with a build:

```yaml
  langflow:
    build:
      context: .
      dockerfile: Dockerfile.langflow
    image: langflow-langfuse:pinned
    # all other config (env, volumes, networks, labels) unchanged
```

Build and deploy:

```bash
docker compose -f docker-compose-langflow.yml up -d --build langflow
```

> **DB caveat when pinning down:** the Langflow Postgres schema may have been
> migrated by a newer version. If startup shows a migration/schema error,
> export the flow (UI → Export → JSON), reset the `langflow-postgres` volume,
> rebuild, and re-import the flow.

### Verify

```bash
# tracer imports succeed on Python 3.13 (no Pydantic crash)
docker compose -f docker-compose-langflow.yml exec langflow \
  python -c "from langfuse.langchain import CallbackHandler; from langfuse._client.span import LangfuseSpan; print('OK')"

# startup log clean of "Could not import langfuse"
docker compose -f docker-compose-langflow.yml logs --since 3m langflow | grep -i langfuse
```

Then run a flow → **Langfuse → project → Tracing** shows the trace.

### Langflow troubleshooting (issues we hit)

| Symptom                                              | Cause / Fix                                                              |
| ---------------------------------------------------- | ------------------------------------------------------------------------ |
| Only `NativeCallbackHandler` in logs, no trace       | langfuse SDK not attached — tracer failed to init.                       |
| `Could not import langfuse` at startup               | langfuse SDK missing or wrong major version for Python 3.14.             |
| `ModuleNotFoundError: langfuse.callback`             | v4 installed; Langflow needs v3 API.                                     |
| `pydantic.v1.errors.ConfigError` importing langfuse  | Python 3.14 incompatibility — pin Langflow to 1.9.2 (Python 3.13).       |
| `WARN ... "XPxv1" variable is not set`               | A secret in `.env` contains a literal `$` — escape it as `$$`.          |
| `no such service: langflow`                          | Wrong compose file — pass `-f docker-compose-langflow.yml`.             |

---

## 8. Backend Monitoring API (read traces from Python)

The SafePath FastAPI backend (`backend/`, Python 3.12) reads traces from
Langfuse using the langfuse **v3 Python SDK** and exposes read-only monitoring
endpoints. This is the "get the logs / monitor user activity" layer.

### Files

- `backend/langfuse_monitor.py` — Langfuse client + query/alert/stat logic.
- `backend/main.py` — four endpoints wired in (below).
- `backend/requirements.txt` — added `langfuse>=3,<4` and `python-dotenv`.

### Backend environment variables (`.env`)

```
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://langfuse.safepath.duckdns.org   # public fallback
```

> **Important:** the SDK reads `LANGFUSE_HOST` — **not** `LANGFUSE_BASE_URL`.
> `LANGFUSE_BASE_URL` is Langflow's variable (section 7). Different services,
> different variable names for the same Langfuse instance.

### Endpoints

| Endpoint                                | Purpose                                             |
| --------------------------------------- | --------------------------------------------------- |
| `GET /api/monitor/health`               | Verify credentials + connectivity.                  |
| `GET /api/monitor/traces`               | Recent traces, newest first (`minutes`, `limit`).   |
| `GET /api/monitor/traces?include_io=true` | Adds truncated `input_preview` / `output_preview`.|
| `GET /api/monitor/traces/{trace_id}`    | Full input/output + all observations (per step).    |
| `GET /api/monitor/alerts`               | High-latency + ERROR/WARNING alerts.                |
| `GET /api/monitor/stats`                | Volume / avg-max latency / cost / per-user counts.  |

Test:

```bash
docker compose up -d --build backend
curl https://backend.safepath.duckdns.org/api/monitor/health
curl -s "https://backend.safepath.duckdns.org/api/monitor/traces?minutes=1440&include_io=true" | python3 -m json.tool
curl -s "https://backend.safepath.duckdns.org/api/monitor/traces/<TRACE_ID>" | python3 -m json.tool
```

Swagger UI: `https://backend.safepath.duckdns.org/docs`.

### Issues fixed while building the backend monitor

| Issue                                                    | Cause / Fix                                                                                              |
| -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Which SDK read methods to use                            | v3 SDK: `client.api.trace.list(...)`, `client.api.trace.get(id)`, `client.api.observations.get_many(...)`. |
| Traces returned but no input/output                      | The list summary omits I/O by design. Use `include_io=true` for previews, or the `/{trace_id}` detail endpoint for full I/O + observations. |
| Full prompt/response not on the trace top level          | The richest input/output lives at the **observation** level — exposed in the detail endpoint's `observations[]`. |
| `LANGFUSE_HOST` vs `LANGFUSE_BASE_URL` confusion          | Backend SDK uses `LANGFUSE_HOST`; Langflow uses `LANGFUSE_BASE_URL`. Same instance, different var names.  |
| `python-dotenv` imported but not pinned                  | Added `python-dotenv` to `requirements.txt`.                                                              |
| Per-user stats show `anonymous`                          | Langflow calls don't pass `user_id`/`session_id` yet — attribution needs to be added to the run payload. |

---

## 9. Status & Next Steps

**Done:** Langfuse stack deployed, served via Caddy with TLS, Keycloak SSO
working end-to-end, first account created, **Langflow tracing working** (pinned
to Langflow 1.9.2 + langfuse v3), **backend monitoring API reading traces**
(`/api/monitor/*`).

**Outstanding:**
- Re-lock signup: `AUTH_DISABLE_SIGNUP=true` + redeploy.
- Confirm `AUTH_DISABLE_USERNAME_PASSWORD=true` took effect (hide local form).
- Ensure `.env` is gitignored (no secrets committed).
- Revisit the Langflow pin when upstream supports langfuse on Python 3.14
  (then `latest` can be used again).
- Pass `user_id` / `session_id` into the Langflow call in `/api/routes/safe`
  so traces are attributed to users (fixes `anonymous` in monitor stats).
- Optional: scheduled alert check (poll `/api/monitor/alerts` periodically).
