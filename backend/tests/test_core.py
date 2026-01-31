import tempfile
from pathlib import Path

import pytest

from prompter.core.models import PromptCreate, PromptUpdate
from prompter.core.renderer import render_prompt
from prompter.core.store import PromptStore
from prompter.tools.exporters import export_prompt


@pytest.fixture
def store(tmp_path):
    s = PromptStore(tmp_path / "prompts")
    s.init()
    return s


@pytest.fixture
def sample_prompt(store):
    return store.create_prompt(PromptCreate(
        name="test-prompt",
        description="A test prompt",
        content="Hello {{name}}, welcome to {{place}}.",
        tags=["test"],
        tool="generic",
        variables=["name", "place"],
    ))


def test_create_and_get(store, sample_prompt):
    p = store.get_prompt("test-prompt")
    assert p.name == "test-prompt"
    assert p.description == "A test prompt"
    assert "Hello" in p.content


def test_list(store, sample_prompt):
    items = store.list_prompts()
    assert len(items) == 1
    assert items[0].name == "test-prompt"


def test_update(store, sample_prompt):
    updated = store.update_prompt("test-prompt", PromptUpdate(description="Updated"))
    assert updated.description == "Updated"
    assert store.get_prompt("test-prompt").description == "Updated"


def test_delete(store, sample_prompt):
    store.delete_prompt("test-prompt")
    assert store.list_prompts() == []


def test_delete_not_found(store):
    with pytest.raises(FileNotFoundError):
        store.delete_prompt("nonexistent")


def test_duplicate_create(store, sample_prompt):
    with pytest.raises(FileExistsError):
        store.create_prompt(PromptCreate(name="test-prompt"))


def test_render():
    result = render_prompt("Hello {{name}}!", {"name": "World"})
    assert result == "Hello World!"


def test_render_missing_var():
    with pytest.raises(Exception):
        render_prompt("Hello {{name}}!", {})


def test_export_openai(sample_prompt):
    result = export_prompt(sample_prompt, "openai")
    assert '"role": "system"' in result


def test_export_text(sample_prompt):
    result = export_prompt(sample_prompt, "text")
    assert "Hello" in result


def test_export_unknown(sample_prompt):
    with pytest.raises(ValueError):
        export_prompt(sample_prompt, "unknown")
