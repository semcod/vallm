"""LLM backend abstraction for vallm SemanticValidator.

Protocol + concrete implementations so semantic.py is not coupled to
litellm / ollama / urllib at module load time.
"""

from __future__ import annotations

import json
import urllib.request
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class LLMBackend(Protocol):
    """Minimal single-turn LLM completion interface."""

    def complete(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        api_base: str | None = None,
    ) -> str:
        """Return assistant message content string."""
        ...


class LitellmBackend:
    """Multi-provider backend via litellm."""

    def complete(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        api_base: str | None = None,
    ) -> str:
        import litellm  # type: ignore

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if api_base:
            kwargs["api_base"] = api_base
        response = litellm.completion(**kwargs)
        return str(response.choices[0].message.content or "").strip()


class OllamaBackend:
    """Backend using the ollama Python package."""

    def complete(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        api_base: str | None = None,
    ) -> str:
        import ollama  # type: ignore

        host = api_base or "http://localhost:11434"
        client = ollama.Client(host=host)
        response = client.chat(
            model=model,
            messages=messages,
            options={"temperature": temperature},
        )
        return str(response["message"]["content"]).strip()


class HttpOllamaBackend:
    """Fallback HTTP backend — no external deps, calls Ollama REST API."""

    def complete(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        api_base: str | None = None,
    ) -> str:
        base = (api_base or "http://localhost:11434").rstrip("/")
        url = f"{base}/api/chat"
        payload = json.dumps(
            {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {"temperature": temperature},
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return str(data["message"]["content"]).strip()


def get_backend(
    provider: str,
    *,
    backend: LLMBackend | None = None,
) -> LLMBackend:
    """Return explicit backend or construct one from provider name."""
    if backend is not None:
        return backend
    p = provider.lower()
    if p == "litellm":
        return LitellmBackend()
    if p == "ollama":
        try:
            import ollama  # noqa: F401
            return OllamaBackend()
        except ImportError:
            return HttpOllamaBackend()
    return HttpOllamaBackend()


__all__ = [
    "LLMBackend",
    "LitellmBackend",
    "OllamaBackend",
    "HttpOllamaBackend",
    "get_backend",
]
