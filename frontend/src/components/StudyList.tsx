import { formatDate, type Study } from '../types'

interface StudyListProps {
  studies: Study[]
  selectedStudyId: number | null
  onSelect: (studyId: number | null) => void
  search: string
}

export function StudyList({ studies, selectedStudyId, onSelect, search }: StudyListProps) {
  const term = search.trim().toLowerCase()
  const filtered = studies.filter((study) => {
    if (!term) return true
    return (
      study.title.toLowerCase().includes(term) ||
      study.species.some((s) => s.toLowerCase().includes(term))
    )
  })

  if (filtered.length === 0) {
    return (
      <div style={{ padding: 16, fontSize: 13, color: 'var(--color-ink-faint)' }}>
        No studies match “{search}”.
      </div>
    )
  }

  return (
    <div style={{ overflowY: 'auto', flex: 1, minHeight: 0 }}>
      {filtered.map((study) => {
        const isSelected = study.id === selectedStudyId
        const activate = () => onSelect(isSelected ? null : study.id)
        return (
          <div
            key={study.id}
            className="po-row"
            role="button"
            tabIndex={0}
            aria-pressed={isSelected}
            onClick={activate}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault()
                activate()
              }
            }}
            style={{
              padding: '12px 16px',
              borderBottom: '1px solid var(--color-border)',
              background: isSelected ? 'var(--color-accent-soft)' : 'transparent',
              borderLeft: isSelected
                ? '3px solid var(--color-brand-light)'
                : '3px solid transparent',
            }}
          >
            <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--color-ink)' }}>
              {study.title}
            </div>
            <div
              style={{
                fontSize: 12,
                color: 'var(--color-ink-soft)',
                marginTop: 4,
                fontStyle: 'italic',
              }}
            >
              {study.species.join(', ') || 'Unknown species'}
            </div>
            <div style={{ fontSize: 12, color: 'var(--color-ink-faint)', marginTop: 2 }}>
              {study.record_count} records &middot; {formatDate(study.date_range.start)} –{' '}
              {formatDate(study.date_range.end)}
            </div>
          </div>
        )
      })}
    </div>
  )
}
