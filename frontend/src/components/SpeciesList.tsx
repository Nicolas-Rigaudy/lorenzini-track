import { formatDate, type Study } from '../types'

interface SpeciesListProps {
  studies: Study[]
  selectedSpeciesName: string | null
  onSelectSpecies: (name: string | null) => void
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

export function SpeciesList({
  studies,
  selectedSpeciesName,
  onSelectSpecies,
  onSelectStudy,
}: SpeciesListProps) {
  const speciesMap = groupBySpecies(studies)
  const speciesNames = Array.from(speciesMap.keys())

  return (
    <div style={{ overflowY: 'auto', flex: 1, minHeight: 0 }}>
      {speciesNames.map((name) => {
        const isSelected = name === selectedSpeciesName
        const studiesForSpecies = speciesMap.get(name)!

        return (
          <div
            key={name}
            onClick={() => onSelectSpecies(isSelected ? null : name)}
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
            <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--color-ink)' }}>{name}</div>
            <div style={{ fontSize: 12, color: 'var(--color-ink-faint)', marginTop: 2 }}>
              {studiesForSpecies.length} {studiesForSpecies.length === 1 ? 'study' : 'studies'}
              {isSelected ? ' — see details on the right' : ''}
            </div>

            {isSelected && (
              <ul style={{ margin: '10px 0 0', padding: 0, listStyle: 'none' }}>
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
                    <div style={{ fontWeight: 600, fontSize: 13 }}>{study.title}</div>
                    <div style={{ fontSize: 12, color: 'var(--color-ink-faint)' }}>
                      {study.record_count} records &middot; {formatDate(study.date_range.start)} –{' '}
                      {formatDate(study.date_range.end)}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )
      })}
    </div>
  )
}
