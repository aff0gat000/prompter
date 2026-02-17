interface Props {
  onBack: () => void
}

export default function UsageGuide({ onBack }: Props) {
  return (
    <div>
      <button onClick={onBack} className="text-blue-600 text-sm mb-4 hover:underline">
        &larr; Back to list
      </button>

      <h2 className="text-lg font-semibold text-gray-900 mb-2">Usage Guide</h2>
      <p className="text-sm text-gray-600 mb-6">
        Learn how to create, optimize, and export prompts for any AI provider.
      </p>

      {/* Workflow */}
      <section className="mb-8">
        <h3 className="text-md font-semibold text-gray-800 mb-3">How It Works</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            {
              step: '1',
              title: 'Pick a starting point',
              desc: 'Browse starter templates or create a prompt from scratch. Templates cover common use cases like code review, writing, and data extraction.',
            },
            {
              step: '2',
              title: 'Customize your prompt',
              desc: 'Write your prompt content, add variables with {{name}} syntax, and check the Best Practices panel to make sure you cover all the essentials.',
            },
            {
              step: '3',
              title: 'Export & integrate',
              desc: 'Set your provider (Claude, ChatGPT, Gemini, Copilot, etc.) and export. Use the output in your code, API calls, or tool settings.',
            },
          ].map((item) => (
            <div key={item.step} className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="text-blue-600 font-bold text-lg mb-1">Step {item.step}</div>
              <h4 className="font-medium text-gray-900 mb-1">{item.title}</h4>
              <p className="text-sm text-gray-500">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Best Practices */}
      <section className="mb-8">
        <h3 className="text-md font-semibold text-gray-800 mb-3">Best Practices</h3>
        <p className="text-sm text-gray-600 mb-3">
          The editor checks your prompt against these 8 patterns. Aim to include as many as
          relevant for your use case:
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {[
            { label: 'Role', example: '"You are a senior backend engineer..."' },
            { label: 'Task', example: '"Review this code for..." or "Generate a REST endpoint..."' },
            { label: 'Output format', example: '"Respond in markdown with code blocks"' },
            { label: 'Examples', example: 'Input/output pairs for the model to follow' },
            { label: 'Boundaries', example: '"Do not suggest frontend changes"' },
            { label: 'Step-by-step reasoning', example: '"Think step by step before answering"' },
            { label: 'Context', example: '"Given a Python FastAPI project with PostgreSQL..."' },
            { label: 'Tone & style', example: '"Be concise and technical"' },
          ].map((h) => (
            <div key={h.label} className="flex gap-2 text-sm">
              <span className="text-green-600 font-medium whitespace-nowrap">{h.label}:</span>
              <span className="text-gray-500">{h.example}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Provider Examples */}
      <section className="mb-8">
        <h3 className="text-md font-semibold text-gray-800 mb-3">Provider Examples</h3>
        <p className="text-sm text-gray-600 mb-4">
          Set the <strong>Provider / Tool</strong> field in the editor to match your target.
          Each provider exports in the format its API expects.
        </p>

        <div className="space-y-4">
          <ProviderExample
            name="Claude / Anthropic"
            provider="claude"
            format="Markdown"
            description="Claude uses the system prompt as a separate parameter. Export gives you raw markdown."
            code={`import anthropic, subprocess

client = anthropic.Anthropic()

result = subprocess.run(
    ["prompter", "export", "my-prompt", "--format", "claude"],
    capture_output=True, text=True,
)

message = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    system=result.stdout,
    messages=[{"role": "user", "content": "Your question here"}],
)
print(message.content[0].text)`}
          />

          <ProviderExample
            name="ChatGPT / OpenAI"
            provider="openai"
            format="Messages JSON"
            description='Export produces a JSON array with a system message: [{"role": "system", "content": "..."}].'
            code={`from openai import OpenAI
import json, subprocess

client = OpenAI()

result = subprocess.run(
    ["prompter", "export", "my-prompt", "--format", "openai"],
    capture_output=True, text=True,
)
messages = json.loads(result.stdout)
messages.append({"role": "user", "content": "Your question here"})

response = client.chat.completions.create(model="gpt-4o", messages=messages)
print(response.choices[0].message.content)`}
          />

          <ProviderExample
            name="Gemini / Google"
            provider="gemini"
            format="Markdown"
            description="Gemini accepts the system instruction as plain text. Export gives you raw markdown."
            code={`from google import genai
import subprocess

client = genai.Client()

result = subprocess.run(
    ["prompter", "export", "my-prompt", "--format", "gemini"],
    capture_output=True, text=True,
)

response = client.models.generate_content(
    model="gemini-2.0-flash",
    config={"system_instruction": result.stdout},
    contents="Your question here",
)
print(response.text)`}
          />

          <ProviderExample
            name="GitHub Copilot"
            provider="copilot"
            format="Markdown"
            description="Export your prompt and save it as .github/copilot-instructions.md in your repository. Copilot Chat will follow it automatically."
            code={`# Export and save to your repo
prompter export my-prompt --format copilot > .github/copilot-instructions.md

# Or paste the output into VS Code:
# Copilot Chat > Settings > Custom Instructions`}
          />
        </div>
      </section>

      {/* Variables */}
      <section className="mb-8">
        <h3 className="text-md font-semibold text-gray-800 mb-3">Using Variables</h3>
        <p className="text-sm text-gray-600 mb-3">
          Variables make your prompts reusable across projects. Use <code className="bg-gray-100 px-1 rounded text-xs">{'{{name}}'}</code> syntax
          in your prompt content, then fill them in when rendering.
        </p>
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-sm font-mono">
          <p className="text-gray-500 mb-2"># In your prompt content:</p>
          <p>You are a senior <span className="text-blue-600">{'{{language}}'}</span> developer using <span className="text-blue-600">{'{{framework}}'}</span>.</p>
          <p className="text-gray-500 mt-3 mb-2"># Render with values:</p>
          <p>prompter render my-prompt --var language="Python" --var framework="FastAPI"</p>
        </div>
      </section>

      {/* CLI Quick Reference */}
      <section className="mb-8">
        <h3 className="text-md font-semibold text-gray-800 mb-3">CLI Quick Reference</h3>
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left px-4 py-2 font-medium text-gray-700">Command</th>
                <th className="text-left px-4 py-2 font-medium text-gray-700">Description</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {[
                ['prompter init', 'Initialize prompts directory'],
                ['prompter list', 'List all saved prompts'],
                ['prompter templates', 'List starter templates'],
                ['prompter clone <template>', 'Clone a template to your prompts'],
                ['prompter create <name> --tool <provider>', 'Create a new prompt'],
                ['prompter render <name> --var key=value', 'Render with variables'],
                ['prompter export <name> --format <provider>', 'Export for a provider'],
                ['prompter providers', 'List all known providers'],
                ['prompter serve', 'Start the API server'],
              ].map(([cmd, desc]) => (
                <tr key={cmd}>
                  <td className="px-4 py-2 font-mono text-xs text-gray-800">{cmd}</td>
                  <td className="px-4 py-2 text-gray-500">{desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}

function ProviderExample({
  name,
  provider,
  format,
  description,
  code,
}: {
  name: string
  provider: string
  format: string
  description: string
  code: string
}) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-1">
        <h4 className="font-medium text-gray-900">{name}</h4>
        <span className="px-2 py-0.5 bg-blue-50 text-blue-600 text-xs rounded">{provider}</span>
        <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded">{format}</span>
      </div>
      <p className="text-sm text-gray-500 mb-3">{description}</p>
      <pre className="bg-gray-50 border border-gray-200 rounded p-3 text-xs font-mono text-gray-800 overflow-x-auto whitespace-pre">
        {code}
      </pre>
    </div>
  )
}
