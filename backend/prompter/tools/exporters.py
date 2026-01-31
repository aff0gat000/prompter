from __future__ import annotations

import json

from ..core.models import Prompt


def export_markdown(prompt: Prompt) -> str:
    return prompt.content


def export_openai(prompt: Prompt) -> str:
    messages = [{"role": "system", "content": prompt.content}]
    return json.dumps(messages, indent=2)


def export_text(prompt: Prompt) -> str:
    return prompt.content


EXPORTERS = {
    "claude": export_markdown,
    "openai": export_openai,
    "text": export_text,
}


def export_prompt(prompt: Prompt, fmt: str) -> str:
    exporter = EXPORTERS.get(fmt)
    if not exporter:
        raise ValueError(f"Unknown format: {fmt}. Available: {', '.join(EXPORTERS)}")
    return exporter(prompt)
