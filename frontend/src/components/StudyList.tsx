import { formatDate, type Study } from '../types'
import { Icon } from './Icon'

interface StudyListProps {
  studies: Study[]
  selectedStudyId: number | null
  onSelect: (studyId: number | null) => void
  onSelectSpecies: (name: string) => void
  search: string
}

const sectionLabel = {
  fontWeight: 800,
  fontSize: 10.5,
  textTransform: 'uppercase' as const,
  letterSpacing: 0.4,
  color: 'var(--color-brand-light)',
}

export function StudyList({ studies, selectedStudyId, onSelect, onSelectSpecies, search }: StudyListProps) {
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
        const isMulti = study.species.length > 1
        const activate = () => onSelect(isSelected ? null : study.id)
        return (
          <div key={study.id} style={{ borderBottom: '1px solid var(--color-border)' }}>
            <div
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
                background: isSelected ? 'var(--color-accent-soft)' : 'transparent',
                borderLeft: isSelected
                  ? '3px solid var(--color-brand-light)'
                  : '3px solid transparent',
              }}
            >
              <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--color-ink)' }}>
                {study.title}
              </div>
              <div style={{ fontSize: 12, color: 'var(--color-ink-soft)', marginTop: 4, fontStyle: 'italic' }}>
                {study.species.length} {study.species.length === 1 ? 'species' : 'species'} ·{' '}
                {study.record_count.toLocaleString()} records
              </div>
              <div style={{ fontSize: 12, color: 'var(--color-ink-faint)', marginTop: 2 }}>
                {formatDate(study.date_range.start)} – {formatDate(study.date_range.end)}
              </div>
            </div>

            {isSelected && isMulti && (
              <div style={{ padding: '4px 16px 14px' }}>
                {study.abstract && (
                  <p style={{ margin: '4px 0 12px', fontSize: 13, color: 'var(--color-ink-soft)', lineHeight: 1.5 }}>
                    {study.abstract}
                  </p>
                )}

                <div style={sectionLabel}>Species in this study</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 8, marginBottom: 12 }}>
                  {study.species.map((name) => (
                    <button
                      key={name}
                      onClick={(e) => {
                        e.stopPropagation()
                        onSelectSpecies(name)
                      }}
                      className="po-card"
                      style={{
                        fontFamily: 'var(--font-sans)',
                        fontSize: 12,
                        fontStyle: 'italic',
                        color: 'var(--color-brand)',
                        background: 'var(--color-surface-alt)',
                        border: '1px solid var(--color-border)',
                        borderRadius: 999,
                        padding: '3px 10px',
                      }}
                    >
                      {name}
                    </button>
                  ))}
                </div>

                <ul style={{ margin: 0, padding: '0 0 0 16px', lineHeight: 1.7, fontSize: 12.5, color: 'var(--color-ink)' }}>
                  {study.rights_holder && (
                    <li><strong>Conducted by:</strong> {study.rights_holder}</li>
                  )}
                  {study.data_provider && (
                    <li><strong>Data provider:</strong> {study.data_provider}</li>
                  )}
                  {study.published_date && (
                    <li><strong>Published:</strong> {formatDate(study.published_date)}</li>
                  )}
                  <li><strong>Licence:</strong> {study.license ?? 'Not specified'}</li>
                </ul>

                {study.source_url && (
                  <a
                    href={study.source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="po-link"
                    style={{ display: 'inline-flex', alignItems: 'center', gap: 4, marginTop: 10, fontSize: 12.5 }}
                  >
                    View source dataset
                    <Icon name="external" size={13} />
                  </a>
                )}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
