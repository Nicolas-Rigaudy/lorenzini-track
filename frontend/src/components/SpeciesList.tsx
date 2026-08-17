import { useEffect, useState } from 'react'
import { fetchSpeciesSummary, statusColor, type SpeciesSummary } from '../species'
import { formatDate, type Study } from '../types'

interface SpeciesListProps {
  studies: Study[]
  onSelectStudy: (studyId: number) => void
}

function groupBySpecies(studies: Study[]): Map<string, Study[]> {
  const map = new Map<string, Study[]>()
  for (const study of studies) {
    for (const name of study.species.length ? study.species : ['Unknown species']) {
      if (!map.has(name)) map.set(name, [])
      map.get(name)!.push(study)
    }
  }
  return map
}

export function SpeciesList({ studies, onSelectStudy }: SpeciesListProps) {
  const speciesMap = groupBySpecies(studies)
  const speciesNames = Array.from(speciesMap.keys())

  const [summaries, setSummaries] = useState<Record<string, SpeciesSummary | null>>({})
  const [expanded, setExpanded] = useState<string | null>(null)

  useEffect(() => {
    speciesNames.forEach((name) => {
      if (name in summaries) return
      fetchSpeciesSummary(name).then((summary) => {
        setSummaries((prev) => ({ ...prev, [name]: summary }))
      })
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [studies])

  return (
    <div style={{ overflowY: 'auto', flex: 1, minHeight: 0 }}>
      {speciesNames.map((name) => {
        const isExpanded = name === expanded
        const summary = summaries[name]
        const studiesForSpecies = speciesMap.get(name)!

        return (
          <div
            key={name}
            onClick={() => setExpanded(isExpanded ? null : name)}
            style={{
              padding: '12px 16px',
              borderBottom: '1px solid var(--color-border)',
              cursor: 'pointer',
              background: isExpanded ? 'var(--color-accent-soft)' : 'transparent',
              borderLeft: isExpanded
                ? '3px solid var(--color-brand-light)'
                : '3px solid transparent',
              display: 'flex',
              gap: 10,
              alignItems: 'flex-start',
            }}
          >
            {summary?.thumbnailUrl ? (
              <img
                src={summary.thumbnailUrl}
                alt={name}
                style={{ width: 40, height: 40, borderRadius: 6, objectFit: 'cover', flexShrink: 0 }}
              />
            ) : (
              <div
                style={{
                  width: 40,
                  height: 40,
                  borderRadius: 6,
                  background: 'var(--color-surface-alt)',
                  flexShrink: 0,
                }}
              />
            )}

            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--color-ink)' }}>
                {summary?.title ?? name}
              </div>
              <div style={{ fontSize: 12, fontStyle: 'italic', color: 'var(--color-ink-faint)' }}>
                {name}
              </div>
              <div style={{ fontSize: 12, color: 'var(--color-ink-faint)', marginTop: 2 }}>
                {studiesForSpecies.length} {studiesForSpecies.length === 1 ? 'study' : 'studies'}
              </div>

              {isExpanded && (
                <div
                  style={{
                    marginTop: 10,
                    paddingTop: 10,
                    borderTop: '1px solid var(--color-border)',
                    fontSize: 13,
                    color: 'var(--color-ink)',
                  }}
                >
                  {summary?.conservationStatus && (
                    <div
                      style={{
                        display: 'inline-block',
                        marginBottom: 8,
                        padding: '3px 10px',
                        borderRadius: 12,
                        background: statusColor(summary.conservationStatus),
                        color: '#fff',
                        fontSize: 11,
                        fontWeight: 700,
                        textTransform: 'uppercase',
                        letterSpacing: 0.3,
                      }}
                    >
                      IUCN: {summary.conservationStatus}
                    </div>
                  )}
                  {summary?.extract && (
                    <p style={{ margin: '0 0 10px', color: 'var(--color-ink-soft)', lineHeight: 1.5 }}>
                      {summary.extract}
                    </p>
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
                    Studies for this species
                  </div>
                  <ul style={{ margin: '6px 0 0', padding: 0, listStyle: 'none' }}>
                    {studiesForSpecies.map((study) => (
                      <li
                        key={study.id}
                        onClick={(e) => {
                          e.stopPropagation()
                          onSelectStudy(study.id)
                        }}
                        style={{
                          padding: '6px 8px',
                          marginBottom: 4,
                          background: 'var(--color-surface-alt)',
                          borderRadius: 6,
                          cursor: 'pointer',
                        }}
                      >
                        <div style={{ fontWeight: 600 }}>{study.title}</div>
                        <div style={{ fontSize: 12, color: 'var(--color-ink-faint)' }}>
                          {study.record_count} records &middot; {formatDate(study.date_range.start)} –{' '}
                          {formatDate(study.date_range.end)}
                        </div>
                      </li>
                    ))}
                  </ul>

                  {summary?.pageUrl && (
                    <a
                      href={summary.pageUrl}
                      target="_blank"
                      rel="noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      style={{
                        display: 'inline-block',
                        marginTop: 10,
                        fontSize: 12,
                        fontWeight: 600,
                        color: 'var(--color-brand-light)',
                      }}
                    >
                      Read more on Wikipedia →
                    </a>
                  )}
                </div>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}
