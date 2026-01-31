from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from pathlib import Path

import json
import shutil

import frontmatter

from .models import Prompt, PromptCreate, PromptListItem, PromptUpdate

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
DATA_DIR = Path(__file__).parent.parent / "data"


def _sanitize_filename(name: str) -> str:
    safe = re.sub(r"[^\w\-]", "-", name.strip().lower())
    safe = re.sub(r"-+", "-", safe).strip("-")
    if not safe:
        raise ValueError("Invalid prompt name")
    return safe


class PromptStore:
    def __init__(self, directory: str | Path) -> None:
        self.directory = Path(directory).resolve()

    def init(self) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)

    def _path(self, id_: str) -> Path:
        safe = _sanitize_filename(id_)
        path = (self.directory / f"{safe}.md").resolve()
        if not str(path).startswith(str(self.directory)):
            raise ValueError("Invalid prompt id")
        return path

    def _load(self, path: Path) -> Prompt:
        post = frontmatter.load(str(path))
        meta = dict(post.metadata)
        stem = path.stem
        stat = path.stat()
        return Prompt(
            id=stem,
            name=meta.get("name", stem),
            description=meta.get("description", ""),
            content=post.content,
            tags=meta.get("tags", []),
            tool=meta.get("tool", "generic"),
            variables=meta.get("variables", []),
            category=meta.get("category", ""),
            created_at=meta.get("created_at", datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc)),
            updated_at=meta.get("updated_at", datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)),
        )

    def _save(self, prompt: Prompt) -> Path:
        path = self._path(prompt.id)
        meta = dict(
            name=prompt.name,
            description=prompt.description,
            tags=prompt.tags,
            tool=prompt.tool,
            variables=prompt.variables,
            created_at=prompt.created_at.isoformat(),
            updated_at=prompt.updated_at.isoformat(),
        )
        if prompt.category:
            meta["category"] = prompt.category
        post = frontmatter.Post(prompt.content, **meta)
        path.write_text(frontmatter.dumps(post) + "\n")
        return path

    def list_prompts(self) -> list[PromptListItem]:
        if not self.directory.exists():
            return []
        items = []
        for f in sorted(self.directory.glob("*.md")):
            p = self._load(f)
            items.append(PromptListItem(
                id=p.id, name=p.name, description=p.description,
                tags=p.tags, tool=p.tool, category=p.category,
                updated_at=p.updated_at,
            ))
        return items

    def get_prompt(self, id_: str) -> Prompt:
        path = self._path(id_)
        if not path.exists():
            raise FileNotFoundError(f"Prompt not found: {id_}")
        return self._load(path)

    def create_prompt(self, data: PromptCreate) -> Prompt:
        now = datetime.now(timezone.utc)
        prompt = Prompt(
            id=_sanitize_filename(data.name),
            name=data.name,
            description=data.description,
            content=data.content,
            tags=data.tags,
            tool=data.tool,
            variables=data.variables,
            category=data.category,
            created_at=now,
            updated_at=now,
        )
        path = self._path(prompt.id)
        if path.exists():
            raise FileExistsError(f"Prompt already exists: {prompt.id}")
        self._save(prompt)
        return prompt

    def update_prompt(self, id_: str, data: PromptUpdate) -> Prompt:
        prompt = self.get_prompt(id_)
        updates = data.model_dump(exclude_none=True)
        for k, v in updates.items():
            setattr(prompt, k, v)
        prompt.updated_at = datetime.now(timezone.utc)
        if "name" in updates:
            new_id = _sanitize_filename(updates["name"])
            if new_id != id_:
                old_path = self._path(id_)
                prompt.id = new_id
                self._save(prompt)
                old_path.unlink()
                return prompt
        self._save(prompt)
        return prompt

    def delete_prompt(self, id_: str) -> None:
        path = self._path(id_)
        if not path.exists():
            raise FileNotFoundError(f"Prompt not found: {id_}")
        path.unlink()


class TemplateStore:
    def __init__(self, directory: Path = TEMPLATES_DIR) -> None:
        self.directory = directory
        self._loader = PromptStore(directory)

    def list_templates(self) -> list[PromptListItem]:
        if not self.directory.exists():
            return []
        items = []
        for f in sorted(self.directory.glob("*.md")):
            p = self._loader._load(f)
            items.append(PromptListItem(
                id=p.id, name=p.name, description=p.description,
                tags=p.tags, tool=p.tool, category=p.category,
                updated_at=p.updated_at,
            ))
        return items

    def get_template(self, id_: str) -> Prompt:
        path = self._loader._path(id_)
        if not path.exists():
            raise FileNotFoundError(f"Template not found: {id_}")
        return self._loader._load(path)

    def clone_template(self, template_id: str, new_name: str, target_store: PromptStore) -> Prompt:
        template = self.get_template(template_id)
        data = PromptCreate(
            name=new_name,
            description=template.description,
            content=template.content,
            tags=template.tags,
            tool=template.tool,
            variables=template.variables,
            category=template.category,
        )
        target_store.init()
        return target_store.create_prompt(data)


def load_hints() -> list[dict]:
    path = DATA_DIR / "hints.json"
    if not path.exists():
        return []
    return json.loads(path.read_text())


def load_scaffold(provider: str) -> str:
    path = DATA_DIR / "scaffolds.json"
    if not path.exists():
        return ""
    scaffolds = json.loads(path.read_text())
    return scaffolds.get(provider, scaffolds.get("generic", ""))
