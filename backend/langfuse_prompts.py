"""Langfuse Prompt Management for SafePath (read-only fetch).

Fetches managed prompts from the self-hosted Langfuse instance using the
official Python SDK (v3). Prompts are authored/versioned in the Langfuse UI
under "Prompts" and pulled at request time here, so prompt changes do not
require a backend redeploy.

Auth is read from the same environment variables as langfuse_monitor:

  LANGFUSE_PUBLIC_KEY=pk-lf-...
  LANGFUSE_SECRET_KEY=sk-lf-...
  LANGFUSE_HOST / LANGFUSE_BASE_URL=https://langfuse.safepath.duckdns.org

If Langfuse is unreachable or the prompt is missing, the caller-supplied
`fallback` text is used so routing never breaks.

Prompt names (must match what is created in the Langfuse UI):
  ROUTE_SAFETY_PROMPT      -> "safepath-route-safety"  (text prompt)

Variables use Langfuse mustache syntax ({{var}}); compile() substitutes them.

---------------------------------------------------------------------------
Perf note (see get_safe_routes latency investigation):

The SDK's own default for get_prompt() is up to 2 retries with a ~5s
per-attempt timeout and ~1s backoff between attempts — a full failure can
cost ~15-17s before the caller-supplied fallback kicks in, since the SDK
still has to exhaust its retry budget first. Bounding both (FETCH_MAX_RETRIES
/ FETCH_TIMEOUT_SECONDS) got a real request down from 16.75s to 6.89s — but
that 6.89s (~2 attempts x 3s timeout + backoff) shows the fetch is STILL
failing/timing out on every attempt, just faster. That means the request
path can never rely on this fetch succeeding in reasonable time.

So the request path (fetch_prompt/get_compiled_prompt) does NOT make network
calls at all anymore. A background thread (start_background_refresh) owns
the only network calls to Langfuse's prompt API, on a fixed interval, and
publishes whatever it gets (real prompt or the local fallback) into a
module-level slot. get_cached_prompt() just reads that slot — zero network,
effectively instant — which is what main.py's request path now calls.
compile_prompt() then does the (local, no-network) variable substitution.
---------------------------------------------------------------------------
"""

from __future__ import annotations

import os
import threading
import time
from typing import Any

# Reuse the cached client from the monitor module so we only build one
# Langfuse client per process.
from langfuse_monitor import LangfuseConfigError, get_client

# Label to pull. "production" is Langfuse's convention for the live version.
PROMPT_LABEL = os.getenv("LANGFUSE_PROMPT_LABEL", "production")

# Canonical prompt names in Langfuse. Overridable via env so the name can be
# changed without a code edit (must match the prompt name in the Langfuse UI).
ROUTE_SAFETY_PROMPT = os.getenv("LANGFUSE_ROUTE_PROMPT_NAME", "safepath-route-safety")

# How long a fetched (or fallback) prompt stays cached in the SDK's own cache.
CACHE_TTL_SECONDS = 300
# Bounded retry/timeout so one background refresh attempt costs seconds, not ~17s.
FETCH_MAX_RETRIES = int(os.getenv("LANGFUSE_PROMPT_MAX_RETRIES", "1"))
FETCH_TIMEOUT_SECONDS = int(os.getenv("LANGFUSE_PROMPT_FETCH_TIMEOUT_SECONDS", "3"))
# How often the background thread retries fetching from Langfuse.
REFRESH_INTERVAL_SECONDS = int(os.getenv("LANGFUSE_PROMPT_REFRESH_SECONDS", "240"))


class _FallbackPrompt:
    """Minimal stand-in with the same `.compile(**vars)` interface as a
    Langfuse PromptClient. Used only when we can't even reach client.get_prompt
    (e.g. missing credentials) — client.get_prompt's own `fallback=` argument
    already covers network/API failures by returning a real fallback
    PromptClient, so this class is the last-resort path underneath that.
    """

    def __init__(self, text: str) -> None:
        self._text = text

    def compile(self, **variables: Any) -> str:
        return _local_compile(self._text, variables)


def fetch_prompt(
    name: str,
    *,
    fallback: str,
    label: str | None = None,
) -> Any:
    """Fetch (or return the cached copy of) a prompt object, WITHOUT
    compiling any variables into it yet — call `.compile(**variables)` on
    the result once you have them. Safe to call concurrently with other I/O
    (e.g. via asyncio.to_thread) since it doesn't need route data.

    Never raises: falls back to a local `_FallbackPrompt` wrapping `fallback`
    if Langfuse credentials aren't configured or the fetch fails outright.
    """
    try:
        client = get_client()
    except LangfuseConfigError:
        return _FallbackPrompt(fallback)

    try:
        # client.get_prompt already returns a fallback-wrapping PromptClient
        # (with a working .compile()) on fetch failure when `fallback` is
        # given, so this rarely raises — the try/except is defense in depth.
        return client.get_prompt(
            name,
            label=label or PROMPT_LABEL,
            cache_ttl_seconds=CACHE_TTL_SECONDS,
            fallback=fallback,
            max_retries=FETCH_MAX_RETRIES,
            fetch_timeout_seconds=FETCH_TIMEOUT_SECONDS,
        )
    except Exception as exc:  # noqa: BLE001 - degrade gracefully
        print(f"[LANGFUSE] prompt '{name}' fetch failed, using fallback: {exc}")
        return _FallbackPrompt(fallback)


def compile_prompt(prompt: Any, variables: dict[str, Any], *, fallback: str) -> str:
    """Compile a prompt object (from fetch_prompt / warm_prompt_cache) with
    `variables`. Purely local/in-memory — no network call — so this is safe
    to do inline in the request path even though fetch_prompt() isn't.
    """
    try:
        return prompt.compile(**variables)
    except Exception as exc:  # noqa: BLE001 - degrade gracefully
        print(f"[LANGFUSE] prompt compile failed, using local fallback: {exc}")
        return _local_compile(fallback, variables)


def get_compiled_prompt(
    name: str,
    variables: dict[str, Any],
    *,
    fallback: str,
    label: str | None = None,
) -> str:
    """Convenience one-shot wrapper: fetch `name` from Langfuse and compile it
    with `variables`. Still a single blocking network call — do NOT use this
    in a request path; use get_cached_prompt() + compile_prompt() instead
    (see below). Kept for scripts/one-off use outside the API.
    """
    prompt = fetch_prompt(name, fallback=fallback, label=label)
    return compile_prompt(prompt, variables, fallback=fallback)


# --------------------------------------------------------------------------- #
# Background-refreshed cache: the only thing request handlers should touch.
#
# _cached_prompts holds the last prompt object successfully (or fallback-ily)
# fetched for each name, written ONLY by the background refresh thread below.
# get_cached_prompt() reads it with zero network I/O, so it's safe to call
# inline in an async request handler without blocking anything.
# --------------------------------------------------------------------------- #
_cache_lock = threading.Lock()
_cached_prompts: dict[str, Any] = {}


def get_cached_prompt(name: str, *, fallback: str) -> Any:
    """Return whatever prompt object is currently cached in-process, with NO
    network call. If the background refresher hasn't populated this name yet
    (e.g. very first seconds after process start, before its first fetch
    completes), returns a local `_FallbackPrompt` so callers always get a
    working `.compile()`.
    """
    with _cache_lock:
        cached = _cached_prompts.get(name)
    return cached if cached is not None else _FallbackPrompt(fallback)


def refresh_prompt_cache_once(name: str = ROUTE_SAFETY_PROMPT, *, fallback: str, label: str | None = None) -> None:
    """Do one bounded network fetch and publish the result into the
    in-process cache read by get_cached_prompt(). This is the ONLY function
    in this module that a background thread should call — never call it from
    a request handler, since fetch_prompt() can still take a few seconds
    (bounded by FETCH_MAX_RETRIES/FETCH_TIMEOUT_SECONDS) if Langfuse is slow
    or unreachable.
    """
    prompt = fetch_prompt(name, fallback=fallback, label=label)
    with _cache_lock:
        _cached_prompts[name] = prompt


def start_background_refresh(
    name: str = ROUTE_SAFETY_PROMPT,
    *,
    fallback: str,
    label: str | None = None,
    interval_seconds: int = REFRESH_INTERVAL_SECONDS,
) -> None:
    """Start a daemon thread that fetches `name` immediately and then keeps
    refreshing it every `interval_seconds`, forever. Call this once from
    main.py's startup handler. Request handlers never wait on this thread —
    they just read whatever it last published via get_cached_prompt().

    Runs in a plain daemon thread (not asyncio) so it keeps working
    regardless of event-loop activity, and a hung/slow HTTP call in one
    cycle can never block app startup or any request.
    """

    def _loop() -> None:
        while True:
            try:
                refresh_prompt_cache_once(name, fallback=fallback, label=label)
                print(f"[LANGFUSE] prompt '{name}' cache refreshed.")
            except Exception as exc:  # noqa: BLE001 - refresher must never die/crash the app
                print(f"[LANGFUSE] prompt '{name}' background refresh failed (non-fatal): {exc}")
            time.sleep(interval_seconds)

    threading.Thread(target=_loop, daemon=True).start()


def _local_compile(text: str, variables: dict[str, Any]) -> str:
    """Compile a mustache-style fallback string locally ({{var}} -> value).

    Used when the SDK is not available at all. Mirrors Langfuse's basic
    substitution so the fallback prompt behaves like the managed one.
    """
    out = text
    for key, value in variables.items():
        out = out.replace("{{" + key + "}}", str(value))
        out = out.replace("{{ " + key + " }}", str(value))
    return out
