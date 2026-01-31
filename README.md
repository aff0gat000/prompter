# Prompter

CLI + web UI for designing, managing, and organizing prompts for AI tools (Claude, ChatGPT/OpenAI, Gemini, and others).

Prompts are stored as markdown files with YAML frontmatter, making them easy to version control, share, and integrate into any workflow.

## Quick Start

```bash
# Install
cd backend
pip install -e .

# Initialize and list prompts
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

Supported `tool` values: `claude`, `openai`, `gemini`, `generic`.

## CLI Usage

### List all prompts

```bash
prompter list
```

```
┏━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Name                   ┃ Description                               ┃ Tags              ┃ Tool   ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ code-review            │ System prompt for code review              │ review, coding    │ claude │
│ chatgpt-assistant      │ Custom ChatGPT assistant with persona ...  │ assistant, openai │ openai │
│ openai-function-caller │ System prompt for structured function ...  │ openai, function  │ openai │
└────────────────────────┴───────────────────────────────────────────┴───────────────────┴────────┘
```

### Show a prompt

```bash
prompter show chatgpt-assistant
```

### Create a prompt

```bash
prompter create my-prompt --desc "My custom prompt" --tags "openai,chat" --tool openai --content "You are a helpful assistant."
```

Or pipe content from a file:

```bash
cat system-prompt.txt | prompter create my-prompt --desc "Imported prompt" --tool openai
```

### Render with variables

Replace `{{variable}}` placeholders with actual values:

```bash
prompter render chatgpt-assistant \
  --var persona="a senior data scientist" \
  --var topic="machine learning" \
  --var tone="friendly and encouraging"
```

Output:

```
You are a senior data scientist, an expert in machine learning.

Communicate in a friendly and encouraging tone. Follow these rules:
1. Always cite sources when making factual claims.
2. If you don't know something, say so rather than guessing.
3. Break complex topics into digestible steps.
4. Use examples to illustrate abstract concepts.
5. Ask clarifying questions when the user's request is ambiguous.
```

### Export for OpenAI / ChatGPT

Export a prompt in OpenAI's chat messages JSON format:

```bash
prompter export chatgpt-assistant --format openai \
  # after rendering, you get:
```

```json
[
  {
    "role": "system",
    "content": "You are a senior data scientist, an expert in machine learning.\n\nCommunicate in a friendly and encouraging tone...."
  }
]
```

This output plugs directly into the OpenAI API:

```python
from openai import OpenAI
import json

# Export your prompt
# $ prompter render chatgpt-assistant --var persona="..." | prompter export chatgpt-assistant --format openai > messages.json

client = OpenAI()

# Load the exported system message
with open("messages.json") as f:
    messages = json.load(f)

# Add a user message and call the API
messages.append({"role": "user", "content": "Explain gradient descent simply."})

response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
)
print(response.choices[0].message.content)
```

### Export for Claude

```bash
prompter export code-review --format claude
```

Returns the raw markdown content, ready to use as a system prompt with the Anthropic API:

```python
import anthropic

# $ prompter render code-review --var language=python --var style_guide=PEP8 > system.md

client = anthropic.Anthropic()

with open("system.md") as f:
    system_prompt = f.read()

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system=system_prompt,
    messages=[{"role": "user", "content": "Review this function:\n\ndef add(a, b): return a+b"}],
)
print(message.content[0].text)
```

### Export as plain text

```bash
prompter export my-prompt --format text
```

### Edit in your editor

```bash
prompter edit chatgpt-assistant   # opens in $EDITOR
```

## Web UI

Start the backend API server and frontend dev server:

```bash
# Terminal 1 - API server
cd backend
prompter serve

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 to access the web UI. Features:

- Browse and search prompts by name, tag, or tool
- Create and edit prompts with a markdown editor
- Live preview with variable rendering
- Filter by tool (Claude, OpenAI, Gemini, etc.)

## API

The REST API runs on `http://localhost:8000`:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/prompts` | List all prompts |
| GET | `/prompts/{id}` | Get a prompt |
| POST | `/prompts` | Create a prompt |
| PUT | `/prompts/{id}` | Update a prompt |
| DELETE | `/prompts/{id}` | Delete a prompt |
| POST | `/prompts/{id}/render` | Render with variables |
| POST | `/prompts/{id}/export?fmt=openai` | Export in a format |

### Example: Create and render via API

```bash
# Create a prompt
curl -X POST http://localhost:8000/prompts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "email-writer",
    "description": "Write emails in a specific style",
    "content": "Write a {{tone}} email about {{subject}}.",
    "tags": ["email", "writing"],
    "tool": "openai",
    "variables": ["tone", "subject"]
  }'

# Render it
curl -X POST http://localhost:8000/prompts/email-writer/render \
  -H "Content-Type: application/json" \
  -d '{"variables": {"tone": "professional", "subject": "project update"}}'
```

## OpenAI / ChatGPT Examples

### Custom GPT System Prompt

Create a prompt for a Custom GPT:

```bash
prompter create customer-support-gpt \
  --desc "System prompt for a customer support Custom GPT" \
  --tags "openai,chatgpt,custom-gpt,support" \
  --tool openai \
  --content "You are a customer support agent for {{company}}.

Your responsibilities:
- Answer questions about {{product}} features and pricing
- Help troubleshoot common issues
- Escalate complex problems by providing a support ticket link
- Never make promises about unreleased features
- Always be polite and empathetic

Knowledge cutoff: You only know about features released as of {{knowledge_date}}."
```

Render and export for the OpenAI API:

```bash
prompter render customer-support-gpt \
  --var company="Acme Inc" \
  --var product="Acme Cloud" \
  --var knowledge_date="2025-01-01"

prompter export customer-support-gpt --format openai
```

### Structured Output Prompt

```bash
prompter create json-extractor \
  --desc "Extract structured JSON from unstructured text" \
  --tags "openai,structured-output,json" \
  --tool openai \
  --content "Extract {{entity_type}} entities from the user's text.

Return a JSON object matching this schema:
{
  \"entities\": [
    {
      \"name\": \"string\",
      \"type\": \"{{entity_type}}\",
      \"confidence\": 0.0-1.0
    }
  ]
}

Only return valid JSON. Do not include any explanation outside the JSON block."
```

```bash
prompter render json-extractor --var entity_type="person"
prompter export json-extractor --format openai
```

### Multi-turn Conversation Seed

For prompts that seed a multi-turn conversation, create the system prompt with Prompter and combine it with your conversation logic:

```python
from openai import OpenAI
import subprocess, json

client = OpenAI()

# Use Prompter CLI to render the system prompt
result = subprocess.run(
    ["prompter", "export", "chatgpt-assistant", "--format", "openai"],
    capture_output=True, text=True, env={**__import__("os").environ, "PROMPTER_DIR": "./prompts"}
)
messages = json.loads(result.stdout)

# Multi-turn conversation loop
while True:
    user_input = input("You: ")
    if user_input.lower() in ("quit", "exit"):
        break
    messages.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(model="gpt-4o", messages=messages)
    reply = response.choices[0].message.content
    print(f"Assistant: {reply}")
    messages.append({"role": "assistant", "content": reply})
```

## Project Structure

```
prompter/
├── backend/
│   ├── pyproject.toml
│   ├── prompter/
│   │   ├── cli.py            # Typer CLI
│   │   ├── api.py            # FastAPI REST API
│   │   ├── core/
│   │   │   ├── models.py     # Pydantic models
│   │   │   ├── store.py      # Filesystem prompt storage
│   │   │   └── renderer.py   # Jinja2 sandboxed variable substitution
│   │   └── tools/
│   │       └── exporters.py  # Export to Claude/OpenAI/text formats
│   └── tests/
│       └── test_core.py
├── frontend/
│   ├── package.json
│   └── src/                  # React + TypeScript + Tailwind
├── prompts/                  # Default prompt storage
│   ├── example.md
│   ├── chatgpt-assistant.md
│   └── openai-function-caller.md
└── README.md
```

## Configuration

Set `PROMPTER_DIR` to change where prompts are stored:

```bash
export PROMPTER_DIR=~/my-prompts
prompter init
prompter list
```

## Running Tests

```bash
cd backend
pip install pytest
python -m pytest tests/ -v
```
