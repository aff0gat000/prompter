import { useState } from 'react'
import Layout from './components/Layout'
import PromptList from './components/PromptList'
import PromptEditor from './components/PromptEditor'

export default function App() {
  const [view, setView] = useState<'list' | 'edit'>('list')
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [refreshKey, setRefreshKey] = useState(0)

  const handleSelect = (id: string) => {
    setSelectedId(id)
    setView('edit')
  }

  const handleCreate = () => {
    setSelectedId(null)
    setView('edit')
  }

  const handleBack = () => {
    setView('list')
    setSelectedId(null)
  }

  return (
    <Layout>
      {view === 'list' ? (
        <PromptList onSelect={handleSelect} onCreate={handleCreate} refreshKey={refreshKey} />
      ) : (
        <PromptEditor
          promptId={selectedId}
          onBack={handleBack}
          onSaved={() => setRefreshKey((k) => k + 1)}
        />
      )}
    </Layout>
  )
}
