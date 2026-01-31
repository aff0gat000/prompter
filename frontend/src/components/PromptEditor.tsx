import React, { useEffect, useState } from 'react'
import { getPrompt, createPrompt, updatePrompt, renderPrompt } from '../api'
import type { Prompt } from '../types'

interface Props {
  promptId: string | null
  onBack: () => void
  onSaved: () => void
}

export default function PromptEditor({ promptId, onBack, onSaved }: Props) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [content, setContent] = useState('')
  const [tags, setTags] = useState('')
  const [tool, setTool] = useState('generic')
  const [variables, setVariables] = useState('')
  const [preview, setPreview] = useState('')
  const [varInputs, setVarInputs] = useState<Record<string, string>>({})
  const isNew = !promptId

  useEffect(() => {
    if (promptId) {
      getPrompt(promptId).then((p) => {
        setName(p.name)
        setDescription(p.description)
        setContent(p.content)
        setTags(p.tags.join(', '))
        setTool(p.tool)
        setVariables(p.variables.join(', '))
        const inputs: Record<string, string> = {}
        p.variables.forEach((v) => (inputs[v] = ''))
        setVarInputs(inputs)
      })
    }
  }, [promptId])

  const handleSave = async () => {
    const tagList = tags.split(',').map((t) => t.trim()).filter(Boolean)
    const varList = variables.split(',').map((v) => v.trim()).filter(Boolean)
    if (isNew) {
      await createPrompt({ name, description, content, tags: tagList, tool, variables: varList })
    } else {
      await updatePrompt(promptId, { name, description, content, tags: tagList, tool, variables: varList })
    }
    onSaved()
    onBack()
  }

  const handleRender = async () => {
    if (!promptId) return
    try {
      const result = await renderPrompt(promptId, varInputs)
      setPreview(result)
    } catch {
      setPreview('Error rendering prompt')
    }
  }

  return (
    <div>
      <button onClick={onBack} className="text-blue-600 text-sm mb-4 hover:underline">
        &larr; Back to list
      </button>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              disabled={!isNew}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <input
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
          </div>
          <div className="flex gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">Tags (comma-separated)</label>
              <input
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              />
            </div>
            <div className="w-48">
              <label className="block text-sm font-medium text-gray-700 mb-1">Provider / Tool</label>
              <input
                value={tool}
                onChange={(e) => setTool(e.target.value)}
                placeholder="openai, claude, groq, ollama..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                list="provider-suggestions"
              />
              <datalist id="provider-suggestions">
                {['generic', 'openai', 'claude', 'groq', 'together', 'mistral',
                  'ollama', 'lmstudio', 'gemini', 'deepseek', 'perplexity',
                  'fireworks', 'openrouter', 'azure', 'cohere', 'vllm', 'litellm',
                ].map((p) => <option key={p} value={p} />)}
              </datalist>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Variables (comma-separated)</label>
            <input
              value={variables}
              onChange={(e) => setVariables(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Content</label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={16}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm font-mono"
            />
          </div>
          <button
            onClick={handleSave}
            className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700"
          >
            {isNew ? 'Create' : 'Save'}
          </button>
        </div>
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-2">Preview / Render</h3>
          {!isNew && Object.keys(varInputs).length > 0 && (
            <div className="space-y-2 mb-4">
              {Object.keys(varInputs).map((v) => (
                <div key={v} className="flex gap-2 items-center">
                  <label className="text-sm text-gray-600 w-32">{v}:</label>
                  <input
                    value={varInputs[v]}
                    onChange={(e) => setVarInputs({ ...varInputs, [v]: e.target.value })}
                    className="flex-1 px-3 py-1 border border-gray-300 rounded-md text-sm"
                  />
                </div>
              ))}
              <button
                onClick={handleRender}
                className="px-3 py-1 bg-green-600 text-white rounded-md text-sm hover:bg-green-700"
              >
                Render
              </button>
            </div>
          )}
          <div className="bg-white border border-gray-200 rounded-lg p-4 min-h-[200px]">
            <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono">
              {preview || content || 'Content preview will appear here...'}
            </pre>
          </div>
        </div>
      </div>
    </div>
  )
}
