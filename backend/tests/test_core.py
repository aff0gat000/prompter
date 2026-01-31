import pytest

from prompter.core.models import PromptCreate, PromptUpdate
from prompter.core.renderer import render_prompt
from prompter.core.store import PromptStore
from prompter.tools.exporters import (
    export_prompt,
    get_format_for_provider,
    init_config,
    list_providers,
    load_config,
)


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


# -- Store tests --

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


def test_custom_tool_name(store):
    store.create_prompt(PromptCreate(name="custom", tool="my-local-llm"))
    loaded = store.get_prompt("custom")
    assert loaded.tool == "my-local-llm"


# -- Renderer tests --

def test_render():
    result = render_prompt("Hello {{name}}!", {"name": "World"})
    assert result == "Hello World!"


def test_render_missing_var():
    with pytest.raises(Exception):
        render_prompt("Hello {{name}}!", {})


# -- Exporter tests --

def test_export_by_format_messages(sample_prompt):
    result = export_prompt(sample_prompt, "messages")
    assert '"role": "system"' in result


def test_export_by_format_markdown(sample_prompt):
    result = export_prompt(sample_prompt, "markdown")
    assert "Hello" in result


def test_export_by_format_text(sample_prompt):
    result = export_prompt(sample_prompt, "text")
    assert "Hello" in result


def test_export_by_provider_openai(sample_prompt):
    result = export_prompt(sample_prompt, "openai")
    assert '"role": "system"' in result


def test_export_by_provider_groq(sample_prompt):
    result = export_prompt(sample_prompt, "groq")
    assert '"role": "system"' in result


def test_export_by_provider_ollama(sample_prompt):
    result = export_prompt(sample_prompt, "ollama")
    assert '"role": "system"' in result


def test_export_by_provider_claude(sample_prompt):
    result = export_prompt(sample_prompt, "claude")
    assert "Hello" in result
    assert '"role"' not in result


def test_export_by_provider_gemini(sample_prompt):
    result = export_prompt(sample_prompt, "gemini")
    assert "Hello" in result


def test_export_unknown_defaults_to_messages(sample_prompt):
    result = export_prompt(sample_prompt, "some-future-provider")
    assert '"role": "system"' in result


# -- Provider registry tests --

def test_provider_format_mapping():
    assert get_format_for_provider("openai") == "messages"
    assert get_format_for_provider("groq") == "messages"
    assert get_format_for_provider("ollama") == "messages"
    assert get_format_for_provider("together") == "messages"
    assert get_format_for_provider("mistral") == "messages"
    assert get_format_for_provider("deepseek") == "messages"
    assert get_format_for_provider("claude") == "markdown"
    assert get_format_for_provider("gemini") == "markdown"
    assert get_format_for_provider("generic") == "text"


def test_unknown_provider_defaults_to_messages():
    assert get_format_for_provider("some-new-provider") == "messages"


def test_list_providers():
    providers = list_providers()
    assert len(providers) > 10
    names = [p["provider"] for p in providers]
    assert "openai" in names
    assert "groq" in names
    assert "claude" in names


# -- providers.yaml config tests --

def test_init_config_creates_file(tmp_path):
    path = init_config(tmp_path)
    assert path.exists()
    assert "providers:" in path.read_text()


def test_init_config_idempotent(tmp_path):
    init_config(tmp_path)
    # Write custom content
    config_path = tmp_path / "providers.yaml"
    config_path.write_text("providers:\n  my-llm: markdown\n")
    # init again should NOT overwrite
    init_config(tmp_path)
    assert "my-llm" in config_path.read_text()


def test_load_config_merges_user_providers(tmp_path):
    config_path = tmp_path / "providers.yaml"
    config_path.write_text("providers:\n  my-company-llm: markdown\n  my-local: text\n")
    merged = load_config(tmp_path)
    # User providers are present
    assert merged["my-company-llm"] == "markdown"
    assert merged["my-local"] == "text"
    # Built-ins still present
    assert merged["openai"] == "messages"
    assert merged["claude"] == "markdown"


def test_load_config_user_overrides_builtin(tmp_path):
    config_path = tmp_path / "providers.yaml"
    # Override claude to use messages instead of markdown
    config_path.write_text("providers:\n  claude: messages\n")
    merged = load_config(tmp_path)
    assert merged["claude"] == "messages"


def test_load_config_ignores_invalid_formats(tmp_path):
    config_path = tmp_path / "providers.yaml"
    config_path.write_text("providers:\n  bad-provider: nonexistent_format\n")
    merged = load_config(tmp_path)
    assert "bad-provider" not in merged


def test_load_config_no_file(tmp_path):
    merged = load_config(tmp_path)
    assert merged["openai"] == "messages"


def test_load_config_none_directory():
    merged = load_config(None)
    assert merged["openai"] == "messages"


def test_export_uses_custom_provider(tmp_path, sample_prompt):
    config_path = tmp_path / "providers.yaml"
    config_path.write_text("providers:\n  my-api: markdown\n")
    result = export_prompt(sample_prompt, "my-api", directory=tmp_path)
    assert "Hello" in result
    assert '"role"' not in result


def test_list_providers_includes_custom(tmp_path):
    config_path = tmp_path / "providers.yaml"
    config_path.write_text("providers:\n  acme-llm: messages\n")
    providers = list_providers(directory=tmp_path)
    names = [p["provider"] for p in providers]
    assert "acme-llm" in names
    assert "openai" in names
