import type { Prompt, PromptCreate, PromptListItem } from './types'

const BASE = '/prompts'

export async function listPrompts(): Promise<PromptListItem[]> {
  const res = await fetch(BASE)
  if (!res.ok) throw new Error('Failed to list prompts')
  return res.json()
}

export async function getPrompt(id: string): Promise<Prompt> {
  const res = await fetch(`${BASE}/${id}`)
  if (!res.ok) throw new Error('Failed to get prompt')
  return res.json()
}

export async function createPrompt(data: PromptCreate): Promise<Prompt> {
  const res = await fetch(BASE, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error('Failed to create prompt')
  return res.json()
}

export async function updatePrompt(id: string, data: Partial<PromptCreate>): Promise<Prompt> {
  const res = await fetch(`${BASE}/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error('Failed to update prompt')
  return res.json()
}

export async function deletePrompt(id: string): Promise<void> {
  const res = await fetch(`${BASE}/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Failed to delete prompt')
}

export async function renderPrompt(id: string, variables: Record<string, string>): Promise<string> {
  const res = await fetch(`${BASE}/${id}/render`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ variables }),
  })
  if (!res.ok) throw new Error('Failed to render prompt')
  const data = await res.json()
  return data.rendered
}
