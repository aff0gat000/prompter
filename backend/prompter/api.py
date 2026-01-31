from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .core.models import Prompt, PromptCreate, PromptListItem, PromptUpdate, RenderRequest
from .core.renderer import render_prompt
from .core.store import PromptStore
from .tools.exporters import export_prompt

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


@app.get("/prompts", response_model=list[PromptListItem])
def list_prompts():
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


@app.post("/prompts/{prompt_id}/export")
def export(prompt_id: str, fmt: str = "text"):
    try:
        prompt = _store().get_prompt(prompt_id)
    except FileNotFoundError:
        raise HTTPException(404, "Prompt not found")
    try:
        result = export_prompt(prompt, fmt)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"exported": result, "format": fmt}
