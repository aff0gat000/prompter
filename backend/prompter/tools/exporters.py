from __future__ import annotations

import json
from typing import Callable

from ..core.models import Prompt


# ---------------------------------------------------------------------------
# Export formats – the actual serialization logic
# ---------------------------------------------------------------------------

def export_messages(prompt: Prompt) -> str:
    """OpenAI chat completions format. This is the de facto standard used by
    OpenAI, Groq, Together, Mistral, Ollama, LM Studio, vLLM, Anyscale,
    Fireworks, Perplexity, DeepSeek, and many others."""
    messages = [{"role": "system", "content": prompt.content}]
    return json.dumps(messages, indent=2)


def export_markdown(prompt: Prompt) -> str:
    """Raw markdown content, used as system prompt for Claude, Gemini, and
    any provider that accepts plain-text system instructions."""
    return prompt.content


def export_text(prompt: Prompt) -> str:
    """Plain text, no wrapping."""
    return prompt.content


FORMATS: dict[str, Callable[[Prompt], str]] = {
    "messages": export_messages,
    "markdown": export_markdown,
    "text": export_text,
}

# ---------------------------------------------------------------------------
# Provider registry – maps a provider name to its preferred export format.
# Any provider not listed here falls back to "messages" because that's what
# most OpenAI-compatible APIs expect.
# ---------------------------------------------------------------------------

PROVIDERS: dict[str, str] = {
    # OpenAI-compatible (messages JSON) ────────────────────────────
    "openai":      "messages",
    "chatgpt":     "messages",
    "gpt":         "messages",
    "groq":        "messages",
    "together":    "messages",
    "mistral":     "messages",
    "ollama":      "messages",
    "lmstudio":    "messages",
    "vllm":        "messages",
    "anyscale":    "messages",
    "fireworks":   "messages",
    "perplexity":  "messages",
    "deepseek":    "messages",
    "openrouter":  "messages",
    "litellm":     "messages",
    "azure":       "messages",
    "cohere":      "messages",

    # Plain markdown / text system prompt ──────────────────────────
    "claude":      "markdown",
    "anthropic":   "markdown",
    "gemini":      "markdown",
    "google":      "markdown",
    "generic":     "text",
}

# Default format when provider is unknown – most providers speak messages
DEFAULT_FORMAT = "messages"


def get_format_for_provider(provider: str) -> str:
    return PROVIDERS.get(provider.lower().strip(), DEFAULT_FORMAT)


def list_providers() -> list[dict[str, str]]:
    return [{"provider": p, "format": f} for p, f in sorted(PROVIDERS.items())]


def export_prompt(prompt: Prompt, fmt: str) -> str:
    """Export a prompt using an explicit format name (messages, markdown, text)
    or a provider name (openai, groq, ollama, claude, etc.)."""
    # Try as a format first, then resolve as a provider
    if fmt in FORMATS:
        return FORMATS[fmt](prompt)
    resolved = PROVIDERS.get(fmt.lower().strip())
    if resolved:
        return FORMATS[resolved](prompt)
    raise ValueError(
        f"Unknown format or provider: {fmt}. "
        f"Formats: {', '.join(FORMATS)}. "
        f"Providers: {', '.join(sorted(PROVIDERS))}."
    )
