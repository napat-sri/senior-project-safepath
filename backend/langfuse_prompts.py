"""Langfuse Prompt Management for SafePath (read-only fetch).

Fetches managed prompts from the self-hosted Langfuse instance using the
official Python SDK (v3). Prompts are authored/versioned in the Langfuse UI
under "Prompts" and pulled at request time here, so prompt changes do not
require a backend redeploy.

Auth is read from the same environment variables as langfuse_monitor:

  LANGFUSE_PUBLIC_KEY=pk-lf-...
  LANGFUSE_SECRET_KEY=sk-lf-...
  LANGFUSE_HOST=https://langfuse.safepath.duckdns.org   # or internal compose URL

If Langfuse is unreachable or the prompt is missing, the caller-supplied
`fallback` text is used so routing never breaks.

Prompt names (must match what is created in the Langfuse UI):
  ROUTE_SAFETY_PROMPT      -> "safepath-route-safety"  (text prompt)

Variables use Langfuse mustache syntax ({{var}}); compile() substitutes them.
"""

from __future__ import annotations

import os
from typing import Any

# Reuse the cached client from the monitor module so we only build one
# Langfuse client per process.
from langfuse_monitor import get_client, LangfuseConfigError

# Label to pull. "production" is Langfuse's convention for the live version.
PROMPT_LABEL = os.getenv("LANGFUSE_PROMPT_LABEL", "production")

# Canonical prompt names in Langfuse. Overridable via env so the name can be
# changed without a code edit (must match the prompt name in the Langfuse UI).
ROUTE_SAFETY_PROMPT = os.getenv("LANGFUSE_ROUTE_PROMPT_NAME", "safepath-route-safety")


def get_compiled_prompt(
    name: str,
    variables: dict[str, Any],
    *,
    fallback: str,
    label: str | None = None,
) -> str:
    """Fetch `name` from Langfuse and compile it with `variables`.

    Falls back to `fallback` (already a plain string) if Langfuse is
    unreachable, misconfigured, or the prompt does not exist. Never raises.
    """
    try:
        client = get_client()
        prompt = client.get_prompt(
            name,
            label=label or PROMPT_LABEL,
            # Cache the prompt in-process for 5 min; also serves as an
            # offline fallback if a later refresh fails.
            cache_ttl_seconds=300,
            fallback=fallback,
        )
        # .compile() replaces {{var}} placeholders. Extra/missing keys are
        # tolerated by the SDK (missing ones are left as-is).
        return prompt.compile(**variables)
    except LangfuseConfigError:
        # Credentials not set — use the local fallback silently.
        return _local_compile(fallback, variables)
    except Exception as exc:  # noqa: BLE001 - degrade gracefully
        print(f"[LANGFUSE] prompt '{name}' fetch failed, using fallback: {exc}")
        return _local_compile(fallback, variables)


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
