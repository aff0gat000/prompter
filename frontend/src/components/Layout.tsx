import React from 'react'

interface Props {
  children: React.ReactNode
  onGuide?: () => void
}

export default function Layout({ children, onGuide }: Props) {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Prompter</h1>
          <p className="text-sm text-gray-500">Prompt engineering toolkit</p>
        </div>
        {onGuide && (
          <button
            onClick={onGuide}
            className="px-3 py-1.5 text-sm text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Guide
          </button>
        )}
      </header>
      <main className="max-w-6xl mx-auto p-6">{children}</main>
    </div>
  )
}
