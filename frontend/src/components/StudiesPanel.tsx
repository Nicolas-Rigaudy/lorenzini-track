import { useState } from 'react'
import type { Study } from '../types'
import { StudyList } from './StudyList'
import { Icon } from './Icon'

interface StudiesPanelProps {
  studies: Study[]
  loading: boolean
  selectedStudyId: number | null
  onSelectStudy: (studyId: number | null) => void
}

export function StudiesPanel({ studies, loading, selectedStudyId, onSelectStudy }: StudiesPanelProps) {
  const [search, setSearch] = useState('')

  return (
    <div
      style={{
        position: 'absolute',
        top: 16,
        left: 16,
        bottom: 16,
        width: 326,
        display: 'flex',
        flexDirection: 'column',
        background: 'var(--color-surface)',
        borderRadius: 12,
        boxShadow: '0 2px 14px rgba(15,36,54,0.28)',
        fontFamily: 'var(--font-sans)',
        overflow: 'hidden',
        zIndex: 1,
      }}
    >
      <div style={{ padding: '12px 14px', background: 'var(--color-surface-alt)', borderBottom: '1px solid var(--color-border)' }}>
        <div style={{ fontSize: 12, fontWeight: 800, letterSpacing: 0.6, textTransform: 'uppercase', color: 'var(--color-brand-light)' }}>
          {loading ? 'Studies' : `Studies · ${studies.length}`}
        </div>
        <div className="po-searchwrap" style={{ marginTop: 9 }}>
          <Icon name="search" size={15} />
          <input
            className="po-input"
            type="search"
            aria-label="Search studies"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search studies…"
          />
        </div>
      </div>
      <StudyList studies={studies} selectedStudyId={selectedStudyId} onSelect={onSelectStudy} search={search} />
    </div>
  )
}
