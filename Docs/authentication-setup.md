# Authentication Setup — Keycloak (SafePath)

A step-by-step guideline for wiring **Keycloak** as the authentication provider for the SafePath app (Vue 3 SPA + FastAPI), covering **both `dev` (localhost) and `prod`**. It is written to be reusable: the concepts and steps apply to any SPA + API that wants to delegate login to Keycloak.

---

## 1. Overview

Login is delegated entirely to Keycloak using the **OpenID Connect Authorization Code flow with PKCE**:

- The SPA never handles raw passwords. It redirects the browser to Keycloak's hosted login/registration pages (`keycloak-js`). Keycloak authenticates the user (email/password **or** Google) and redirects back with a one-time `code`, which `keycloak-js` exchanges for tokens held **in memory**.
- Every API call carries the access token as `Authorization: Bearer <token>`.
- The FastAPI backend **validates the token locally** using Keycloak's public keys (JWKS) — no per-request call to Keycloak.
- **Roles** (`member`, `admin`) travel inside the token (`realm_access.roles`) and drive access control on both the frontend and backend. A **guest** is simply an unauthenticated visitor (no token, no role).

```
Browser (Vue SPA)
  │  click Login / Register / Google
  ▼
keycloak-js ── Authorization Code + PKCE ──▶ Keycloak (realm: safepath)
  ▲                                            │  email+password  OR  Google IdP broker
  │  redirect back with code → tokens in memory ├─▶ Google OAuth
  │                                            └─▶ Keycloak database (users)
  ▼
SPA attaches  Authorization: Bearer <access_token>
  ▼
FastAPI ── validates JWT via JWKS ──▶ Keycloak /certs (public keys)
```

---

## 2. Concepts (glossary)

| Term | Meaning |
|---|---|
| **Realm** | An isolated tenant in Keycloak (its own users, clients, roles). We use `safepath`. |
| **Client** | An application registered in a realm. **Public** = SPA, no secret (uses PKCE). **Confidential** = server app, has a secret. |
| **PKCE** | Proof Key for Code Exchange — protects the Authorization Code flow for public clients. Method `S256`. |
| **Access token (JWT)** | Signed token (`header.payload.signature`) with claims: `sub`, `email`, `exp`, `iss`, `aud`, `realm_access.roles`. |
| **JWKS** | Keycloak's public keys, published at `/realms/<realm>/protocol/openid-connect/certs`. Used to verify token signatures. |
| **Identity provider (IdP) / brokering** | Keycloak delegating login to an external provider (Google). First login auto-creates/links the user. |
| **Realm role** | A label attached to users (`member`, `admin`), surfaced in `realm_access.roles`. |
| **Service account** | A confidential client that can call Keycloak's Admin REST API using the client-credentials grant. |

**Key principle:** *dev and prod Keycloak are separate servers with separate databases.* Configuring one never affects the other. Configure `dev` first, then **export the realm and import it into `prod`** (Section 6).

---

## 3. Environments at a glance

| | **dev** | **prod** |
|---|---|---|
| Keycloak URL | `http://localhost:8090` (local container) | `https://login.safepath.duckdns.org` (existing instance) |
| App URL | `http://localhost:8080` | `https://safepath.duckdns.org` |
| Keycloak DB | ephemeral H2 (in-container) | Postgres (`keycloak-postgresql-1`) |
| TLS | none (http) | yes (Caddy) |
| Realm | `safepath` | `safepath` (imported copy) |
| Frontend client | `safepath-frontend` (redirect `http://localhost:8080/*`) | `safepath-frontend` (redirect `https://safepath.duckdns.org/*`) |
| Backend → Keycloak | internal `http://keycloak:8080`, browser `http://localhost:8090` (URLs **split**, see §7.2) | same host for both |
| Google IdP | optional locally | required |

---

## 4. Keycloak realm configuration

Do this in the **`safepath`** realm (top-left realm selector — never `master`). In dev you configure by hand; in prod you import the dev realm (§6) and only fix prod-specific values.

### 4.1 Create the realm
Create realm → name **`safepath`** (must match the app config).

### 4.2 Login / registration settings — *Realm settings → Login*
- **User registration: ON**
- **Login with email: ON**
- **Duplicate emails: OFF** (blocks registering the same email twice)
- **Forgot password: ON** (recommended)
- **Verify email:** ON only if SMTP is configured (optional for dev)

### 4.3 Frontend client — *Clients → Create client* → `safepath-frontend`
- Type **OpenID Connect**; **Client authentication: OFF** (public SPA).
- **Standard flow: ON** (Direct access grants OFF, Implicit OFF).
- **Valid redirect URIs:** dev `http://localhost:8080/*` · prod `https://safepath.duckdns.org/*`
- **Valid post-logout redirect URIs:** same as above.
- **Web origins:** `+`
- **Advanced → PKCE Code Challenge Method: `S256`**

### 4.4 Roles — *Realm roles*
1. **Create role** `member`, then **Create role** `admin`.
2. Make `admin` composite: open `admin` → **Associated roles → Assign role** → tick `member`.
3. Grant `member` to everyone automatically: **Realm settings → User registration → Default roles → Assign role** → tick `member`.
   - ⚠️ Default roles apply only to users created **after** this step.
4. Promote an admin: **Users → (user) → Role mapping → Assign role** → tick `admin`.

*(Guest needs nothing — it is the unauthenticated state.)*

### 4.5 Google identity provider
**a) Google Cloud Console** — *APIs & Services*:
1. **OAuth consent screen** → External; scopes `openid`, `email`, `profile`. In dev, add your Google account under **Test users**. In prod, **Publish** the app.
2. **Credentials → Create OAuth client ID → Web application**. Add **Authorized redirect URI** = the Keycloak broker endpoint:
   - dev: `http://localhost:8090/realms/safepath/broker/google/endpoint`
   - prod: `https://login.safepath.duckdns.org/realms/safepath/broker/google/endpoint`
3. Copy the **Client ID** and **Client secret**.

**b) Keycloak** — *Identity providers → Add provider → Google*:
- Paste Client ID / Secret · **Trust Email: ON** · scopes `openid profile email` · keep alias **`google`** (must match `idpHint: 'google'`) · leave **First login flow = first broker login** (auto-creates/links by email).

### 4.6 Backend audience (so the API can check the token is for it) — *Client scopes*
- Create client scope `safepath-api` → add mapper type **Audience** (Included Custom Audience = `safepath-api`).
- Add `safepath-api` as a **Default** client scope on `safepath-frontend`. Access tokens then carry `aud: "safepath-api"`.

### 4.7 (Optional) Service-account client for in-app user management — *Clients → Create* → `safepath-backend`
- **Client authentication: ON** (confidential); **Service accounts roles: ON**; Standard/Direct flows OFF.
- **Credentials** tab → copy the **Client secret**.
- **Service account roles** → assign from the `realm-management` client: `manage-users`, `view-users`, `query-users`, `view-realm`.

---

## 5. Development setup (localhost)

### 5.1 Run a local Keycloak (dev-only, in the dev `docker-compose.yml`)
```yaml
  keycloak:
    image: quay.io/keycloak/keycloak:26.1
    command: start-dev --import-realm        # built-in H2, HTTP, relaxed hostname
    environment:
      KC_BOOTSTRAP_ADMIN_USERNAME: admin
      KC_BOOTSTRAP_ADMIN_PASSWORD: admin
    ports:
      - "8090:8080"                          # 8081 is taken by the tile server; use 8090
    volumes:
      - ./keycloak/import:/opt/keycloak/data/import:ro   # optional realm auto-import
```
Start it: `docker compose up -d keycloak` → admin console at `http://localhost:8090/admin` (`admin` / `admin`). This is a throwaway sandbox and never touches production.

### 5.2 Configure the realm
Do Section 4 in the local Keycloak, using the **dev** redirect URIs (`http://localhost:8080/*`). Google (4.5) is optional for a first pass.

### 5.3 Frontend env — root `.env`
```
VUE_APP_KEYCLOAK_URL=http://localhost:8090
VUE_APP_KEYCLOAK_REALM=safepath
VUE_APP_KEYCLOAK_CLIENT_ID=safepath-frontend
VUE_APP_API_URL=http://localhost:9000/api
```

### 5.4 Backend env — root `.env`
```
KEYCLOAK_ISSUER=http://localhost:8090/realms/safepath
KEYCLOAK_JWKS_URL=http://keycloak:8080/realms/safepath/protocol/openid-connect/certs
KEYCLOAK_AUDIENCE=safepath-api
```
> **Why two URLs?** The browser reaches Keycloak at `localhost:8090`, so tokens carry `iss=http://localhost:8090/...`. But the backend container cannot resolve `localhost:8090` — it reaches Keycloak over the compose network at `keycloak:8080`. So we **validate** `iss` against `KEYCLOAK_ISSUER` while **fetching keys** from `KEYCLOAK_JWKS_URL`. (In prod both are the same host — see §9.)

### 5.5 Run + smoke test
```
docker compose up -d keycloak backend frontend
```
1. `http://localhost:8090/realms/safepath/.well-known/openid-configuration` → JSON.
2. `http://localhost:8080/login` → Login → register a user → back on `/home` authenticated; duplicate email blocked.
3. Visit `/overview` while logged out → redirected to login (route guard).

---

## 6. Production setup (reuse existing Keycloak + import realm)

Prod reuses the Keycloak already running at `login.safepath.duckdns.org`. **No new containers.** A new `safepath` realm is fully isolated from any other realm (e.g. one fronting Portainer) — never edit `master`.

### 6.1 Export the dev realm, import into prod
1. Local Keycloak → **Realm settings → Action → Partial export** (include **roles** + **clients**) → download JSON. *(Keep it out of git — it can contain secrets.)*
2. Prod Keycloak → **Create realm → Browse** the JSON → **Create**. This recreates roles, clients, the Google IdP, and login settings at once.

### 6.2 Fix prod-specific values in the imported realm
- **`safepath-frontend`** → redirect/post-logout URIs `https://safepath.duckdns.org/*`; Web origins `+`; PKCE `S256`.
- **Google IdP** → re-enter Client ID/Secret; Trust Email ON.
- **`safepath-backend`** → regenerate the client secret; verify its service-account roles survived the import.
- **Roles** → confirm `admin` composite includes `member`, and `member` is a Default role. Users do **not** import — register your admin in prod, then assign `admin`.

### 6.3 Google (prod)
- Add the prod redirect URI `https://login.safepath.duckdns.org/realms/safepath/broker/google/endpoint` to the OAuth client.
- **Publish** the OAuth consent screen (Testing → In production) so any Google user can sign in.

### 6.4 Production env — set on the server's root `.env` (git-ignored)
```
# frontend
VUE_APP_KEYCLOAK_URL=https://login.safepath.duckdns.org
VUE_APP_KEYCLOAK_REALM=safepath
VUE_APP_KEYCLOAK_CLIENT_ID=safepath-frontend
VUE_APP_API_URL=https://safepath.duckdns.org/api
# backend (same host for issuer + jwks in prod)
KEYCLOAK_ISSUER=https://login.safepath.duckdns.org/realms/safepath
KEYCLOAK_JWKS_URL=https://login.safepath.duckdns.org/realms/safepath/protocol/openid-connect/certs
KEYCLOAK_AUDIENCE=safepath-api
```
Ensure the `backend` (and `frontend`) service in the prod compose has `env_file: .env` so these are loaded.

### 6.5 Deploy & verify
- Merge to the `prod` branch and push → the deploy webhook rebuilds the stacks (or run `deploy.sh` on the server).
- Verify: `.well-known` JSON → app loads → guest search works → email register (+ duplicate blocked) → Google login → admin sees `/overview`, member is bounced → protected API returns 200 with a token, 401/403 without.

---

## 7. Application integration

### 7.1 Frontend (`keycloak-js`)
Install: `npm install keycloak-js`.

**`src/services/keycloak.js`** — one shared instance:
```js
import Keycloak from 'keycloak-js';
export default new Keycloak({
  url: process.env.VUE_APP_KEYCLOAK_URL,
  realm: process.env.VUE_APP_KEYCLOAK_REALM,
  clientId: process.env.VUE_APP_KEYCLOAK_CLIENT_ID,
});
```

**`public/silent-check-sso.html`** — required for `check-sso`:
```html
<html><body><script>parent.postMessage(location.href, location.origin)</script></body></html>
```

**`src/main.js`** — initialise Keycloak *before* mounting, then strip the OAuth params from the URL:
```js
import keycloak from './services/keycloak';

keycloak.init({
  onLoad: 'check-sso',
  silentCheckSsoRedirectUri: window.location.origin + '/silent-check-sso.html',
  pkceMethod: 'S256',
}).then(() => {
  // keycloak-js already consumed the callback; remove leftover params from the bar.
  if (/[#?&](state|session_state|iss|code)=/.test(window.location.href)) {
    const url = new URL(window.location.href);
    url.hash = '';
    ['state', 'session_state', 'iss', 'code'].forEach((p) => url.searchParams.delete(p));
    window.history.replaceState({}, document.title, url.pathname + url.search);
  }
  const app = createApp(App);
  app.use(router).use(vuetify);
  app.provide('keycloak', keycloak);
  app.mount('#app');
  setInterval(() => keycloak.updateToken(60).catch(() => keycloak.login()), 60000);
});
```

**`src/services/api.js`** — attach the token to every request:
```js
api.interceptors.request.use(async (config) => {
  if (keycloak.authenticated) {
    try { await keycloak.updateToken(30); } catch { keycloak.login(); }
    config.headers.Authorization = `Bearer ${keycloak.token}`;
  }
  return config;
});
```

**`src/router/index.js`** — guard by auth + role:
```js
router.beforeEach((to) => {
  if (to.meta.requiresAuth && !keycloak.authenticated) {
    keycloak.login({ redirectUri: window.location.origin + to.fullPath });
    return false;
  }
  if (to.meta.requiredRole && !keycloak.hasRealmRole(to.meta.requiredRole)) {
    return { path: '/home' };
  }
  return true;
});
```
Mark routes: member pages `meta: { requiresAuth: true }`; admin dashboard `meta: { requiresAuth: true, requiredRole: 'admin' }`.

**Buttons:** Login → `keycloak.login({ redirectUri: origin + '/home' })`; Google → `keycloak.login({ idpHint: 'google', redirectUri: ... })`; Register → `keycloak.register(...)`; Logout → `keycloak.logout({ redirectUri: origin + '/login' })`.

### 7.2 Backend (FastAPI JWT validation)
`requirements.txt`: add `python-jose[cryptography]`.

**`backend/auth.py`:**
```python
import os, httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from jose.exceptions import JWTError

KEYCLOAK_ISSUER   = os.environ["KEYCLOAK_ISSUER"]
KEYCLOAK_JWKS_URL = os.environ["KEYCLOAK_JWKS_URL"]
KEYCLOAK_AUDIENCE = os.environ.get("KEYCLOAK_AUDIENCE")

bearer_scheme = HTTPBearer()
_jwks = None

def _get_jwks(refresh=False):
    global _jwks
    if _jwks is None or refresh:
        _jwks = httpx.get(KEYCLOAK_JWKS_URL, timeout=10.0).json()
    return _jwks

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    try:
        kid = jwt.get_unverified_header(token).get("kid")
        key = next((k for k in _get_jwks()["keys"] if k["kid"] == kid), None)
        if key is None:
            key = next((k for k in _get_jwks(True)["keys"] if k["kid"] == kid), None)
        if key is None:
            raise JWTError("Signing key not found")
        return jwt.decode(token, key, algorithms=["RS256"],
                          issuer=KEYCLOAK_ISSUER, audience=KEYCLOAK_AUDIENCE,
                          options={"verify_aud": KEYCLOAK_AUDIENCE is not None})
    except JWTError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"Invalid token: {exc}",
                            headers={"WWW-Authenticate": "Bearer"})

def require_realm_role(role: str):
    def checker(user: dict = Depends(get_current_user)):
        if role not in user.get("realm_access", {}).get("roles", []):
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"Requires role: {role}")
        return user
    return checker
```
Validation rejects the token unless the **signature** (RS256, via JWKS), **`iss`**, **`aud`**, and **`exp`** all check out.

**Protect endpoints in `main.py`:**
```python
from auth import get_current_user, require_realm_role

@app.post("/api/routes/safe")                       # PUBLIC (guests search) → no dependency
async def get_safe_routes(req: RouteRequest): ...

@app.get("/api/admin/users")                        # admin only
async def list_users(user: dict = Depends(require_realm_role("admin"))): ...
```
Add your prod origin to the CORS `allow_origins` list.

---

## 8. Roles & access control

| Tier | Who | Access | Keycloak |
|---|---|---|---|
| **Guest** | not logged in | Home search + chatbot | nothing |
| **Member** | any logged-in user | + route details, incident, profile | `member` via **default role** |
| **Admin** | assigned users | + dashboard / management | `admin` (composite incl. `member`), assigned manually |

Frontend enforces via `keycloak.hasRealmRole(...)` (route guard + nav visibility); backend enforces via `require_realm_role(...)` on protected endpoints.

---

## 9. Dev vs prod — the differences that bite

| Aspect | dev | prod |
|---|---|---|
| Keycloak URL / TLS | `http://localhost:8090`, no TLS | `https://login.safepath.duckdns.org`, TLS via Caddy |
| Backend token check | **split** `KEYCLOAK_ISSUER` (localhost:8090) vs `KEYCLOAK_JWKS_URL` (keycloak:8080) | **same host** for both |
| Redirect URIs | `http://localhost:8080/*` | `https://safepath.duckdns.org/*` |
| Google consent screen | Testing (test users only) | **Published** (any user) |
| `.env` | local file | set on the **server** (never in git) |
| Realm | configured by hand | **imported** from dev, then fixed |

---

## 10. Verification checklist

- [ ] `…/realms/safepath/.well-known/openid-configuration` returns JSON.
- [ ] Email/password register → lands authenticated; duplicate email is blocked.
- [ ] Google login → consent → returns authenticated; user appears in Keycloak with a linked `google` identity.
- [ ] Access token contains `realm_access.roles` with `member` (and `admin` for admins).
- [ ] Guest can search + chat; visiting a member/admin route redirects to login.
- [ ] Member is bounced from `/overview`; admin loads it.
- [ ] Protected API: 200 with a valid token; 401 without; 403 for a non-admin on an admin route.
- [ ] No OAuth params linger in the address bar after login.

---

## 11. Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| `Invalid redirect_uri` on the Keycloak page | Client **Valid redirect URIs** must match the app origin exactly (`http://localhost:8080/*` or `https://safepath.duckdns.org/*`). |
| Google `redirect_uri_mismatch` (400) | The Google OAuth client's Authorized redirect URI must be the **Keycloak broker endpoint**, byte-for-byte (right host, no trailing slash). |
| Google `access_denied` | Your account isn't a **Test user** (dev), or the consent screen isn't **Published** (prod). |
| Backend 401 with a valid token | Issuer/JWKS mismatch — check the dev **split** URLs; ensure the backend loads `.env`. |
| Backend 401 about audience | Add the `safepath-api` **audience mapper** (§4.6), or unset `KEYCLOAK_AUDIENCE` to skip the check. |
| Admin bounced from `/overview` | The user has no `admin` role — assign it (§4.4); default roles don't apply retroactively. |
| Roles missing after prod import | Users don't import; re-assign `admin`. Re-check the `admin`→`member` composite and the default role. |
| OAuth params stay in the URL | Ensure the `main.js` cleanup runs after `keycloak.init()` (§7.1). |
| Icons/login broken after adding a dependency | Rebuild the frontend container and renew the anon node_modules volume. |

---

*dev and prod Keycloak are independent servers — configure dev, export, import to prod, and maintain each separately.*
