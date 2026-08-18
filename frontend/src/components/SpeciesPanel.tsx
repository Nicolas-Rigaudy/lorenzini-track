import { useState } from 'react'
import type { Study } from '../types'
import type { SpeciesListItem } from '../speciesApi'
import { SpeciesGallery } from './SpeciesGallery'
import { SpeciesProfile } from './SpeciesProfile'

interface SpeciesPanelProps {
  speciesList: SpeciesListItem[]
  selectedSpeciesName: string | null
  onSelectSpecies: (name: string | null) => void
  studies: Study[]
  selectedStudyId: number | null
  onSelectStudy: (studyId: number | null) => void
}

export function SpeciesPanel({
  speciesList,
  selectedSpeciesName,
  onSelectSpecies,
  studies,
  selectedStudyId,
  onSelectStudy,
}: SpeciesPanelProps) {
  const [search, setSearch] = useState('')

  return (
    <div
      style={{
        position: 'absolute',
        top: 16,
        right: 16,
        bottom: 16,
        width: 372,
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
      {selectedSpeciesName ? (
        <SpeciesProfile
          scientificName={selectedSpeciesName}
          studies={studies}
          selectedStudyId={selectedStudyId}
          onSelectStudy={onSelectStudy}
          onBack={() => onSelectSpecies(null)}
        />
      ) : (
        <>
          <div style={{ padding: '12px 14px', background: 'var(--color-surface-alt)', borderBottom: '1px solid var(--color-border)' }}>
            <div style={{ fontSize: 12, fontWeight: 800, letterSpacing: 0.6, textTransform: 'uppercase', color: 'var(--color-brand-light)' }}>
              Species · {speciesList.length}
            </div>
            <input
              type="search"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search species…"
              style={{
                width: '100%',
                padding: '7px 10px',
                marginTop: 9,
                fontSize: 13,
                fontFamily: 'var(--font-sans)',
                color: 'var(--color-ink)',
                border: '1px solid var(--color-border)',
                borderRadius: 9,
                outline: 'none',
              }}
            />
          </div>
          <SpeciesGallery species={speciesList} search={search} onSelect={onSelectSpecies} />
        </>
      )}
    </div>
  )
}
