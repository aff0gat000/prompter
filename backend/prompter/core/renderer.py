from __future__ import annotations

from jinja2 import BaseLoader, StrictUndefined
from jinja2.sandbox import SandboxedEnvironment


def render_prompt(content: str, variables: dict[str, str]) -> str:
    env = SandboxedEnvironment(
        loader=BaseLoader(),
        variable_start_string="{{",
        variable_end_string="}}",
        undefined=StrictUndefined,
    )
    template = env.from_string(content)
    return template.render(**variables)
