import { useEffect, useState } from 'react'
import { fetchSpeciesSummary, statusColor, type SpeciesSummary } from '../species'
import type { SpeciesListItem } from '../speciesApi'
import { speciesPhoto } from '../speciesMedia'

interface SpeciesGalleryProps {
  species: SpeciesListItem[]
  speciesColors: Record<string, string>
  search: string
  onSelect: (scientificName: string) => void
}

export function SpeciesGallery({ species, speciesColors, search, onSelect }: SpeciesGalleryProps) {
  const [summaries, setSummaries] = useState<Record<string, SpeciesSummary | null>>({})

  useEffect(() => {
    let cancelled = false
    Promise.all(
      species.map(async (s) => [s.scientific_name, await fetchSpeciesSummary(s.scientific_name)] as const),
    ).then((entries) => {
      if (!cancelled) setSummaries(Object.fromEntries(entries))
    })
    return () => {
      cancelled = true
    }
  }, [species])

  const term = search.trim().toLowerCase()
  const filtered = species.filter((s) => {
    if (!term) return true
    const summary = summaries[s.scientific_name]
    return (
      s.scientific_name.toLowerCase().includes(term) ||
      (s.common_name?.toLowerCase().includes(term) ?? false) ||
      (summary?.title?.toLowerCase().includes(term) ?? false)
    )
  })

  if (species.length === 0) {
    return (
      <div style={{ overflowY: 'auto', flex: 1, minHeight: 0, padding: 14 }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="po-skel" style={{ height: 148, borderRadius: 12 }} />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div style={{ overflowY: 'auto', flex: 1, minHeight: 0, padding: 14 }}>
      <div style={{ fontSize: 12, color: 'var(--color-ink-faint)', margin: '0 2px 10px' }}>
        {filtered.length === species.length
          ? 'Tap a species to open its profile.'
          : `${filtered.length} of ${species.length} species`}
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
        {filtered.map((s) => {
          const summary = summaries[s.scientific_name]
          return (
            <div
              key={s.scientific_name}
              className="po-card"
              role="button"
              tabIndex={0}
              aria-label={`Open profile for ${s.common_name ?? summary?.title ?? s.scientific_name}`}
              onClick={() => onSelect(s.scientific_name)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault()
                  onSelect(s.scientific_name)
                }
              }}
              style={{
                border: '1px solid var(--color-border)',
                borderTop: `3px solid ${speciesColors[s.scientific_name] ?? 'var(--color-border)'}`,
                borderRadius: 12,
                overflow: 'hidden',
                background: 'var(--color-surface)',
              }}
            >
              <div
                role="img"
                aria-label={`Photograph of ${s.common_name ?? s.scientific_name}`}
                style={{
                  height: 82,
                  position: 'relative',
                  background: speciesPhoto(s.scientific_name, summary?.thumbnailUrl)
                    ? `center / cover no-repeat url(${speciesPhoto(s.scientific_name, summary?.thumbnailUrl)})`
                    : 'linear-gradient(135deg, #2f6d8c, #123a52)',
                }}
              >
                {summary?.conservationStatus && (
                  <span
                    title={`IUCN: ${summary.conservationStatus}`}
                    style={{
                      position: 'absolute',
                      top: 6,
                      right: 6,
                      width: 12,
                      height: 12,
                      borderRadius: '50%',
                      background: statusColor(summary.conservationStatus),
                      border: '2px solid #fff',
                      boxShadow: '0 0 3px rgba(0,0,0,.4)',
                    }}
                  />
                )}
              </div>
              <div style={{ padding: '8px 9px' }}>
                <div style={{ fontSize: 12.5, fontWeight: 700, lineHeight: 1.15, color: 'var(--color-ink)' }}>
                  {s.common_name ?? summary?.title ?? s.scientific_name}
                </div>
                <div style={{ fontSize: 10.5, fontStyle: 'italic', color: 'var(--color-ink-faint)', marginTop: 1 }}>
                  {s.scientific_name}
                </div>
                <div style={{ fontSize: 10.5, color: 'var(--color-ink-faint)', marginTop: 5 }}>
                  {s.study_count} {s.study_count === 1 ? 'study' : 'studies'} · {s.record_count} records
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
