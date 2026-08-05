"""SafePath admin — Keycloak Admin REST API client.

Lets the backend list/create/update/disable Keycloak users on behalf of the
admin dashboard (SafePathAdminUserManagement.vue). Auth is a client-credentials
service account (NOT a user's own token) — see Docs setup: the client
`KEYCLOAK_ADMIN_CLIENT_ID` must have the realm-management roles
`view-users` + `manage-users` under its Service account roles tab.

Env vars (backend .env):
    KEYCLOAK_BASE_URL           e.g. http://keycloak:8080   (internal docker host)
    KEYCLOAK_REALM              e.g. safepath
    KEYCLOAK_ADMIN_CLIENT_ID    e.g. safepath-backend-admin
    KEYCLOAK_ADMIN_CLIENT_SECRET
"""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from typing import Any

import httpx

KEYCLOAK_BASE_URL = os.getenv("KEYCLOAK_BASE_URL")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM")
KEYCLOAK_ADMIN_CLIENT_ID = os.getenv("KEYCLOAK_ADMIN_CLIENT_ID")
KEYCLOAK_ADMIN_CLIENT_SECRET = os.getenv("KEYCLOAK_ADMIN_CLIENT_SECRET")

# The Edit modal's role dropdown only offers these three — keep in sync with
# the realm roles you created in Keycloak. Index = priority when a user
# happens to hold more than one (Admin beats Member).
KNOWN_ROLES = ["Admin", "Member"]


class KeycloakConfigError(RuntimeError):
    """Raised when the Keycloak admin-client env vars are missing."""


def _require_config() -> None:
    missing = [
        name
        for name, val in [
            ("KEYCLOAK_BASE_URL", KEYCLOAK_BASE_URL),
            ("KEYCLOAK_REALM", KEYCLOAK_REALM),
            ("KEYCLOAK_ADMIN_CLIENT_ID", KEYCLOAK_ADMIN_CLIENT_ID),
            ("KEYCLOAK_ADMIN_CLIENT_SECRET", KEYCLOAK_ADMIN_CLIENT_SECRET),
        ]
        if not val
    ]
    if missing:
        raise KeycloakConfigError(
            f"Missing Keycloak admin env vars: {', '.join(missing)}. "
        )

_token_cache: dict[str, Any] = {"access_token": None, "expires_at": 0.0}


"""Admin token - cached, auto-refreshed"""
def _fetch_admin_token() -> dict[str, Any]:
    url = f"{KEYCLOAK_BASE_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
    resp = httpx.post(
        url,
        data={
            "grant_type": "client_credentials",
            "client_id": KEYCLOAK_ADMIN_CLIENT_ID,
            "client_secret": KEYCLOAK_ADMIN_CLIENT_SECRET,
        },
        timeout=10.0,
    )
    resp.raise_for_status()
    return resp.json()


def _get_admin_token(force_refresh: bool = False) -> str:
    _require_config()
    now = time.time()
    if force_refresh or _token_cache["access_token"] is None or now >= _token_cache["expires_at"]:
        data = _fetch_admin_token()
        _token_cache["access_token"] = data["access_token"]
        # Refresh 30s early so we don't race the real expiry.
        _token_cache["expires_at"] = now + data.get("expires_in", 60) - 30
    return _token_cache["access_token"]


"""Request helper (retires once on an expired token)"""
def _kc_request(method: str, path: str, **kwargs) -> httpx.Response:
    """One authenticated call to `{KEYCLOAK_BASE_URL}/admin/realms/{realm}{path}`.

    Retries once with a forced token refresh on a 401 (token expired/rotated
    between our cache check and the actual call).
    """
    url = f"{KEYCLOAK_BASE_URL}/admin/realms/{KEYCLOAK_REALM}{path}"
    token = _get_admin_token()
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {token}"

    resp = httpx.request(method, url, headers=headers, timeout=10.0, **kwargs)
    if resp.status_code == 401:
        token = _get_admin_token(force_refresh=True)
        headers["Authorization"] = f"Bearer {token}"
        resp = httpx.request(method, url, headers=headers, timeout=10.0, **kwargs)

    resp.raise_for_status()
    return resp


"""Shaping one Keycloak user into a table row"""
def _display_name(user: dict[str, Any]) -> str:
    first, last = user.get("firstName", ""), user.get("lastName", "")
    full = f"{first} {last}".strip()
    return full or user.get("username", "Unknown")


def _created_at(user: dict[str, Any]) -> str:
    ts = user.get("createdTimestamp")
    if not ts:
        return ""
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d")


def _fetch_role(user_id: str) -> str:
    resp = _kc_request("GET", f"/users/{user_id}/role-mappings/realm")
    held = {r["name"] for r in resp.json()}
    return next((r for r in KNOWN_ROLES if r in held), "Member")


def _fetch_provider(user_id: str) -> str:
    resp = _kc_request("GET", f"/users/{user_id}/federated-identity")
    identities = resp.json()
    if identities:
        return identities[0]["identityProvider"].capitalize()
    return "Email"


def _to_row(user: dict[str, Any]) -> dict[str, Any]:
    name = _display_name(user)
    return {
        "id": user["id"],
        "initial": (name[:1] or "U").upper(),
        "name": name,
        "email": user.get("email", ""),
        "role": _fetch_role(user["id"]),
        "provider": _fetch_provider(user["id"]),
        "status": "Active" if user.get("enabled", True) else "Suspended",
        "createdAt": _created_at(user),
    }

def fetch_user(user_id: str) -> dict[str, Any]:
    """Raw Keycloak representation of one user (used by the /api/me route)."""
    return _kc_request("GET", f"/users/{user_id}").json()


"""Public functions used by the FastAPI routes"""
def fetch_users(search: str = "", first: int = 0, max: int = 20) -> dict[str, Any]:
    """One page of users, newest-first isn't native to Keycloak's list endpoint,
    so we sort client-side by createdTimestamp desc."""
    params = {"first": first, "max": max, "briefRepresentation": "false"}
    if search:
        params["search"] = search

    users_resp = _kc_request("GET", "/users", params=params)
    count_resp = _kc_request(
        "GET", "/users/count", params={"search": search} if search else {}
    )

    users = sorted(
        users_resp.json(), key=lambda u: u.get("createdTimestamp", 0), reverse=True
    )
    return {"users": [_to_row(u) for u in users], "total": count_resp.json()}


def create_user(*, name: str, email: str, role: str) -> dict[str, Any]:
    first, _, last = name.partition(" ")
    payload = {
        "username": email,
        "email": email,
        "firstName": first or name,
        "lastName": last,
        "enabled": True,
        "emailVerified": False,
        "credentials": [
            {"type": "password", "value": os.urandom(16).hex(), "temporary": True}
        ],
        "requiredActions": ["UPDATE_PASSWORD"],
    }
    resp = _kc_request("POST", "/users", json=payload)
    # Keycloak returns 201 with no body; the new user's id is in Location header.
    user_id = resp.headers["Location"].rsplit("/", 1)[-1]
    _assign_role(user_id, role)
    return _to_row(_kc_request("GET", f"/users/{user_id}").json())


def update_user(user_id: str, *, name: str, email: str, role: str) -> dict[str, Any]:
    first, _, last = name.partition(" ")
    _kc_request(
        "PUT",
        f"/users/{user_id}",
        json={
            "firstName": first or name,
            "lastName": last,
            "email": email
            },
    )
    _assign_role(user_id, role)
    return _to_row(_kc_request("GET", f"/users/{user_id}").json())


def delete_user(user_id: str) -> None:
    _kc_request("DELETE", f"/users/{user_id}")


def _assign_role(user_id: str, role: str) -> None:
    """Make `role` the user's only KNOWN_ROLES realm role (removes the others)."""
    if role not in KNOWN_ROLES:
        return
    held_resp = _kc_request("GET", f"/users/{user_id}/role-mappings/realm")
    held = {r["name"]: r for r in held_resp.json()}

    to_remove = [held[r] for r in KNOWN_ROLES if r in held and r != role]
    if to_remove:
        _kc_request("DELETE", f"/users/{user_id}/role-mappings/realm", json=to_remove)

    if role not in held:
        available_resp = _kc_request("GET", f"/users/{user_id}/role-mappings/realm/available")
        role_rep = next((r for r in available_resp.json() if r["name"] == role), None)
        if role_rep is None:
            raise KeycloakConfigError(
                f"Realm role '{role}' does not exist in Keycloak (or isn't assignable)."
            )
        _kc_request("POST", f"/users/{user_id}/role-mappings/realm", json=[role_rep])