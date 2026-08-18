import { useState } from 'react'
import type { Study } from '../types'
import { StudyList } from './StudyList'
import { SpeciesList } from './SpeciesList'

interface SidebarProps {
  studies: Study[]
  loading: boolean
  selectedStudyId: number | null
  onSelectStudy: (studyId: number | null) => void
  selectedSpeciesName: string | null
  onSelectSpecies: (name: string | null) => void
}

type Tab = 'species' | 'studies'

export function Sidebar({
  studies,
  loading,
  selectedStudyId,
  onSelectStudy,
  selectedSpeciesName,
  onSelectSpecies,
}: SidebarProps) {
  const [tab, setTab] = useState<Tab>('species')
  const [search, setSearch] = useState('')

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
      <div style={{ padding: '14px 16px 0', background: 'var(--color-surface-alt)' }}>
        <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--color-ink)' }}>Explore</div>
        <div
          style={{ fontSize: 12, color: 'var(--color-ink-faint)', marginTop: 2, marginBottom: 10 }}
        >
          {loading
            ? 'Loading…'
            : `${studies.length} ${studies.length === 1 ? 'study' : 'studies'} loaded`}
        </div>

        <input
          type="search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder={tab === 'species' ? 'Search species…' : 'Search studies…'}
          style={{
            width: '100%',
            padding: '7px 10px',
            marginBottom: 10,
            fontSize: 13,
            fontFamily: 'var(--font-sans)',
            color: 'var(--color-ink)',
            border: '1px solid var(--color-border)',
            borderRadius: 8,
            outline: 'none',
            background: 'var(--color-surface)',
          }}
        />

        <div style={{ display: 'flex', borderTop: '1px solid var(--color-border)' }}>
          <div style={tabButtonStyle(tab === 'species')} onClick={() => setTab('species')}>
            Species
          </div>
          <div style={tabButtonStyle(tab === 'studies')} onClick={() => setTab('studies')}>
            Studies
          </div>
        </div>
      </div>

      {tab === 'species' ? (
        <SpeciesList
          studies={studies}
          selectedSpeciesName={selectedSpeciesName}
          onSelectSpecies={onSelectSpecies}
          search={search}
        />
      ) : (
        <StudyList
          studies={studies}
          selectedStudyId={selectedStudyId}
          onSelect={onSelectStudy}
          search={search}
        />
      )}
    </div>
  )
}
