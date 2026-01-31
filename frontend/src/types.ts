export interface PromptListItem {
  id: string
  name: string
  description: string
  tags: string[]
  tool: string
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
}
