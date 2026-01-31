# Prompter

CLI + web UI for designing, managing, and organizing prompts for AI tools.

Prompts are stored as markdown files with YAML frontmatter, making them easy to version control, share, and integrate into any workflow. Works with any LLM provider out of the box.

## Supported Providers

Prompter uses a **provider registry** that maps provider names to export formats. Most LLM providers use the OpenAI chat completions format (`messages` JSON array), so any unknown provider defaults to it automatically.

| Provider | Export Format | Notes |
|----------|-------------|-------|
| openai, chatgpt, gpt | messages | OpenAI Chat Completions API |
| groq | messages | Groq Cloud |
| together | messages | Together AI |
| mistral | messages | Mistral / La Plateforme |
| ollama | messages | Local models via Ollama |
| lmstudio | messages | Local models via LM Studio |
| vllm | messages | vLLM serving |
| deepseek | messages | DeepSeek API |
| perplexity | messages | Perplexity API |
| fireworks | messages | Fireworks AI |
| openrouter | messages | OpenRouter (multi-provider) |
| azure | messages | Azure OpenAI Service |
| cohere | messages | Cohere API |
| litellm | messages | LiteLLM proxy |
| claude, anthropic | markdown | Anthropic Claude API |
| gemini, google | markdown | Google Gemini API |
| generic | text | Plain text |
| *(any other string)* | messages | Defaults to OpenAI-compatible |

The `tool` field in your prompt files is a **free-form string** — use any provider name you want. If it's not in the built-in registry, it exports as `messages` format since that's what most APIs expect.

```bash
prompter providers   # list all known providers
```

## Quick Start

```bash
cd backend
pip install -e .
prompter init
prompter list
```

## Prompt File Format

Prompts live in the `prompts/` directory as `.md` files with YAML frontmatter:

```markdown
---
name: chatgpt-assistant
description: Custom ChatGPT assistant with persona and constraints
tags: [assistant, openai, chatgpt]
tool: openai
variables: [persona, topic, tone]
---

You are {{persona}}, an expert in {{topic}}.

Communicate in a {{tone}} tone. Follow these rules:
1. Always cite sources when making factual claims.
2. If you don't know something, say so rather than guessing.
...
```

The `tool` field can be any string — `openai`, `groq`, `ollama`, `my-custom-server`, etc.

## CLI Usage

### List prompts

```bash
prompter list
```

### Show a prompt

```bash
prompter show chatgpt-assistant
```

### Create a prompt

```bash
prompter create my-prompt \
  --desc "My custom prompt" \
  --tags "openai,chat" \
  --tool groq \
  --content "You are a helpful assistant."
```

Or pipe from stdin:

```bash
cat system-prompt.txt | prompter create my-prompt --tool ollama
```

### Render with variables

```bash
prompter render chatgpt-assistant \
  --var persona="a senior data scientist" \
  --var topic="machine learning" \
  --var tone="friendly"
```

### Export

Export using a **format name** or a **provider name**:

```bash
# By format
prompter export my-prompt --format messages   # OpenAI-compatible JSON
prompter export my-prompt --format markdown   # raw markdown
prompter export my-prompt --format text       # plain text

# By provider (auto-resolves to the right format)
prompter export my-prompt --format openai     # → messages JSON
prompter export my-prompt --format groq       # → messages JSON
prompter export my-prompt --format ollama     # → messages JSON
prompter export my-prompt --format claude     # → markdown
prompter export my-prompt --format gemini     # → markdown
```

### List providers

```bash
prompter providers
```

## Examples

### OpenAI / ChatGPT

```bash
# Create a prompt
prompter create customer-support \
  --desc "Customer support system prompt" \
  --tags "openai,support" \
  --tool openai \
  --content "You are a support agent for {{company}}. Help users with {{product}}."

# Render and export for the OpenAI API
prompter render customer-support --var company="Acme" --var product="Cloud"
prompter export customer-support --format openai
```

Output:

```json
[
  {
    "role": "system",
    "content": "You are a support agent for Acme. Help users with Cloud."
  }
]
```

Use with the OpenAI Python SDK:

```python
from openai import OpenAI
import json, subprocess

client = OpenAI()

result = subprocess.run(
    ["prompter", "export", "customer-support", "--format", "openai"],
    capture_output=True, text=True,
)
messages = json.loads(result.stdout)
messages.append({"role": "user", "content": "How do I reset my password?"})

response = client.chat.completions.create(model="gpt-4o", messages=messages)
print(response.choices[0].message.content)
```

### Groq

Same `messages` format, different client:

```python
from groq import Groq
import json, subprocess

client = Groq()

result = subprocess.run(
    ["prompter", "export", "customer-support", "--format", "groq"],
    capture_output=True, text=True,
)
messages = json.loads(result.stdout)
messages.append({"role": "user", "content": "What's your refund policy?"})

response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=messages)
print(response.choices[0].message.content)
```

### Ollama (local models)

```python
import requests, json, subprocess

result = subprocess.run(
    ["prompter", "export", "customer-support", "--format", "ollama"],
    capture_output=True, text=True,
)
messages = json.loads(result.stdout)
messages.append({"role": "user", "content": "Help me with billing."})

response = requests.post("http://localhost:11434/api/chat", json={
    "model": "llama3.2",
    "messages": messages,
})
print(response.json()["message"]["content"])
```

### Together AI

```python
from together import Together
import json, subprocess

client = Together()

result = subprocess.run(
    ["prompter", "export", "customer-support", "--format", "together"],
    capture_output=True, text=True,
)
messages = json.loads(result.stdout)
messages.append({"role": "user", "content": "What features do you offer?"})

response = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
    messages=messages,
)
print(response.choices[0].message.content)
```

### Mistral

```python
from mistralai import Mistral
import json, subprocess

client = Mistral(api_key="your-key")

result = subprocess.run(
    ["prompter", "export", "customer-support", "--format", "mistral"],
    capture_output=True, text=True,
)
messages = json.loads(result.stdout)
messages.append({"role": "user", "content": "Tell me about pricing."})

response = client.chat.complete(model="mistral-large-latest", messages=messages)
print(response.choices[0].message.content)
```

### Claude / Anthropic

Claude uses the system prompt as a separate parameter (markdown format):

```python
import anthropic, subprocess

client = anthropic.Anthropic()

result = subprocess.run(
    ["prompter", "export", "customer-support", "--format", "claude"],
    capture_output=True, text=True,
)

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system=result.stdout,
    messages=[{"role": "user", "content": "How do I upgrade my plan?"}],
)
print(message.content[0].text)
```

### Gemini / Google

```python
from google import genai

client = genai.Client()

result = subprocess.run(
    ["prompter", "export", "customer-support", "--format", "gemini"],
    capture_output=True, text=True,
)

response = client.models.generate_content(
    model="gemini-2.0-flash",
    config={"system_instruction": result.stdout},
    contents="How do I contact support?",
)
print(response.text)
```

### DeepSeek

```python
from openai import OpenAI
import json, subprocess

client = OpenAI(api_key="your-key", base_url="https://api.deepseek.com")

result = subprocess.run(
    ["prompter", "export", "customer-support", "--format", "deepseek"],
    capture_output=True, text=True,
)
messages = json.loads(result.stdout)
messages.append({"role": "user", "content": "Help me debug this code."})

response = client.chat.completions.create(model="deepseek-chat", messages=messages)
print(response.choices[0].message.content)
```

### Any OpenAI-Compatible Provider

Since unknown providers default to `messages` format, this works with any provider that speaks the OpenAI protocol:

```bash
# Works even though "my-local-server" isn't in the registry
prompter create my-prompt --tool my-local-server --content "You are helpful."
prompter export my-prompt --format messages
```

```python
from openai import OpenAI
import json, subprocess

# Point to any OpenAI-compatible endpoint
client = OpenAI(base_url="http://localhost:8080/v1", api_key="none")

result = subprocess.run(
    ["prompter", "export", "my-prompt", "--format", "messages"],
    capture_output=True, text=True,
)
messages = json.loads(result.stdout)
messages.append({"role": "user", "content": "Hello!"})

response = client.chat.completions.create(model="local-model", messages=messages)
print(response.choices[0].message.content)
```

## Web UI

```bash
# Terminal 1 - API server
cd backend && prompter serve

# Terminal 2 - Frontend
cd frontend && npm install && npm run dev
```

Open http://localhost:5173. The provider/tool field is a free-form input with autocomplete suggestions for all known providers.

## REST API

Runs on `http://localhost:8000`:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/prompts` | List all prompts |
| GET | `/prompts/{id}` | Get a prompt |
| POST | `/prompts` | Create a prompt |
| PUT | `/prompts/{id}` | Update a prompt |
| DELETE | `/prompts/{id}` | Delete a prompt |
| POST | `/prompts/{id}/render` | Render with variables |
| POST | `/prompts/{id}/export?fmt=openai` | Export for a provider |
| GET | `/providers` | List all known providers |

## Configuration

```bash
export PROMPTER_DIR=~/my-prompts
prompter init
```

## Running Tests

```bash
cd backend
pip install pytest
python -m pytest tests/ -v
```
