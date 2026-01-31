import React, { useEffect, useState } from 'react'
import { getHints } from '../api'
import type { Hint } from '../types'

interface Props {
  content: string
}

export default function HintsPanel({ content }: Props) {
  const [hints, setHints] = useState<Hint[]>([])
  const [collapsed, setCollapsed] = useState(false)

  useEffect(() => {
    getHints().then(setHints).catch(() => {})
  }, [])

  if (hints.length === 0) return null

  const checkedHints = hints.map((h) => {
    try {
      const re = new RegExp(h.pattern)
      return { ...h, checked: re.test(content) }
    } catch {
      return { ...h, checked: false }
    }
  })

  const checkedCount = checkedHints.filter((h) => h.checked).length

  return (
    <div className="border border-gray-200 rounded-lg bg-white">
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="w-full px-4 py-2 flex justify-between items-center text-sm font-medium text-gray-700 hover:bg-gray-50"
      >
        <span>Best Practices ({checkedCount}/{hints.length})</span>
        <span>{collapsed ? '+' : '-'}</span>
      </button>
      {!collapsed && (
        <div className="px-4 pb-3 space-y-1">
          {checkedHints.map((h) => (
            <label key={h.id} className="flex items-start gap-2 text-sm" title={h.description}>
              <input type="checkbox" checked={h.checked} readOnly className="mt-0.5" />
              <span className={h.checked ? 'text-green-700' : 'text-gray-500'}>{h.label}</span>
            </label>
          ))}
        </div>
      )}
    </div>
  )
}
