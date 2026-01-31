from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

import yaml

from ..core.models import Prompt


# ---------------------------------------------------------------------------
# Export formats – the actual serialization logic
# ---------------------------------------------------------------------------

def export_messages(prompt: Prompt) -> str:
    """OpenAI chat completions format. Used by OpenAI, Groq, Together,
    Mistral, Ollama, LM Studio, vLLM, DeepSeek, and many others."""
    messages = [{"role": "system", "content": prompt.content}]
    return json.dumps(messages, indent=2)


def export_markdown(prompt: Prompt) -> str:
    """Raw markdown content, used as system prompt for Claude, Gemini, etc."""
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
# Built-in provider registry (baseline defaults)
# ---------------------------------------------------------------------------

BUILTIN_PROVIDERS: dict[str, str] = {
    # OpenAI-compatible (messages JSON)
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

    # Plain markdown / text system prompt
    "claude":      "markdown",
    "anthropic":   "markdown",
    "gemini":      "markdown",
    "google":      "markdown",
    "generic":     "text",
}

DEFAULT_FORMAT = "messages"

# ---------------------------------------------------------------------------
# Config file: providers.yaml
# ---------------------------------------------------------------------------

_CONFIG_FILENAME = "providers.yaml"

DEFAULT_CONFIG = """\
# Prompter provider registry
# Maps provider names to export formats: messages, markdown, or text.
#
# Built-in providers are always available. Add your own here to extend
# or override them. Changes take effect immediately — no restart needed.
#
# Format reference:
#   messages  - OpenAI chat completions JSON [{"role":"system","content":"..."}]
#   markdown  - Raw markdown (Claude, Gemini system prompts)
#   text      - Plain text
#
# Examples:
#   my-local-llm: messages
#   custom-api: markdown

providers:
  # Add custom providers below. These merge with (and override) built-ins.
  # my-company-llm: messages
  # internal-api: markdown
"""


def load_config(directory: str | Path | None) -> dict[str, str]:
    """Load providers.yaml from the given directory and merge with built-ins.
    User entries override built-in entries."""
    merged = dict(BUILTIN_PROVIDERS)
    if directory is None:
        return merged
    config_path = Path(directory) / _CONFIG_FILENAME
    if not config_path.exists():
        return merged
    with open(config_path) as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        return merged
    user_providers = data.get("providers")
    if isinstance(user_providers, dict):
        for name, fmt in user_providers.items():
            if isinstance(name, str) and isinstance(fmt, str) and fmt in FORMATS:
                merged[name.lower().strip()] = fmt.lower().strip()
    return merged


def init_config(directory: str | Path) -> Path:
    """Create a default providers.yaml if one doesn't exist. Returns the path."""
    config_path = Path(directory) / _CONFIG_FILENAME
    if not config_path.exists():
        config_path.write_text(DEFAULT_CONFIG)
    return config_path


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_format_for_provider(provider: str, directory: str | Path | None = None) -> str:
    providers = load_config(directory)
    return providers.get(provider.lower().strip(), DEFAULT_FORMAT)


def list_providers(directory: str | Path | None = None) -> list[dict[str, str]]:
    providers = load_config(directory)
    return [{"provider": p, "format": f} for p, f in sorted(providers.items())]


def export_prompt(prompt: Prompt, fmt: str, directory: str | Path | None = None) -> str:
    """Export a prompt using an explicit format name (messages, markdown, text)
    or a provider name (openai, groq, ollama, claude, etc.).
    Reads providers.yaml from directory if provided."""
    if fmt in FORMATS:
        return FORMATS[fmt](prompt)
    providers = load_config(directory)
    resolved = providers.get(fmt.lower().strip())
    if resolved:
        return FORMATS[resolved](prompt)
    # Unknown provider → default to messages (OpenAI-compatible)
    return FORMATS[DEFAULT_FORMAT](prompt)
