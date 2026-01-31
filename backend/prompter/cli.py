from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .core.models import PromptCreate, PromptUpdate
from .core.renderer import render_prompt
from .core.store import PromptStore
from .tools.exporters import export_prompt, list_providers

app = typer.Typer(help="Prompter - Prompt engineering toolkit")
console = Console()

DEFAULT_DIR = os.environ.get("PROMPTER_DIR", os.path.join(os.getcwd(), "prompts"))


def _store() -> PromptStore:
    return PromptStore(DEFAULT_DIR)


@app.command()
def init():
    """Initialize a prompts directory."""
    store = _store()
    store.init()
    console.print(f"Initialized prompts directory: {store.directory}")


@app.command("list")
def list_prompts():
    """List all prompts."""
    store = _store()
    items = store.list_prompts()
    if not items:
        console.print("No prompts found.")
        return
    table = Table()
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Tags")
    table.add_column("Tool")
    for item in items:
        table.add_row(item.name, item.description, ", ".join(item.tags), item.tool)
    console.print(table)


@app.command()
def show(name: str):
    """Display a prompt."""
    store = _store()
    prompt = store.get_prompt(name)
    console.print(f"[bold]{prompt.name}[/bold]")
    if prompt.description:
        console.print(f"[dim]{prompt.description}[/dim]")
    if prompt.tags:
        console.print(f"Tags: {', '.join(prompt.tags)}")
    console.print(f"Tool: {prompt.tool}")
    if prompt.variables:
        console.print(f"Variables: {', '.join(prompt.variables)}")
    console.print()
    console.print(prompt.content)


@app.command()
def create(
    name: str,
    description: str = typer.Option("", "--desc", "-d"),
    tags: str = typer.Option("", "--tags", "-t", help="Comma-separated tags"),
    tool: str = typer.Option("generic", "--tool"),
    content: Optional[str] = typer.Option(None, "--content", "-c"),
):
    """Create a new prompt."""
    store = _store()
    store.init()
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    body = content or ""
    if not content and not sys.stdin.isatty():
        body = sys.stdin.read()
    data = PromptCreate(name=name, description=description, content=body, tags=tag_list, tool=tool)
    prompt = store.create_prompt(data)
    console.print(f"Created prompt: {prompt.id}")


@app.command()
def edit(name: str):
    """Open a prompt in $EDITOR."""
    store = _store()
    prompt = store.get_prompt(name)
    editor = os.environ.get("EDITOR", "vi")
    with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
        f.write(prompt.content)
        f.flush()
        subprocess.call([editor, f.name])
        f_path = f.name
    new_content = Path(f_path).read_text()
    os.unlink(f_path)
    store.update_prompt(name, PromptUpdate(content=new_content))
    console.print(f"Updated prompt: {name}")


@app.command()
def render(
    name: str,
    var: list[str] = typer.Option([], "--var", "-v", help="key=value pairs"),
):
    """Render a prompt with variable substitution."""
    store = _store()
    prompt = store.get_prompt(name)
    variables = {}
    for v in var:
        if "=" not in v:
            console.print(f"[red]Invalid variable format: {v} (expected key=value)[/red]")
            raise typer.Exit(1)
        k, val = v.split("=", 1)
        variables[k.strip()] = val.strip()
    result = render_prompt(prompt.content, variables)
    console.print(result)


@app.command()
def export(
    name: str,
    fmt: str = typer.Option("text", "--format", "-f", help="Format or provider name (messages, markdown, text, openai, groq, ollama, claude, etc.)"),
):
    """Export a prompt for any provider. Use --format with a format name (messages, markdown, text) or a provider name (openai, groq, ollama, claude, etc.)."""
    store = _store()
    prompt = store.get_prompt(name)
    result = export_prompt(prompt, fmt)
    console.print(result)


@app.command()
def providers():
    """List all supported providers and their export formats."""
    table = Table()
    table.add_column("Provider")
    table.add_column("Export Format")
    for entry in list_providers():
        table.add_row(entry["provider"], entry["format"])
    console.print(table)
    console.print()
    console.print("[dim]Any unlisted provider defaults to 'messages' (OpenAI-compatible).[/dim]")
    console.print("[dim]You can use any string as a tool name in your prompts.[/dim]")


def serve(
    host: str = "127.0.0.1",
    port: int = 8000,
):
    """Start the API server."""
    import uvicorn
    uvicorn.run("prompter.api:app", host=host, port=port, reload=True)


app.command()(serve)


if __name__ == "__main__":
    app()
