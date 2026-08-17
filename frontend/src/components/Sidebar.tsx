import { useEffect, useState } from 'react'
import { API_BASE_URL } from '../config'
import type { Study } from '../types'
import { StudyList } from './StudyList'
import { SpeciesList } from './SpeciesList'

interface SidebarProps {
  selectedStudyId: number | null
  onSelect: (studyId: number | null) => void
}

type Tab = 'studies' | 'species'

export function Sidebar({ selectedStudyId, onSelect }: SidebarProps) {
  const [studies, setStudies] = useState<Study[]>([])
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState<Tab>('studies')

  useEffect(() => {
    fetch(`${API_BASE_URL}/studies`)
      .then((r) => r.json())
      .then((data) => {
        setStudies(data)
        setLoading(false)
      })
  }, [])

  const tabButtonStyle = (active: boolean) => ({
    flex: 1,
    padding: '8px 0',
    textAlign: 'center' as const,
    fontSize: 13,
    fontWeight: 600,
    cursor: 'pointer',
    color: active ? 'var(--color-brand-light)' : 'var(--color-ink-faint)',
    borderBottom: active ? '2px solid var(--color-brand-light)' : '2px solid transparent',
  })

  return (
    <div
      style={{
        position: 'absolute',
        top: 16,
        left: 16,
        bottom: 96,
        width: 340,
        display: 'flex',
        flexDirection: 'column',
        background: 'var(--color-surface)',
        borderRadius: 10,
        boxShadow: '0 2px 12px rgba(15,36,54,0.25)',
        fontFamily: 'var(--font-sans)',
        overflow: 'hidden',
        zIndex: 1,
      }}
    >
      <div
        style={{
          padding: '14px 16px 0',
          background: 'var(--color-surface-alt)',
        }}
      >
        <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--color-ink)' }}>Explore</div>
        <div style={{ fontSize: 12, color: 'var(--color-ink-faint)', marginTop: 2, marginBottom: 10 }}>
          {loading ? 'Loading…' : `${studies.length} ${studies.length === 1 ? 'study' : 'studies'} loaded`}
        </div>
        <div style={{ display: 'flex', borderTop: '1px solid var(--color-border)' }}>
          <div style={tabButtonStyle(tab === 'studies')} onClick={() => setTab('studies')}>
            Studies
          </div>
          <div style={tabButtonStyle(tab === 'species')} onClick={() => setTab('species')}>
            Species
          </div>
        </div>
      </div>

      {tab === 'studies' ? (
        <StudyList studies={studies} selectedStudyId={selectedStudyId} onSelect={onSelect} />
      ) : (
        <SpeciesList
          studies={studies}
          onSelectStudy={(studyId) => {
            onSelect(studyId)
            setTab('studies')
          }}
        />
      )}
    </div>
  )
}
