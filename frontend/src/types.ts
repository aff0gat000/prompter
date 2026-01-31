export interface PromptListItem {
  id: string
  name: string
  description: string
  tags: string[]
  tool: string
  category: string
  updated_at: string
}

export interface Prompt {
  id: string
  name: string
  description: string
  content: string
  tags: string[]
  tool: string
  variables: string[]
  category: string
  created_at: string
  updated_at: string
}

export interface PromptCreate {
  name: string
  description: string
  content: string
  tags: string[]
  tool: string
  variables: string[]
  category: string
}

export interface Hint {
  id: string
  label: string
  description: string
  pattern: string
}

export interface Scaffold {
  provider: string
  content: string
}
