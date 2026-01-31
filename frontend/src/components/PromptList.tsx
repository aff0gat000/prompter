import React, { useEffect, useState } from 'react'
import { listPrompts, deletePrompt } from '../api'
import type { PromptListItem } from '../types'

interface Props {
  onSelect: (id: string) => void
  onCreate: () => void
  onBrowseTemplates: () => void
  refreshKey: number
}

export default function PromptList({ onSelect, onCreate, onBrowseTemplates, refreshKey }: Props) {
  const [prompts, setPrompts] = useState<PromptListItem[]>([])
  const [search, setSearch] = useState('')
  const [tagFilter, setTagFilter] = useState('')

  useEffect(() => {
    listPrompts().then(setPrompts).catch(() => {})
  }, [refreshKey])

  const filtered = prompts.filter((p) => {
    const matchesSearch =
      !search ||
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.description.toLowerCase().includes(search.toLowerCase())
    const matchesTag = !tagFilter || p.tags.some((t) => t.toLowerCase().includes(tagFilter.toLowerCase()))
    return matchesSearch && matchesTag
  })

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation()
    if (!confirm(`Delete prompt "${id}"?`)) return
    await deletePrompt(id)
    setPrompts((prev) => prev.filter((p) => p.id !== id))
  }

  return (
    <div>
      <div className="flex flex-col sm:flex-row gap-2 mb-4">
        <input
          type="text"
          placeholder="Search prompts..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
        />
        <input
          type="text"
          placeholder="Filter by tag..."
          value={tagFilter}
          onChange={(e) => setTagFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md text-sm w-full sm:w-48"
        />
        <button
          onClick={onBrowseTemplates}
          className="px-4 py-2 bg-gray-100 text-gray-700 border border-gray-300 rounded-md text-sm hover:bg-gray-200"
        >
          Browse Templates
        </button>
        <button
          onClick={onCreate}
          className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700"
        >
          New Prompt
        </button>
      </div>
      <div className="space-y-2">
        {filtered.map((p) => (
          <div
            key={p.id}
            onClick={() => onSelect(p.id)}
            className="bg-white border border-gray-200 rounded-lg p-4 cursor-pointer hover:border-blue-300 transition-colors"
          >
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-medium text-gray-900">{p.name}</h3>
                {p.description && <p className="text-sm text-gray-500 mt-1">{p.description}</p>}
                <div className="flex gap-1 mt-2 flex-wrap">
                  {p.tags.map((t) => (
                    <span key={t} className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded">
                      {t}
                    </span>
                  ))}
                  <span className="px-2 py-0.5 bg-blue-50 text-blue-600 text-xs rounded">{p.tool}</span>
                </div>
              </div>
              <button
                onClick={(e) => handleDelete(e, p.id)}
                className="text-gray-400 hover:text-red-500 text-sm"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
        {filtered.length === 0 && (
          <p className="text-gray-500 text-center py-8">No prompts found.</p>
        )}
      </div>
    </div>
  )
}
