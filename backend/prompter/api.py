from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .core.models import Prompt, PromptCreate, PromptListItem, PromptUpdate, RenderRequest
from .core.renderer import render_prompt
from .core.store import PromptStore, TemplateStore, load_hints, load_scaffold
from .tools.exporters import export_prompt, list_providers

app = FastAPI(title="Prompter API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULT_DIR = os.environ.get("PROMPTER_DIR", os.path.join(os.getcwd(), "prompts"))


def _store() -> PromptStore:
    return PromptStore(DEFAULT_DIR)


def _template_store() -> TemplateStore:
    return TemplateStore()


@app.get("/prompts", response_model=list[PromptListItem])
def list_prompts_route():
    return _store().list_prompts()


@app.get("/prompts/{prompt_id}", response_model=Prompt)
def get_prompt(prompt_id: str):
    try:
        return _store().get_prompt(prompt_id)
    except FileNotFoundError:
        raise HTTPException(404, "Prompt not found")


@app.post("/prompts", response_model=Prompt, status_code=201)
def create_prompt(data: PromptCreate):
    try:
        return _store().create_prompt(data)
    except FileExistsError:
        raise HTTPException(409, "Prompt already exists")


@app.put("/prompts/{prompt_id}", response_model=Prompt)
def update_prompt(prompt_id: str, data: PromptUpdate):
    try:
        return _store().update_prompt(prompt_id, data)
    except FileNotFoundError:
        raise HTTPException(404, "Prompt not found")


@app.delete("/prompts/{prompt_id}", status_code=204)
def delete_prompt(prompt_id: str):
    try:
        _store().delete_prompt(prompt_id)
    except FileNotFoundError:
        raise HTTPException(404, "Prompt not found")


@app.post("/prompts/{prompt_id}/render")
def render(prompt_id: str, req: RenderRequest):
    try:
        prompt = _store().get_prompt(prompt_id)
    except FileNotFoundError:
        raise HTTPException(404, "Prompt not found")
    try:
        result = render_prompt(prompt.content, req.variables)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"rendered": result}


@app.get("/providers")
def get_providers():
    return list_providers(directory=DEFAULT_DIR)


@app.post("/prompts/{prompt_id}/export")
def export(prompt_id: str, fmt: str = "text"):
    try:
        prompt = _store().get_prompt(prompt_id)
    except FileNotFoundError:
        raise HTTPException(404, "Prompt not found")
    result = export_prompt(prompt, fmt, directory=DEFAULT_DIR)
    return {"exported": result, "format": fmt}


# --- Templates ---

@app.get("/templates", response_model=list[PromptListItem])
def list_templates():
    return _template_store().list_templates()


@app.post("/templates/{template_id}/clone", response_model=Prompt, status_code=201)
def clone_template(template_id: str, name: str | None = None):
    ts = _template_store()
    new_name = name or template_id
    try:
        return ts.clone_template(template_id, new_name, _store())
    except FileNotFoundError:
        raise HTTPException(404, "Template not found")
    except FileExistsError:
        raise HTTPException(409, "Prompt already exists with that name")


# --- Hints ---

@app.get("/hints")
def get_hints():
    return load_hints()


# --- Scaffolds ---

@app.get("/scaffold/{provider}")
def get_scaffold(provider: str):
    content = load_scaffold(provider)
    return {"provider": provider, "content": content}
