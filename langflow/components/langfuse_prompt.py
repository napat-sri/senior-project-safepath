"""Langflow custom component: fetch a managed prompt from Langfuse.

Pulls a prompt authored in Langfuse Prompt Management and outputs it as a
Message, so the Agent's *System Message / Agent Instructions* can be sourced
from Langfuse instead of being hard-coded inside the flow. Prompt edits in the
Langfuse UI then take effect without re-exporting the flow.

The langflow-langfuse image already bundles the Langfuse v3 SDK
(see Dockerfile.langflow), so `from langfuse import Langfuse` works.

How to use in Langflow
----------------------
1. In the Langflow builder open the SafePathAgent flow.
2. Add a Custom Component (or set LANGFLOW_COMPONENTS_PATH to this folder and
   restart Langflow so it appears under "Custom" automatically).
3. Fill the inputs:
     - Prompt Name:  safepath-navigator-system
     - Label:        production
     - Public/Secret Key + Host: same values as the backend .env
       (LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY / LANGFUSE_HOST).
       Host inside docker-compose is http://langfuse-web:3000.
     - Fallback: paste the current system prompt as a safety net (optional).
4. Connect this component's "Prompt" output to the Agent node's
   **System Message** (a.k.a. Agent Instructions) input handle.
5. Remove the inline text from the Agent's system_prompt so the value comes
   only from this component.
"""

from __future__ import annotations

from langflow.custom import Component
from langflow.io import MessageTextInput, Output, SecretStrInput, StrInput
from langflow.schema.message import Message


class LangfusePromptComponent(Component):
    display_name = "Langfuse Prompt"
    description = "Fetch a managed prompt from Langfuse Prompt Management."
    documentation = "https://langfuse.com/docs/prompts/get-started"
    icon = "book-open"
    name = "LangfusePrompt"

    inputs = [
        StrInput(
            name="prompt_name",
            display_name="Prompt Name",
            value="safepath-navigator-system",
            info="Exact prompt name as created in the Langfuse UI.",
        ),
        StrInput(
            name="label",
            display_name="Label",
            value="production",
            advanced=True,
            info="Langfuse label/version to fetch (default: production).",
        ),
        SecretStrInput(
            name="public_key",
            display_name="Langfuse Public Key",
            info="LANGFUSE_PUBLIC_KEY (pk-lf-...).",
        ),
        SecretStrInput(
            name="secret_key",
            display_name="Langfuse Secret Key",
            info="LANGFUSE_SECRET_KEY (sk-lf-...).",
        ),
        StrInput(
            name="host",
            display_name="Langfuse Host",
            value="http://langfuse-web:3000",
            info="Internal URL inside docker-compose, or the public HTTPS URL.",
        ),
        MessageTextInput(
            name="fallback",
            display_name="Fallback Prompt",
            advanced=True,
            info="Used verbatim if Langfuse is unreachable or the prompt is missing.",
        ),
    ]

    outputs = [
        Output(display_name="Prompt", name="prompt", method="build_prompt"),
    ]

    def build_prompt(self) -> Message:
        text = self._fetch_prompt()
        return Message(text=text)

    # ------------------------------------------------------------------ #
    def _fetch_prompt(self) -> str:
        fallback = (self.fallback or "").strip()
        try:
            from langfuse import Langfuse

            client = Langfuse(
                public_key=self.public_key,
                secret_key=self.secret_key,
                host=self.host,
            )
            prompt = client.get_prompt(
                self.prompt_name,
                label=self.label or "production",
                cache_ttl_seconds=300,
                fallback=fallback or None,
            )
            text = prompt.compile()
            version = getattr(prompt, "version", "?")
            self.status = f"Fetched '{self.prompt_name}' v{version} from Langfuse"
            return text
        except Exception as exc:  # noqa: BLE001 - degrade gracefully
            self.status = f"Langfuse fetch failed ({exc}); using fallback"
            return fallback
