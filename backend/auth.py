import os

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from jose.exceptions import JWTError

# (a) config — note the two separate URLs
KEYCLOAK_ISSUER   = os.environ["KEYCLOAK_ISSUER"]     # what the token's `iss` must equal
KEYCLOAK_JWKS_URL = os.environ["KEYCLOAK_JWKS_URL"]   # where to fetch the public keys
KEYCLOAK_AUDIENCE = os.environ.get("KEYCLOAK_AUDIENCE")

# (b) tells FastAPI to read the "Authorization: Bearer <token>" header
bearer_scheme = HTTPBearer()
_jwks_cache = None

# (c) fetch Keycloak's public keys once, then reuse
def _get_jwks(force_refresh=False):
    global _jwks_cache
    if _jwks_cache is None or force_refresh:
        _jwks_cache = httpx.get(KEYCLOAK_JWKS_URL, timeout=10.0).json()
    return _jwks_cache

# (d) the dependency every protected endpoint uses
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    try:
        kid = jwt.get_unverified_header(token).get("kid")          # which key signed this?
        key = next((k for k in _get_jwks()["keys"] if k["kid"] == kid), None)
        if key is None:                                            # key rotated → refetch once
            key = next((k for k in _get_jwks(True)["keys"] if k["kid"] == kid), None)
        if key is None:
            raise JWTError("Signing key not found")

        return jwt.decode(                                         # the actual verification
            token, key, algorithms=["RS256"],
            issuer=KEYCLOAK_ISSUER,
            audience=KEYCLOAK_AUDIENCE,
            options={"verify_aud": KEYCLOAK_AUDIENCE is not None},
        )
    except JWTError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"Invalid token: {exc}",
                            headers={"WWW-Authenticate": "Bearer"})


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """FastAPI dependency: 403s unless the caller's token has the Admin realm role.

    Chains off get_current_user, so a request first proves it's a *valid,
    signed* Keycloak token (get_current_user), then this checks *which* roles
    that token carries. Mirrors the frontend's own
    `keycloak.hasRealmRole('Admin')` check (SafePathNavDrawer.vue,
    router/index.js) — but done server-side, where it can't be bypassed by
    calling the API directly instead of going through the Vue app.
    """
    roles = user.get("realm_access", {}).get("roles", [])
    if "Admin" not in roles:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Admin role required.",
        )
    return user