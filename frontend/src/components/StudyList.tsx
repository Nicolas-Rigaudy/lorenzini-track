import { formatDate, type Study } from '../types'

interface StudyListProps {
  studies: Study[]
  selectedStudyId: number | null
  onSelect: (studyId: number | null) => void
}

export function StudyList({ studies, selectedStudyId, onSelect }: StudyListProps) {
  return (
    <div style={{ overflowY: 'auto', flex: 1, minHeight: 0 }}>
      {studies.map((study) => {
        const isSelected = study.id === selectedStudyId
        return (
          <div
            key={study.id}
            onClick={() => onSelect(isSelected ? null : study.id)}
            style={{
              padding: '12px 16px',
              borderBottom: '1px solid var(--color-border)',
              cursor: 'pointer',
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

            {isSelected && (
              <div
                style={{
                  marginTop: 10,
                  paddingTop: 10,
                  borderTop: '1px solid var(--color-border)',
                  fontSize: 13,
                  color: 'var(--color-ink)',
                }}
              >
                {study.abstract && (
                  <>
                    <div
                      style={{
                        fontWeight: 700,
                        fontSize: 11,
                        textTransform: 'uppercase',
                        letterSpacing: 0.4,
                        color: 'var(--color-brand-light)',
                      }}
                    >
                      Purpose
                    </div>
                    <p style={{ margin: '4px 0 12px', color: 'var(--color-ink-soft)', lineHeight: 1.5 }}>
                      {study.abstract}
                    </p>
                  </>
                )}

                <div
                  style={{
                    fontWeight: 700,
                    fontSize: 11,
                    textTransform: 'uppercase',
                    letterSpacing: 0.4,
                    color: 'var(--color-brand-light)',
                  }}
                >
                  Details
                </div>
                <ul style={{ margin: '4px 0 0', padding: '0 0 0 18px', lineHeight: 1.7 }}>
                  <li>
                    <strong>Species tracked:</strong> {study.species.join(', ') || 'Unknown'}
                  </li>
                  <li>
                    <strong>Time period:</strong> {formatDate(study.date_range.start)} –{' '}
                    {formatDate(study.date_range.end)}
                  </li>
                  <li>
                    <strong>Records:</strong> {study.record_count}
                  </li>
                  {study.rights_holder && (
                    <li>
                      <strong>Conducted by:</strong> {study.rights_holder}
                    </li>
                  )}
                  {study.data_provider && (
                    <li>
                      <strong>Tagging/data provider:</strong> {study.data_provider}
                    </li>
                  )}
                  {study.published_date && (
                    <li>
                      <strong>Published:</strong> {formatDate(study.published_date)}
                    </li>
                  )}
                  <li>
                    <strong>Licence:</strong> {study.license ?? 'Not specified'}
                  </li>
                </ul>

                {study.source_url && (
                  <a
                    href={study.source_url}
                    target="_blank"
                    rel="noreferrer"
                    style={{
                      display: 'inline-block',
                      marginTop: 12,
                      fontSize: 13,
                      fontWeight: 600,
                      color: 'var(--color-brand-light)',
                    }}
                  >
                    View source dataset →
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
