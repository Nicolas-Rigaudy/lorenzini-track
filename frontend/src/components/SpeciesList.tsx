import { useEffect, useState } from 'react'
import type { Study } from '../types'
import {
  fetchSpeciesSummary,
  groupStudiesBySpecies,
  speciesStats,
  statusColor,
  type SpeciesSummary,
} from '../species'

interface SpeciesListProps {
  studies: Study[]
  selectedSpeciesName: string | null
  onSelectSpecies: (name: string | null) => void
  search: string
}

export function SpeciesList({
  studies,
  selectedSpeciesName,
  onSelectSpecies,
  search,
}: SpeciesListProps) {
  const speciesMap = groupStudiesBySpecies(studies)
  const speciesNames = Array.from(speciesMap.keys())

  const [summaries, setSummaries] = useState<Record<string, SpeciesSummary | null>>({})

  useEffect(() => {
    let cancelled = false
    Promise.all(
      speciesNames.map(async (name) => {
        const summary = await fetchSpeciesSummary(name)
        return [name, summary] as const
      }),
    ).then((entries) => {
      if (!cancelled) setSummaries(Object.fromEntries(entries))
    })
    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [studies])

  const term = search.trim().toLowerCase()
  const filtered = speciesNames.filter((name) => {
    if (!term) return true
    const summary = summaries[name]
    return (
      name.toLowerCase().includes(term) ||
      (summary?.title?.toLowerCase().includes(term) ?? false)
    )
  })

  if (filtered.length === 0) {
    return (
      <div style={{ padding: 16, fontSize: 13, color: 'var(--color-ink-faint)' }}>
        No species match “{search}”.
      </div>
    )
  }

  return (
    <div style={{ overflowY: 'auto', flex: 1, minHeight: 0 }}>
      {filtered.map((name) => {
        const isSelected = name === selectedSpeciesName
        const stats = speciesStats(speciesMap.get(name)!)
        const summary = summaries[name]

        return (
          <div
            key={name}
            onClick={() => onSelectSpecies(isSelected ? null : name)}
            style={{
              display: 'flex',
              gap: 12,
              alignItems: 'center',
              padding: '10px 16px',
              borderBottom: '1px solid var(--color-border)',
              cursor: 'pointer',
              background: isSelected ? 'var(--color-accent-soft)' : 'transparent',
              borderLeft: isSelected
                ? '3px solid var(--color-brand-light)'
                : '3px solid transparent',
            }}
          >
            <div
              style={{
                width: 48,
                height: 48,
                borderRadius: 8,
                flexShrink: 0,
                background: summary?.thumbnailUrl
                  ? `center / cover no-repeat url(${summary.thumbnailUrl})`
                  : 'var(--color-surface-alt)',
              }}
            />
            <div style={{ minWidth: 0, flex: 1 }}>
              <div
                style={{
                  fontSize: 14,
                  fontWeight: 600,
                  color: 'var(--color-ink)',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}
              >
                {summary?.title ?? name}
              </div>
              <div
                style={{
                  fontSize: 12,
                  fontStyle: 'italic',
                  color: 'var(--color-ink-faint)',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}
              >
                {name}
              </div>
              <div style={{ display: 'flex', gap: 6, alignItems: 'center', marginTop: 4 }}>
                {summary?.conservationStatus && (
                  <span
                    style={{
                      padding: '1px 6px',
                      borderRadius: 8,
                      background: statusColor(summary.conservationStatus),
                      color: '#fff',
                      fontSize: 10,
                      fontWeight: 700,
                      textTransform: 'uppercase',
                      letterSpacing: 0.3,
                    }}
                  >
                    {summary.conservationStatus}
                  </span>
                )}
                <span style={{ fontSize: 12, color: 'var(--color-ink-faint)' }}>
                  {stats.studyCount} {stats.studyCount === 1 ? 'study' : 'studies'} &middot;{' '}
                  {stats.recordCount} records
                </span>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
