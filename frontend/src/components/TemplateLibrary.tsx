import React, { useEffect, useState } from 'react'
import { listTemplates, cloneTemplate } from '../api'
import type { PromptListItem } from '../types'

interface Props {
  onBack: () => void
  onCloned: (id: string) => void
}

export default function TemplateLibrary({ onBack, onCloned }: Props) {
  const [templates, setTemplates] = useState<PromptListItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listTemplates()
      .then(setTemplates)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const categories = Array.from(new Set(templates.map((t) => t.category || 'other')))

  const handleUse = async (t: PromptListItem) => {
    try {
      const prompt = await cloneTemplate(t.id)
      onCloned(prompt.id)
    } catch (e) {
      alert(`Failed to clone template: ${(e as Error).message}`)
    }
  }

  if (loading) return <p className="text-gray-500 text-center py-8">Loading templates...</p>

  return (
    <div>
      <button onClick={onBack} className="text-blue-600 text-sm mb-4 hover:underline">
        &larr; Back to list
      </button>
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Starter Templates</h2>
      {categories.map((cat) => (
        <div key={cat} className="mb-6">
          <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">{cat}</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {templates
              .filter((t) => (t.category || 'other') === cat)
              .map((t) => (
                <div key={t.id} className="bg-white border border-gray-200 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900">{t.name}</h4>
                  <p className="text-sm text-gray-500 mt-1">{t.description}</p>
                  <div className="flex gap-1 mt-2 flex-wrap">
                    {t.tags.map((tag) => (
                      <span key={tag} className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded">
                        {tag}
                      </span>
                    ))}
                  </div>
                  <button
                    onClick={() => handleUse(t)}
                    className="mt-3 px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                  >
                    Use Template
                  </button>
                </div>
              ))}
          </div>
        </div>
      ))}
      {templates.length === 0 && (
        <p className="text-gray-500 text-center py-8">No templates available.</p>
      )}
    </div>
  )
}
